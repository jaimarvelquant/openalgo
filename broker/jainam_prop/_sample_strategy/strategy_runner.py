import pytz
import traceback
import datetime as dt
from time import sleep
import concurrent.futures as cf
from order_tracker import OrderTracker
from logzero import logger as logzero_logger, logfile, setup_logger
import os

os.makedirs("logs", exist_ok=True)
logfile("logs/success.log", maxBytes=1e6, backupCount=3)
error_logger = setup_logger(name="error_logger", logfile="logs/error.log", level=40, disableStderrLogger=True)
         
class StrategyRunner:
    def __init__(self, strategy, db, logger, account_manager):
        self.strategy = strategy
        self.db = db
        self.logger = logger
        self.user = self.db.get_user(self.strategy.user_id)

        self.account_manager = account_manager
        self.order_tracker = OrderTracker(self.db, self.logger, self.account_manager, self.enter_leg, self.exit_leg)
        logzero_logger.info("✅ StrategyRunner initialized successfully")

    # Algo Functions

    def run(self):
        try:
            self.update_data()

            self.account_manager.do_login(self.strategy)
            if self.account_manager.is_logged_in(self.strategy):
                acc_obj = self.account_manager.accounts_objs[self.strategy.account_id]
                # print(f"{acc_obj.account.is_locked=}")
                if acc_obj.account.is_locked:
                    return

                ports = self.db.get_ports(self.strategy.id)

                res = self.check_max_loss(ports)
                # print(f"{res=}")
                if res == "return":
                    return

                orderbook = self.account_manager.get_orderbook(self.strategy)
                # position_book = self.account_manager.get_positions()
                # print(f"{orderbook=}")
                with cf.ThreadPoolExecutor(max_workers=10) as executor:
                    futures = []

                    for i, port in ports.iterrows():
                        futures.append(executor.submit(self.run_port, port, orderbook))

                    for future in cf.as_completed(futures):
                        try:
                            future.result()
                            logzero_logger.info("✅ run() completed successfully")
                        except Exception as e:
                            logzero_logger.error(f"🚨 run() execution error: {e}\n{traceback.format_exc()}")
                            error_logger.error(f"🚨 run() execution error: {e}\n{traceback.format_exc()}")

            else:
                sleep(2)
        except Exception as e:
            logzero_logger.error(f"🚨 run() error: {e}\n{traceback.format_exc()}")
            error_logger.error(f"🚨 run() error: {e}\n{traceback.format_exc()}")
            raise

    def run_port(self, port, orderbook):
        try:
            now = dt.datetime.now(tz=pytz.timezone("Asia/Kolkata"))
            current_time = now.time()

            legs = self.db.get_legs(port.id)

            res1 = self.check_combined_exit(port, legs)
            if res1 == "return":
                return

            # ----------------------------------------
            # Check Alerts & Manual Execute Button

            tv_alerts = self.db.get_pending_tv_alerts(port.id).sort_values(by=["id"], ascending=False)

            if len(tv_alerts) > 0:
                latest_alert = tv_alerts.iloc[0]
                self.db.update_alert("status", "complete", latest_alert.id)
            else:
                latest_alert = None

            if port.execute_button:
                # Reset execute button for next cycle, for this cycle, it will be considered
                self.db.update_port("execute_button", False, port.id)
                self.db.update_port("execute_button_lots", 0, port.id)

            # ----------------------------------------
            # Manual Squareoff Button

            if port.squareoff_button:
                self.db.update_port("squareoff_button", False, port.id)

                for i, leg in legs.iterrows():
                    if leg.status == "entered":
                        self.logger.log(f"Exiting Leg#{leg['name']} because Squareoff button was clicked", "INFO", port.id)
                        self.exit_leg(leg, port)

            # ----------------------------------------
            # Prime Flow

            for j, leg in legs.iterrows():
                res2 = self.order_tracker.check_leg_order(orderbook, leg, port, self.strategy)
                # print(f"{res2=} for {leg=}")
                if res2 != "continue":
                    continue # This continue means continue in loop, i.e., go check next cycle

                if leg.is_hedge:
                    # If leg is hedge, then don't check any conditions, it will follow what its parent leg does
                    continue

                if not port.stop_button:
                    if current_time >= port.squareoff_time:
                        if leg.status == "entered":
                            self.logger.log(f"Exiting Leg#{leg['name']} as Squareoff time is reached", "INFO", port.id)
                            self.exit_leg(leg, port)

                    elif current_time >= port.start_time and current_time <= port.squareoff_time: # After squareoff time no conditions are checked
                        if self.is_exited(leg):
                            if current_time <= port.stop_time and not port.combined_exit_done and not self.strategy.max_loss_hit: # Check Entry Conditions till Stop Time
                                to_take_entry = False
                                lots_to_enter = 0

                                if leg.idle:
                                    pass

                                else:
                                    if port.ub_enabled:
                                        if port.ub_upper_range == 0:
                                            if current_time >= port.ub_end_time:
                                                self.set_ub_range(port)

                                        else:
                                            if port.ub_monitoring == "Realtime":
                                                underlying_ltp = self.account_manager.get_ltp(
                                                    self.strategy,
                                                    _exch[0] if port.scrip_type == "INDEX" else _exch[2],
                                                    self.account_manager.get_underlying_token(port, self.strategy)
                                                )

                                                if port.ub_entry_at in ("High", "Any") and underlying_ltp >= port.ub_upper_range:
                                                    to_take_entry = True
                                                elif port.ub_entry_at in ("Low", "Any") and underlying_ltp <= port.ub_lower_range:
                                                    to_take_entry = True

                                    else:
                                        if latest_alert is not None and latest_alert.type == "ENTRY":
                                            self.logger.log(f"Taking entry in Leg#{leg['name']} as Latest TV Entry Alert: {latest_alert.id} has come", "INFO", port.id)
                                            to_take_entry = True
                                            lots_to_enter = latest_alert.lots

                                        elif port.execute_button:
                                            self.logger.log(f"Taking entry in Leg#{leg['name']} as Manual Execute Button was clicked", "INFO", port.id)
                                            to_take_entry = True
                                            lots_to_enter = port.execute_button_lots

                                        elif port.is_re_executed_port:
                                            self.logger.log(f"Taking entry in Leg#{leg['name']} as this port is re-executed", "INFO", port.id)
                                            to_take_entry = True
                                            lots_to_enter = port.lots_multiplier_set

                                if to_take_entry:
                                    # print("entering....")
                                    self.enter_leg(leg, port, lots_to_enter)

                                    # hedge_legs = self.db.get_hedge_legs(leg.id, port.id)
                                    # for t, h_leg in hedge_legs.iterrows():
                                    #     self.logger.log(f"Taking entry in Hedge Leg#{h_leg['name']}", "INFO", port.id)
                                    #     self.enter_leg(h_leg, port, lots_to_enter)

                                    self.db.update_port("is_re_executed_port", False, port.id)

                        elif self.is_entered(leg):
                            base_price_for_sl, sl = self.get_sl(leg)
                            base_price_for_tp, target = self.get_tp(leg)

                            _exch = self.account_manager.get_exchange(port.scrip)

                            ltp = self.account_manager.get_ltp(
                                self.strategy,
                                self.account_manager.get_exchange(port.scrip)[2],
                                leg.entered_token
                            )

                            underlying_ltp = self.account_manager.get_ltp(
                                self.strategy,
                                _exch[0] if port.scrip_type == "INDEX" else _exch[2],
                                self.account_manager.get_underlying_token(port, self.strategy)
                            )

                            to_exit = False

                            if latest_alert is not None and latest_alert.type == "EXIT":
                                self.logger.log(f"Exiting Leg#{leg['name']} as Latest TV Exit Alert: {latest_alert.id} has come", "INFO", port.id)
                                to_exit = True

                            else:
                                if leg.trade_type == "BUY":
                                    if sl != 0 and leg.sl_on == "PREMIUM" and ltp <= base_price_for_sl - sl:
                                        self.logger.log(f"Premium: {ltp} went below SL: {base_price_for_sl - sl}, exiting Leg#{leg['name']}", "INFO", port.id)
                                        to_exit = True
                                    elif target != 0 and ltp >= base_price_for_tp + target:
                                        self.logger.log(f"Premium: {ltp} went above Target: {base_price_for_tp + target}, exiting Leg#{leg['name']}", "INFO", port.id)
                                        to_exit = True

                                elif leg.trade_type == "SELL":
                                    if sl != 0 and leg.sl_on == "PREMIUM" and ltp >= base_price_for_sl + sl:
                                        self.logger.log(f"Premium: {ltp} went above SL: {base_price_for_sl + sl}, exiting Leg#{leg['name']}", "INFO", port.id)
                                        to_exit = True
                                    elif target != 0 and ltp <= base_price_for_tp - target:
                                        self.logger.log(f"Premium: {ltp} went below Target: {base_price_for_tp - target}, exiting Leg#{leg['name']}", "INFO", port.id)
                                        to_exit = True

                                if leg.sl_on == "UNDERLYING":
                                    position_type = self.get_position_type(leg)

                                    if sl != 0 and position_type == "BULLISH" and underlying_ltp <= base_price_for_sl - sl:
                                        self.logger.log(f"Underlying LTP: {underlying_ltp} went below SL: {base_price_for_sl - sl}, exiting Leg#{leg['name']}", "INFO", port.id)
                                        to_exit = True
                                    elif sl != 0 and position_type == "BEARISH" and underlying_ltp >= base_price_for_sl + sl:
                                        self.logger.log(f"Underlying LTP: {underlying_ltp} went above SL: {base_price_for_sl + sl}, exiting Leg#{leg['name']}", "INFO", port.id)
                                        to_exit = True

                                # No use for this as pending orders will get cancelled

                                # if port.combined_exit_done and self.is_entered(leg):
                                #     self.logger.log(f"Combined exit has happened, exiting Open Leg#{leg['name']}", "INFO", port.id)
                                #     to_exit = True

                            if leg.trade_type == "BUY":
                                running_pnl = ltp - leg.entry_executed_price
                            elif leg.trade_type == "SELL":
                                running_pnl = leg.entry_executed_price - ltp

                            running_pnl = round(running_pnl * leg.entry_filled_qty * self.account_manager.pnl_mult[port.scrip], 2)

                            if not to_exit and leg.last_profit_trail_point != 0 and running_pnl <= leg.locked_profit:
                                self.logger.log(f"P&L: {running_pnl} went below Locked Profit: {leg.locked_profit}, exiting Leg#{leg['name']}", "INFO", port.id)
                                to_exit = True

                            if to_exit:
                                self.exit_leg(leg, port)

                                # hedge_legs = self.db.get_hedge_legs(leg.id, port.id)
                                # for t, h_leg in hedge_legs.iterrows():
                                #     self.logger.log(f"Exiting Hedge Leg#{h_leg['name']}", "INFO", port.id)
                                #     self.exit_leg(h_leg, port)

                            else:
                                if leg.if_profit_reaches != 0 and leg.last_profit_trail_point == 0:
                                    if running_pnl >= leg.if_profit_reaches:
                                        self.logger.log(f"Leg #{leg['name']} Running P&L: {running_pnl} went above If-Profit-Reaches: {leg.if_profit_reaches}, locking min. profit at {leg.lock_min_profit_at}", "INFO", port.id)
                                        self.db.update_leg("locked_profit", float(leg.lock_min_profit_at), leg.id)
                                        self.db.update_leg("last_profit_trail_point", float(leg.if_profit_reaches), leg.id)

                                elif leg.for_every_increase_in_profit != 0 and running_pnl >= leg.last_profit_trail_point + leg.for_every_increase_in_profit:
                                    new_trail_point = round(leg.last_profit_trail_point + leg.for_every_increase_in_profit, 2)
                                    trailed_profit = round(leg.locked_profit + leg.trail_profit_by, 2)

                                    self.logger.log(f"Leg #{leg['name']} Running P&L: {running_pnl} went above Next trail point: {new_trail_point}, trailing profit at {trailed_profit}", "INFO", port.id)
                                    self.db.update_leg("locked_profit", float(trailed_profit), leg.id)
                                    self.db.update_leg("last_profit_trail_point", float(new_trail_point), leg.id)

                                self.db.update_leg("ltp", float(ltp), leg.id)
                                self.db.update_leg("running_pnl", float(running_pnl), leg.id)
            logzero_logger.info(f"✅ run_port completed successfully for port: {port['name']}")
        except Exception as e:
            logzero_logger.error(f"🚨 run_port error: {e}\n{traceback.format_exc()}")
            error_logger.error(f"🚨 run_port error: {e}\n{traceback.format_exc()}")
            raise

    def update_data(self):
        try:
            self.user = self.db.get_user(self.user.id)
            self.strategy = self.db.get_strategy(self.strategy.id)
            logzero_logger.info("✅ update_data completed successfully")
        except Exception as e:
            # Strategy might be deleted
            logzero_logger.error(f"🚨 update_data error: {e}\n{traceback.format_exc()}")
            error_logger.error(f"🚨 update_data error: {e}\n{traceback.format_exc()}")
            return "deleted"

    # Entry/Exit Functions

    def enter_leg(self, leg, port, alert_lots_multiplier, order_type=None, qty=0, modification=False, final_modification=False):
        try:
            if qty == 0:
                lots = leg.lots * alert_lots_multiplier * self.strategy.lots_multiplier
            else:
                lots = qty

            if modification:
                ins = leg.entered_ins
                strike = leg.entered_strike
                token = leg.entered_token

            else:
                ins, strike, token = self.account_manager.get_instrument(leg, port, self.strategy)
            entry_order_id, order_msg, order_qty, entry_price, underlying_entry_price = self.account_manager.place_order(
                self.strategy,
                ins,
                token,
                lots,
                leg.trade_type,
                leg.order_type if order_type is None else order_type,
                leg,
                port,
                qty_type="lots" if qty == 0 else "qty",
                limit_pct=leg.default_limit_pct if final_modification else leg.limit_pct
            )

            self.db.update_leg("status", "entered", leg.id)
            self.db.update_leg("entered_ins", ins, leg.id)
            self.db.update_leg("entered_token", token, leg.id)
            self.db.update_leg("entered_strike", int(strike), leg.id)
            self.db.update_leg("entered_underlying_price", float(underlying_entry_price), leg.id)
            self.db.update_leg("ltp", 0, leg.id)
            self.db.update_leg("running_pnl", 0, leg.id)

            self.db.update_leg("entry_order_id", entry_order_id, leg.id)
            self.db.update_leg("entry_order_type", leg.order_type if order_type is None else order_type, leg.id)
            self.db.update_leg("entry_order_message", order_msg, leg.id)

            if not modification:
                self.db.update_leg("entry_num_modifications_done", 0, leg.id)
                self.db.update_port("lots_multiplier_set", float(alert_lots_multiplier), port.id)

                self.db.update_leg("exit_order_id", "", leg.id)
                self.db.update_leg("exit_order_type", "", leg.id)
                self.db.update_leg("exit_order_message", "", leg.id)
                self.db.update_leg("exit_order_status", "", leg.id)
                self.db.update_leg("exit_filled_qty", 0, leg.id)
                self.db.update_leg("exit_executed_price", 0, leg.id)

            else:
                self.db.update_leg("entry_num_modifications_done", leg.entry_num_modifications_done+1, leg.id)

            if port.trading_mode == "Live":
                self.db.update_leg("entry_order_status", "Pending", leg.id)

                if not modification:
                    self.db.update_leg("entry_filled_qty", 0, leg.id)
                    self.db.update_leg("entry_executed_price", 0, leg.id)

            elif port.trading_mode == "Paper":
                self.db.update_leg("entry_order_status", "Execute", leg.id)
                self.db.update_leg("entry_filled_qty", int(order_qty), leg.id)
                self.db.update_leg("entry_executed_price", float(entry_price), leg.id)
            logzero_logger.info(f"✅ enter_leg completed for Leg#{leg['name']} on Port#{port['name']}")
        except Exception as e:
            logzero_logger.error(f"🚨 enter_leg error: {e}\n{traceback.format_exc()}")
            error_logger.error(f"🚨 enter_leg error: {e}\n{traceback.format_exc()}")
            raise

    def exit_leg(self, leg, port, order_type=None, modification=False, final_modification=False):
        exit_order_id, order_msg, order_qty, exit_price, underlying_exit_price = self.account_manager.place_order(
            self.strategy,
            leg.entered_ins,
            leg.entered_token,
            # qty_to_exit,
            leg.entry_filled_qty,
            "SELL" if leg.trade_type == "BUY" else "BUY",
            leg.order_type if order_type is None else order_type,
            leg,
            port,
            qty_type="qty",
            limit_pct=leg.default_limit_pct if final_modification else leg.limit_pct
        )

        try:
            if leg.entry_order_status == "Pending":
                cancellation_res = self.account_manager.cancel_order(leg.entry_order_id, self.strategy)
                self.logger.log(f"Cancelled pending entry order: {leg.entry_order_id}, response: {str(cancellation_res)}", "INFO", port.id)

            self.db.update_leg("status", "exited", leg.id)
            self.db.update_leg("exit_order_id", exit_order_id, leg.id)
            self.db.update_leg("exit_order_type", leg.order_type if order_type is None else order_type, leg.id)
            self.db.update_leg("exit_order_message", order_msg, leg.id)

            if not modification:
                self.db.update_leg("exit_num_modifications_done", 0, leg.id)
            else:
                self.db.update_leg("exit_num_modifications_done", leg.exit_num_modifications_done+1, leg.id)

            if port.trading_mode == "Live":
                self.db.update_leg("exit_order_status", "Pending", leg.id)

                if not modification:
                    self.db.update_leg("exit_filled_qty", 0, leg.id)
                    self.db.update_leg("exit_executed_price", 0, leg.id)

            elif port.trading_mode == "Paper":
                self.db.update_leg("exit_order_status", "Execute", leg.id)
                self.db.update_leg("exit_filled_qty", int(order_qty), leg.id)
                self.db.update_leg("exit_executed_price", float(exit_price), leg.id)
            logzero_logger.info(f"✅ exit_leg completed for Leg#{leg['name']} on Port#{port['name']}")
        except Exception as e:
            logzero_logger.error(f"🚨 exit_leg error: {e}\n{traceback.format_exc()}")
            error_logger.error(f"🚨 exit_leg error: {e}\n{traceback.format_exc()}")
            raise

    def exit_all(self):
        try:
            ports = self.db.get_ports(self.strategy.id)

            for i, port in ports.iterrows():
                legs = self.db.get_legs(port.id)

                for j, leg in legs.iterrows():
                    if not leg.is_hedge and self.is_entered(leg):
                        self.exit_leg(leg, port)

                        # hedge_legs = self.db.get_hedge_legs(leg.id, port.id)
                        # for j, h in hedge_legs.iterrows():
                        #     self.exit_leg(h, port)
            logzero_logger.info("✅ exit_all completed successfully")
        except Exception as e:
            logzero_logger.error(f"🚨 exit_all error: {e}\n{traceback.format_exc()}")
            error_logger.error(f"🚨 exit_all error: {e}\n{traceback.format_exc()}")
            raise

    # -------------------------------------------
    # Utility Functions

    def is_entered(self, leg):
        return leg.status == "entered" and leg.entry_order_message in ("sucess", "success", "successful") and leg.entry_order_status == "Execute"

    def is_exited(self, leg):
        return leg.status == "no_position" and leg.exit_order_message in ("", "sucess", "success", "successful") and leg.exit_order_status in ("", "Execute")

    def get_sl(self, leg):
        try:
            if leg.sl_on == "PREMIUM":
                base_price = leg.entry_executed_price
            elif leg.sl_on == "UNDERLYING":
                base_price = leg.entered_underlying_price

            try:
                sl_pts = round(float(leg.sl), 2)

            except ValueError:
                sl_pct = round(float(leg.sl.replace("%", "").strip()) / 100, 2)
                sl_pts = round(base_price * sl_pct, 2)
            logzero_logger.info(f"✅ get_sl completed for leg: {leg['name']}")
            return base_price, sl_pts
        except Exception as e:
            logzero_logger.error(f"🚨 get_sl error: {e}\n{traceback.format_exc()}")
            error_logger.error(f"🚨 get_sl error: {e}\n{traceback.format_exc()}")
            raise

    def get_tp(self, leg):
        try:
            base_price = leg.entry_executed_price
            tp_pts = round(float(leg.target), 2)
            logzero_logger.info(f"✅ get_tp completed for leg: {leg['name']}")
            return base_price, tp_pts
        except ValueError as e:
            base_price = leg.entry_executed_price
            tp_pct = round(float(leg.target.replace("%", "").strip()) / 100, 2)
            tp_pts = round(base_price * tp_pct, 2)
            logzero_logger.error(f"🚨 get_tp ValueError: {e}\n{traceback.format_exc()}\nbase_price={base_price}, tp_pts={tp_pts}")
            error_logger.error(f"🚨 get_tp ValueError: {e}\n{traceback.format_exc()}\nbase_price={base_price}, tp_pts={tp_pts}")
            return base_price, tp_pts
        except Exception as e:
            logzero_logger.error(f"🚨 get_tp error: {e}\n{traceback.format_exc()}")
            error_logger.error(f"🚨 get_tp error: {e}\n{traceback.format_exc()}")
            raise

    def get_position_type(self, leg):
        try:
            if leg.ins_type == "FUT" and leg.trade_type == "BUY":
                return "BULLISH"
            elif leg.ins_type == "FUT" and leg.trade_type == "SELL":
                return "BEARISH"
            elif leg.ins_type == "CE" and leg.trade_type == "BUY":
                return "BULLISH"
            elif leg.ins_type == "CE" and leg.trade_type == "SELL":
                return "BEARISH"
            elif leg.ins_type == "PE" and leg.trade_type == "BUY":
                return "BEARISH"
            elif leg.ins_type == "PE" and leg.trade_type == "SELL":
                return "BULLISH"
            logzero_logger.info(f"✅ get_position_type completed for leg: {leg['name']}")
        except Exception as e:
            logzero_logger.error(f"🚨 get_position_type error: {e}\n{traceback.format_exc()}")
            error_logger.error(f"🚨 get_position_type error: {e}\n{traceback.format_exc()}")
            raise

    def re_execute_port(self, port):
        try:
            cur_name = port['name']

            prefix = cur_name
            new_num = 1

            if "_REX" in cur_name:
                prefix = cur_name.split("_REX")[0]
                num = int(cur_name.split("_REX")[1])
                new_num = num + 1

            new_name = prefix + "_REX" + str(new_num)
            self.db.clone_port(new_name, port, self.strategy.id)
            logzero_logger.info(f"✅ re_execute_port completed for port: {port['name']} -> {new_name}")
        except Exception as e:
            logzero_logger.error(f"🚨 re_execute_port error: {e}\n{traceback.format_exc()}")
            error_logger.error(f"🚨 re_execute_port error: {e}\n{traceback.format_exc()}")
            raise

    def check_combined_exit(self, port, legs):
        try:
            if not port.combined_exit_done:
                combined_pnl = 0

                for k, leg in legs.iterrows():
                    combined_pnl += leg.running_pnl + leg.booked_pnl

                combined_pnl = round(combined_pnl, 2)
                combined_exit = False

                if port.combined_sl != 0 and combined_pnl <= -port.combined_sl:
                    self.logger.log(f"Combined P&L: {combined_pnl} went below Combined SL: {-port.combined_sl}, re-executing port", "INFO", port.id)
                    combined_exit = True

                elif port.combined_target != 0 and combined_pnl >= port.combined_target:
                    self.logger.log(f"Combined P&L: {combined_pnl} went above Combined Target: {port.combined_target}, re-executing port", "INFO", port.id)
                    combined_exit = True

                if combined_exit:
                    for k, leg in legs.iterrows():
                        if self.is_entered(leg):
                            self.exit_leg(leg, port)

                    self.db.update_port("combined_exit_done", True, port.id)
                    # self.db.update_port("status", "non_tradable", port.id)

                    if port.to_re_execute:
                        self.re_execute_port(port)
                    logzero_logger.info(f"✅ check_combined_exit triggered for port: {port['name']}")
                    return "return"
            logzero_logger.info(f"✅ check_combined_exit completed for port: {port['name']}")
        except Exception as e:
            logzero_logger.error(f"🚨 check_combined_exit error: {e}\n{traceback.format_exc()}")
            error_logger.error(f"🚨 check_combined_exit error: {e}\n{traceback.format_exc()}")
            raise

    def check_max_loss(self, ports):
        try:
            if not self.strategy.max_loss_hit and self.strategy.max_loss != 0:
                total_pnl = 0

                for _, p in ports.iterrows():
                    legs = self.db.get_legs(p.id)
                    for i, leg in legs.iterrows():
                        total_pnl += round(leg.running_pnl + leg.booked_pnl, 2)

                self.db.update_strategy("total_pnl", total_pnl, self.strategy.id)

                if total_pnl <= -self.strategy.max_loss:
                    self.logger.log(f"Total P&L: {total_pnl} went below Max Loss: {-self.strategy.max_loss}, exiting strategy {self.strategy['name']}", "ERROR")
                    self.logger.log(f"Total P&L: {total_pnl} went below Max Loss: {-self.strategy.max_loss}, exiting strategy {self.strategy['name']}", "ERROR",ports.id)
                    self.db.update_strategy("max_loss_hit", True, self.strategy.id)

                    self.exit_all()
                    logzero_logger.info(f"✅ check_max_loss triggered exit for strategy: {self.strategy['name']}")
                    return "return"
            logzero_logger.info(f"✅ check_max_loss completed successfully for strategy: {self.strategy['name']}")
        except Exception as e:
            logzero_logger.error(f"🚨 check_max_loss error: {e}\n{traceback.format_exc()}")
            error_logger.error(f"🚨 check_max_loss error: {e}\n{traceback.format_exc()}")
            raise