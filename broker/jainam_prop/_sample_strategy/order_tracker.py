import pytz
import datetime as dt
from logzero import logger as logzero_logger, logfile, setup_logger
import traceback
import os

os.makedirs("logs", exist_ok=True)
logfile("logs/success.log", maxBytes=1e6, backupCount=3)
error_logger = setup_logger(name="error_logger", logfile="logs/error.log", level=40, disableStderrLogger=True)

class OrderTracker:
    def __init__(self, db, logger, account_manager, enter_leg_func, exit_leg_func):
        self.db = db
        self.logger = logger
        self.account_manager = account_manager

        self.enter_leg_func = enter_leg_func
        self.exit_leg_func = exit_leg_func
        logzero_logger.info("✅ OrderTracker Initialized")

    def check_leg_order(self, orderbook, leg, port, strategy):
        try:
            exchange = self.account_manager.get_exchange(port.scrip)[2]

            if port.trading_mode == "Paper":
                if leg.status == "exited" and leg.exit_order_status == "Execute":
                    filled_qty = leg.exit_filled_qty
                    exec_price = leg.exit_executed_price
                    self.reset_leg_for_exit(leg, port, filled_qty, exec_price)
                    logzero_logger.info(f"✅ Paper leg exit processed: Leg#{leg['name']} | Booked PnL: moved")
                return "continue"

            elif port.trading_mode == "Live":
                if leg.status == "no_position":
                    return "continue"

                elif leg.status == "entered":
                    if leg.entry_order_message not in ("sucess", "success", "successful"):
                        self.db.update_leg("status", "no_position", leg.id)

                    else:
                        if leg.entry_order_status == "Execute":
                            return "continue"

                        else:
                            logzero_logger.debug(f"{port=}")
                            order = self.get_order(exchange, orderbook, leg.entry_order_id)
                            logzero_logger.debug(f"{order=}")
                            self.db.update_leg("entry_order_status", order["OrderStatus"], leg.id)

                            if order["OrderStatus"] == "Filled":
                                ins = order["TradingSymbol"]
                                tt = order["OrderSide"]
                                qty = order["OrderQuantity"]
                                ot = order["OrderType"]
                                price = order["OrderPrice"]
                                self.db.add_order(ins, tt, qty, ot, price, port.id, strategy.account_id)
                                self.db.update_leg("status", "entered", leg.id)
                                filled_qty, exec_price = self.note_entry_order_info(leg, order)
                                self.logger.log(f"Entry Order #{leg.entry_order_id} of Leg #{leg.id} got executed, going to entered state; Filled Qty: {filled_qty}, Executed Price: {exec_price}", "EMERGENCY", port.id)

                            elif order["OrderStatus"] == "Rejected":
                                if int(leg.entry_filled_qty + order["LeavesQuantity"]) == 0:
                                    self.db.update_leg("status", "no_position", leg.id)
                                    self.db.update_leg("entry_order_message", "Rejected", leg.id)
                                    self.db.update_leg("entry_order_status", "Rejected", leg.id)
                                    self.logger.log(f"Entry Order #{leg.entry_order_id} of Leg #{leg.id} got rejected, filled qty at time of rejection was 0, reverting to no_position state", "EMERGENCY", port.id)

                                else:
                                    # Special Side case
                                    self.db.update_leg("status", "entered", leg.id)
                                    filled_qty, exec_price = self.note_entry_order_info(leg, order)
                                    self.logger.log(f"Entry Order #{leg.entry_order_id} of Leg #{leg.id} got rejected, filled qty at time of rejection was {order['LeavesQuantity']}, going to entered state; Filled Qty: {filled_qty}, Executed Price: {exec_price}", "EMERGENCY", port.id)

                            elif order["OrderStatus"] == "Cancelled":
                                self.logger.log(f"Entry Order #{leg.entry_order_id} of Leg #{leg.id} is cancelled, replacing order with qty: {int(order['OrderQuantity']) - int(order['LeavesQuantity'])}", "EMERGENCY", port.id)
                                self.replace_order(int(order['OrderQuantity']) - int(order["LeavesQuantity"]), leg, port, "entry")

                            elif order["OrderStatus"] == "PendingReplace":
                                if leg.entry_order_type == "LIMIT" and leg.num_modifications != 0 and leg.entry_num_modifications_done <= leg.num_modifications:
                                    cur_time = dt.datetime.now(tz=pytz.timezone("Asia/Kolkata")).replace(tzinfo=None)
                                    order_time = dt.datetime.strptime(order["ExchangeTransactTime"], "%d/%m/%Y%H:%M:%S")

                                    time_diff = cur_time - order_time
                                    max_time_diff = dt.timedelta(seconds=float(leg.modification_wait_time))

                                    if time_diff >= max_time_diff:
                                        res1 = self.account_manager.cancel_order(leg.entry_order_id, strategy)
                                        self.logger.log(f"Time elapsed: {time_diff.seconds} > Max allowed time diff.: {max_time_diff.seconds}, retrying, entry order cancellation message: {str(res1)}", "ERROR", port.id)

                                        filled_qty, exec_price = self.note_entry_order_info(leg, order, set_status_to_execute=False)
                                        self.logger.log(f"Cancelling Entry Order #{leg.entry_order_id} of Leg #{leg.id}; New Filled Qty: {filled_qty}, New Executed Price: {exec_price}", "INFO", port.id)

                elif leg.status == "exited":
                    if leg.exit_order_message not in ("sucess", "success", "successful"):
                        self.db.update_leg("status", "entered", leg.id)

                    else:
                        if leg.exit_order_status == "Execute":
                            return "continue"

                        else:
                            order = self.get_order(exchange, orderbook, leg.exit_order_id)
                            self.db.update_leg("exit_order_status", order["OrderStatus"], leg.id)

                            if order["OrderStatus"] == "Filled":
                                # self.db.update_leg("status", "no_position", leg.id)
                                filled_qty, exec_price = self.note_exit_order_info(leg, order)
                                self.reset_leg_for_exit(leg, port, filled_qty, exec_price)
                                self.logger.log(f"Exit Order #{leg.exit_order_id} of Leg #{leg.id} got executed, going to no_position state; Filled Qty: {filled_qty}, Executed Price: {exec_price}", "EMERGENCY", port.id)

                            elif order["OrderStatus"] == "Rejected":
                                if int(leg.exit_filled_qty + order["LeavesQuantity"]) == 0:
                                    self.db.update_leg("status", "entered", leg.id)
                                    self.logger.log(f"Exit Order #{leg.exit_order_id} of Leg #{leg.id} got rejected, filled qty at time of rejection was 0, reverting to entered state", "EMERGENCY", port.id)

                                # Don't know what to do here yet
                                else:
                                    # Special Side Case
                                    self.db.update_leg("status", "no_position", leg.id)
                                    filled_qty, exec_price = self.note_exit_order_info(leg, order)
                                    self.logger.log(f"Exit Order #{leg.exit_order_id} of Leg #{leg.id} got rejected, filled qty at time of rejection was {order['LeavesQuantity']}, going to no_position state; Filled Qty: {filled_qty}, Executed Price: {exec_price}", "EMERGENCY", port.id)

                            elif order["OrderStatus"] == "Cancelled":
                                self.logger.log(f"Exit Order #{leg.exit_order_id} of Leg #{leg.id} is cancelled, replacing order with qty: {int(order['OrderQuantity']) - int(order['LeavesQuantity'])}", "EMERGENCY", port.id)
                                self.replace_order(int(order['OrderQuantity']) - int(order["LeavesQuantity"]), leg, port, "exit")

                            elif order["OrderStatus"] == "PendingReplace":
                                if leg.exit_order_type == "LIMIT" and leg.num_modifications != 0 and leg.exit_num_modifications_done <= leg.num_modifications:
                                    cur_time = dt.datetime.now(tz=pytz.timezone("Asia/Kolkata")).replace(tzinfo=None)
                                    order_time = dt.datetime.strptime(order["ExchangeTransactTime"], "%d/%m/%Y%H:%M:%S")

                                    time_diff = cur_time - order_time
                                    max_time_diff = dt.timedelta(seconds=float(leg.modification_wait_time))

                                    if time_diff >= max_time_diff:
                                        res3 = self.account_manager.cancel_order(leg.exit_order_id, strategy)
                                        self.logger.log(f"Time elapsed: {time_diff.seconds} > Max allowed time diff.: {max_time_diff.seconds}, retrying, entry order cancellation message: {str(res3)}", "ERROR", port.id)

                                        filled_qty, exec_price = self.note_exit_order_info(leg, order, set_status_to_execute=False)
                                        self.logger.log(f"Cancelling Exit Order #{leg.exit_order_id} of Leg #{leg.id}; New Filled Qty: {filled_qty}, New Executed Price: {exec_price}", "INFO", port.id)
        except Exception as e:
            logzero_logger.error(f"🚨 check_leg_order() error: {e}\n{traceback.format_exc()}")
            error_logger.error(f"🚨 check_leg_order() error: {e}\n{traceback.format_exc()}")
            logzero_logger.error(f"{port=}")
            raise

    def get_order(self, exchange, orderbook, order_id):
        try:
            order = {}

            for _order in orderbook['result']:
                if _order["ExchangeSegment"] == exchange and str(_order["AppOrderID"]) == str(order_id):
                    order = _order
                    break
            logzero_logger.info(f"✅ get_order completed successfully for order_id: {order_id}")
            return order
        except Exception as e:
            logzero_logger.error(f"🚨 get_order() error: {e}\n{traceback.format_exc()}")
            error_logger.error(f"🚨 get_order() error: {e}\n{traceback.format_exc()}")
            raise

    def replace_order(self, qty, leg, port, action_type):
        try:
            if action_type == "entry":
                if leg.entry_num_modifications_done == leg.num_modifications:
                    self.enter_leg_func(leg, port, 1, order_type="LIMIT", qty=qty, modification=True, final_modification=True)  # For final to be at Default Limit %
                    self.logger.log(f"No. of modifications already done: {leg.entry_num_modifications_done} exceeds Max allowed No. of modifications: {leg.num_modifications}, setting entry at default limit %", "INFO", port.id)

                else:
                    self.enter_leg_func(leg, port, 1, order_type="LIMIT", qty=qty, modification=True)

            elif action_type == "exit":
                if leg.exit_num_modifications_done == leg.num_modifications:
                    self.exit_leg_func(leg, port, order_type="LIMIT", modification=True, final_modification=True)  # For final to be at Default Limit %
                    self.logger.log(f"No. of modifications already done: {leg.exit_num_modifications_done} exceeds Max allowed No. of modifications: {leg.num_modifications}, setting exit at default limit %", "INFO", port.id)

                else:
                    self.exit_leg_func(leg, port, order_type="LIMIT", modification=True)
            logzero_logger.info(f"✅ replace_order completed for action_type: {action_type}, leg_id: {leg.id}")
        except Exception as e:
            logzero_logger.error(f"🚨 replace_order() error: {e}\n{traceback.format_exc()}")
            error_logger.error(f"🚨 replace_order() error: {e}\n{traceback.format_exc()}")
            raise

    def reset_leg_for_exit(self, leg, port, filled_qty, exec_price):
        try:
            if leg.trade_type == "BUY":
                _pnl = exec_price - leg.entry_executed_price
            elif leg.trade_type == "SELL":
                _pnl = leg.entry_executed_price - exec_price

            pnl = round(_pnl * filled_qty * self.account_manager.pnl_mult[port.scrip], 2)
            booked_pnl = round(leg.booked_pnl + pnl, 2)

            self.logger.log(f"Booked P&L: {pnl} for Leg#{leg['name']}", "PNL", port.id)

            self.db.update_leg("status", "no_position", leg.id)
            self.db.update_leg("entered_ins", "", leg.id)
            self.db.update_leg("entered_token", "", leg.id)
            self.db.update_leg("entered_strike", 0, leg.id)
            self.db.update_leg("entered_underlying_price", 0, leg.id)
            self.db.update_leg("ltp", 0, leg.id)
            self.db.update_leg("running_pnl", 0, leg.id)
            self.db.update_leg("booked_pnl", float(booked_pnl), leg.id)
            logzero_logger.info(f"✅ reset_leg_for_exit completed for Leg#{leg['name']}")
        except Exception as e:
            logzero_logger.error(f"🚨 reset_leg_for_exit() error: {e}\n{traceback.format_exc()}")
            error_logger.error(f"🚨 reset_leg_for_exit() error: {e}\n{traceback.format_exc()}")
            raise


    def note_entry_order_info(self, leg, order, set_status_to_execute=True):
        try:
            if set_status_to_execute:
                self.db.update_leg("entry_order_status", "Execute", leg.id)

            actual_placedorder = int(order['OrderQuantity']) - int(order["LeavesQuantity"])
            new_filled_qty = int(leg.entry_filled_qty) + int(actual_placedorder)

            if new_filled_qty == 0:
                new_executed_price = 0
            else:
                new_executed_price = float(((leg.entry_filled_qty * leg.entry_executed_price) + (actual_placedorder) * float(order["OrderAverageTradedPrice"])) / new_filled_qty)

            self.db.update_leg("entry_filled_qty", int(new_filled_qty), leg.id)
            self.db.update_leg("entry_executed_price", float(new_executed_price), leg.id)
            logzero_logger.info(f"✅ note_entry_order_info updated leg#{leg.id} with qty={new_filled_qty}, price={new_executed_price}")
            return new_filled_qty, new_executed_price
        except Exception as e:
            logzero_logger.error(f"🚨 note_entry_order_info() error: {e}\n{traceback.format_exc()}")
            error_logger.error(f"🚨 note_entry_order_info() error: {e}\n{traceback.format_exc()}")
            raise

    def note_exit_order_info(self, leg, order, set_status_to_execute=True):
        try:
            if set_status_to_execute:
                self.db.update_leg("exit_order_status", "Execute", leg.id)
            
            actual_placedorder = int(order['OrderQuantity']) - int(order["LeavesQuantity"])
            new_filled_qty = int(leg.exit_filled_qty + actual_placedorder)

            # self.logger.log(f"✅ actual_placedorder : {actual_placedorder} - new_filled_qty: {new_filled_qty}","INFO", port.id))
            logzero_logger.info(f"✅ actual_placedorder : {actual_placedorder} - new_filled_qty: {new_filled_qty}")

            if new_filled_qty == 0:
                new_executed_price = 0
            else:
                new_executed_price = float(((leg.exit_filled_qty * leg.exit_executed_price) + (actual_placedorder) * float(order["OrderAverageTradedPrice"])) / new_filled_qty)

            self.db.update_leg("exit_filled_qty", int(new_filled_qty), leg.id)
            self.db.update_leg("exit_executed_price", float(new_executed_price), leg.id)
            logzero_logger.info(f"✅ note_exit_order_info updated leg#{leg.id} with qty={new_filled_qty}, price={new_executed_price}")
            return new_filled_qty, new_executed_price
        except Exception as e:
            logzero_logger.error(f"🚨 note_exit_order_info() error: {e}\n{traceback.format_exc()}")
            error_logger.error(f"🚨 note_exit_order_info() error: {e}\n{traceback.format_exc()}")
            raise




