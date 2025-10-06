import pytz
import math
import json
import threading
import traceback
import pandas as pd
import datetime as dt
from time import sleep
from helpers import get_strike
import concurrent.futures as cf
from multitrade import Multitrade
from xts_connect import XTS_Symphony


class AccountManager:
	def __init__(self, db, logger, mc):
		self.db = db
		self.logger = logger
		self.mc = mc

		all_accounts = self.db.get_accounts()
		self.accounts_objs = {acc.id: None for i, acc in all_accounts.iterrows()}

		# self.scrip_map = {
		#     "NIFTY": "  ",
		#     "BANKNIFTY": "NIFTY BANK",
		#     "FINNIFTY": "NIFTY FIN SERVICE",
		#     # No underlying for CRUDEOIL & NATURALGAS
		#     "CRUDEOIL": "CRUDEOIL",
		#     "NATURALGAS": "NATURALGAS",
		# }

		self.pnl_mult = {
			"NIFTY": 1,
			"BANKNIFTY": 1,
			"FINNIFTY": 1,
			"MIDCPNIFTY": 1,
			"CRUDEOIL": 100,
			"NATURALGAS": 1250,
			"GOLDM": 10,
			"SILVERM": 5
		}

		self.check_lock = threading.Lock()

	def do_login(self, strategy):
		# str_accounts = self.db.get_accounts(strategy.id)

		# if isinstance(str_accounts, pd.Series):
		#     account = str_accounts
		#     if self.accounts_objs[account.id] is None:
		#         self.login(account)
		# else:
		#     for i, account in str_accounts.iterrows():
		#         if self.accounts_objs[account.id] is None:
		#             self.login(account)

		with self.check_lock:
			if self.accounts_objs[strategy.account_id] is None:
				self.login(strategy.account_id)

	def login(self, account_id):
		account = self.db.get_account(account_id)

		acc = Account(account, self.db, self.logger, self.mc)
		self.accounts_objs[account.id] = acc
		try:
			acc.logout()
		except:
			traceback.print_exc()
		res = acc.login()

		if res == "error":
			self.accounts_objs[account.id] = None

	def is_logged_in(self, strategy):
		# is_logged_in = True

		# str_accounts = self.db.get_accounts(strategy.id)

		# if isinstance(str_accounts, pd.Series):
		#     account = str_accounts
		#     if self.accounts_objs[account.id] is None or not self.accounts_objs[account.id].is_ws_connected:
		#         is_logged_in = False

		# else:
		#     for i, account in str_accounts.iterrows():
		#         if self.accounts_objs[account.id] is None or not self.accounts_objs[account.id].is_ws_connected:
		#             is_logged_in = False
		#             break

		# return is_logged_in

		with self.check_lock:
			# print(f"{strategy.account_id=}")
			# print(f"{self.accounts_objs=}")
			
			# print(f"{self.accounts_objs[strategy.account_id]=} and {self.accounts_objs[strategy.account_id].is_ws_connected=}")
			return self.accounts_objs[strategy.account_id] is not None and self.accounts_objs[strategy.account_id].is_ws_connected

	def get_orderbook(self, strategy):
		account_to_use = self.accounts_objs[strategy.account_id]
		return account_to_use.get_orderbook()

	def place_order(self, strategy, ins, token, lots, tt, ot, leg, port, qty_type="lots", limit_pct=None):
		account = self.db.get_account(strategy.account_id)
		exch_data = self.get_exchange(port.scrip)
		print(f"{exch_data=}")
		print(f"{token=}")
		print(f"{strategy=}")
		ltp = self.get_ltp(strategy, exch_data[2], token)
		print(f"{ltp=}")
		u_token = self.get_underlying_token(port, strategy)
		print(f"{u_token=}")
		underlying_ltp = self.get_ltp(strategy, exch_data[0] if port.scrip_type == "INDEX" else exch_data[2], u_token)

		if limit_pct is None:
			limit_pct = leg.limit_pct

		if tt == "BUY":
			limit_price = ltp * (1 + limit_pct / 100)
		elif tt == "SELL":
			limit_price = ltp * (1 - limit_pct / 100)

		limit_price = round(round(limit_price / 0.05) * 0.05, 2)

		# for i, account in accounts.iterrows():

		if qty_type == "lots":
			qty = int(math.floor(lots * account.lots_multiplier) * self.get_lot_size(port.scrip))
		elif qty_type == "qty":
			qty = lots

		order_id, msg = self.accounts_objs[account.id].place_order(exch_data[2], ins, token, tt, ot, qty, limit_price, port)
		return order_id, msg, qty, ltp, underlying_ltp

	def cancel_order(self, order_id, strategy):
		account_to_use = self.accounts_objs[strategy.account_id]
		return account_to_use.cancel_order(order_id)

	def check_account_functions(self, strategies):
		account_ids = [s.strategy.account_id for s in strategies]

		for acc_id, acc_obj in self.accounts_objs.items():
			if acc_obj is not None:
				acc_obj.refresh_account_data()

				if acc_obj.account.is_locked:
					# If account is locked, then ignore this account
					continue

				if acc_id in account_ids:
					acc_pnl = 0
					str_accounts = {}

					for _str in strategies:
						if _str.strategy.account_id == acc_id:
							if acc_id in str_accounts.keys():
								str_accounts[acc_id].append(_str)
							else:
								str_accounts[acc_id] = [_str]

							ports = self.db.get_ports(_str.strategy.id)

							for i, port in ports.iterrows():
								legs = self.db.get_legs(port.id)

								for j, leg in legs.iterrows():
									acc_pnl += round(leg.running_pnl + leg.booked_pnl, 2)

					# print(str_accounts)

					max_profit_reached = acc_obj.account.max_profit_reached
					max_loss_reached = acc_obj.account.max_loss_reached

					if acc_pnl >= max_profit_reached:
						max_profit_reached = acc_pnl
					elif acc_pnl <= max_loss_reached:
						max_loss_reached = acc_pnl

					self.db.update_account("total_pnl", float(acc_pnl), acc_id)
					self.db.update_account("max_profit_reached", float(max_profit_reached), acc_id)
					self.db.update_account("max_loss_reached", float(max_loss_reached), acc_id)

					to_exit = False
					current_time = dt.datetime.now(tz=pytz.timezone("Asia/Kolkata")).time()

					if acc_obj.account.squareoff_button:
						self.logger.log(f"Squareoff button pressed, exiting complete account #{acc_obj.account['name']}", "SUCCESS")
						self.db.update_account("squareoff_button", False, acc_id)
						to_exit = True

					elif current_time >= acc_obj.account.squareoff_time:
						self.logger.log(f"Time: {current_time} is over squareoff time: {acc_obj.account.squareoff_time}, exiting complete account #{acc_obj.account['name']}", "SUCCESS")
						to_exit = True

					elif acc_obj.account.max_loss != 0 and acc_pnl <= -acc_obj.account.max_loss:
						self.logger.log(f"Account Net P&L: {acc_pnl} hit Max Loss: {acc_obj.account.max_loss}, exiting complete account #{acc_obj.account['name']}", "SUCCESS")
						to_exit = True

					else:
						if acc_obj.account.if_profit_reaches > 0:
							if acc_obj.account.locked_profit_1 == 0:
								if acc_pnl >= acc_obj.account.if_profit_reaches:
									locked_profit_1 = acc_obj.account.lock_min_profit_at
									locked_profit_2 = acc_obj.account.if_profit_reaches

									self.logger.log(f"Account Net P&L: {acc_pnl} went above IF-PROFIT-REACHES: {acc_obj.account.if_profit_reaches}, locking min. profit at: {locked_profit_1} in account #{acc_obj.account['name']}", "EMERGENCY")

									self.db.update_account("locked_profit_1", float(locked_profit_1), acc_id)
									self.db.update_account("locked_profit_2", float(locked_profit_2), acc_id)

							else:
								next_trail_point = float(acc_obj.account.locked_profit_2 + acc_obj.account.every_increase_in_profit)
								if acc_pnl >= next_trail_point:
									trailed_profit = float(acc_obj.account.locked_profit_1 + acc_obj.account.trail_profit_by)
									self.logger.log(f"Account Net P&L: {acc_pnl} went above next trail point: {next_trail_point}, trailing min. profit to: {trailed_profit} in account #{acc_obj.account['name']}", "SUCCESS")

									self.db.update_account("locked_profit_1", trailed_profit, acc_id)
									self.db.update_account("locked_profit_2", next_trail_point, acc_id)

								elif acc_pnl <= acc_obj.account.locked_profit_1:
									self.logger.log(f"Account Net P&L: {acc_pnl} hit Locked Profit: {acc_obj.account.locked_profit_1}, exiting complete account #{acc_obj.account['name']}", "SUCCESS")
									to_exit = True

					if to_exit:
						acc_obj.exit_account(str_accounts)

	# -------------------------------------
	# Utilities
	# -------------------------------------

	def get_ltp(self, strategy, exch, token):
		# accounts = self.db.get_accounts(strategy.id)
		# account_to_use = self.accounts_objs[accounts.iloc[0].id]

		account_to_use = self.accounts_objs[strategy.account_id]
		return account_to_use.get_ltp(2 if exch=="NSEFO" else 1, token)

	def get_exchange(self, scrip):
		if scrip in ("NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY"):
			return ["NSECM", "NFO", "NSEFO"]
		elif scrip in ("CRUDEOIL", "NATURALGAS", "GOLDM", "SILVERM"):
			return ["MCX", "MCX", "MCX"]

	def get_instrument(self, leg, port, strategy):
		# accounts = self.db.get_accounts(strategy.id)
		# account_to_use = self.accounts_objs[accounts.iloc[0].id]

		account_to_use = self.accounts_objs[strategy.account_id]
		exch_data = self.get_exchange(port.scrip)

		if leg.ins_type == "FUT":
			# print(f"{port.scrip=}")
			# print(f"{exch_data=}")
			# print(f"{leg.ins_type=}")
			# print(f"{leg.expiry=}")
			
			row = account_to_use.master_contract[
				(account_to_use.master_contract["symbol"] == port.scrip) &
				(account_to_use.master_contract["exchange"] == exch_data[2]) &
				(account_to_use.master_contract["option_type"] == "FUTIDX") &
				(pd.to_datetime(account_to_use.master_contract["expiry_date"]) == dt.datetime(leg.expiry.year, leg.expiry.month, leg.expiry.day, 0, 0, 0))
			].iloc[-1]
			return row.sec_description, 0, row.sec_id

		else:
			if not leg.actual_strike:
				token = self.get_underlying_token(port, strategy)
				strike = get_strike(token, exch_data, self.get_ltp, leg, port, strategy, account_to_use)
			else:
				strike = leg.actual_strike
			strike = int(strike)
			# print(f"{strike=}")    

			row = account_to_use.master_contract[
				(account_to_use.master_contract["symbol"] == port.scrip) &
				(account_to_use.master_contract["exchange"] == exch_data[2]) &
				(account_to_use.master_contract["option_type"] == leg.ins_type) &
				(pd.to_datetime(account_to_use.master_contract["expiry_date"]) == dt.datetime(leg.expiry.year, leg.expiry.month, leg.expiry.day, 0, 0, 0)) 
				# (account_to_use.master_contract["strike_price"] == strike)
			]
			row = row[(row["strike_price"].astype(int) == strike)].iloc[0]
			# print(f"{row=}")

			return row.sec_description, strike, row.sec_id

	def get_lot_size(self, scrip):
		return self.mc[(self.mc["name"] == scrip) & (self.mc["instrument_type"] == "CE")].iloc[0].lot_size # Lot Size is same for CE & PE

	def get_underlying_token(self, port, strategy):
		# accounts = self.db.get_accounts(strategy.id)
		# account_to_use = self.accounts_objs[accounts.iloc[0].id]

		account_to_use = self.accounts_objs[strategy.account_id]

		if port.scrip_type == "INDEX":
			index_name_map = {
				"NIFTY": "26000",
				"BANKNIFTY": "26001",
				# "FINNIFTY": "Nifty Fin Service",
				# No index for MCX
				# "CRUDEOIL": "Crude Oil",
				# "NATURALGAS": "Natural Gas"
			}
			return index_name_map[port.scrip]
			index_name_map = {
				"NIFTY": "Nifty 50",
				"BANKNIFTY": "Nifty Bank",
				"FINNIFTY": "Nifty Fin Service",
				"MIDCPNIFTY": "NIFTY MID SELECT",
				# No index for MCX
				# "CRUDEOIL": "Crude Oil",
				# "NATURALGAS": "Natural Gas"
			}

			return account_to_use.master_contract[
				(account_to_use.master_contract["symbol"] == index_name_map[port.scrip]) &
				(account_to_use.master_contract["instrument_type"] == "INDEX") &
				(account_to_use.master_contract["exchange"] == self.get_exchange(port.scrip)[0])
			].iloc[0].sec_id

		elif port.scrip_type == "FUT":
			expiry = self.mc[(self.mc["name"] == port.scrip) & (self.mc["instrument_type"] == "FUT")].expiry.min().to_pydatetime()
			# print(f"{port.scrip=}")
			# print(f"{self.get_exchange(port.scrip)[2]=}")
			# print(f"{expiry=}")
			# print(account_to_use.master_contract.head())
			# print(account_to_use.master_contract[
			# 	(account_to_use.master_contract["symbol"] == port.scrip) &
			# 	(account_to_use.master_contract["instrument_type"] == "FUTIDX") &
			# 	(account_to_use.master_contract["InstrumentType"] == "1") &
				
			# 	(account_to_use.master_contract["exchange"] == self.get_exchange(port.scrip)[2]) &
			# 	(pd.to_datetime(account_to_use.master_contract["expiry_date"]) == dt.datetime(expiry.year, expiry.month, expiry.day, 0, 0, 0))
			# ])
			return account_to_use.master_contract[
				(account_to_use.master_contract["symbol"] == port.scrip) &
				(account_to_use.master_contract["instrument_type"] == "FUTIDX") &
				(account_to_use.master_contract["exchange"] == self.get_exchange(port.scrip)[2]) &
				(account_to_use.master_contract["InstrumentType"] == "1") &
				(pd.to_datetime(account_to_use.master_contract["expiry_date"]) == dt.datetime(expiry.year, expiry.month, expiry.day, 0, 0, 0))
			].iloc[0].sec_id


class Account:
	def __init__(self, account, db, logger, master_contract):
		self.account = account
		self.db = db
		self.logger = logger
		self.kite_master_contract = master_contract
		self.master_contract = None

		self.is_ws_connected = False
		# if self.account.type == "XTS":
		self.broker = XTS_Symphony( # For now, multitrade is the only broker
			self.account.market_api_key,
			self.account.market_api_secret,
			self.account.api_key,
			self.account.api_secret,
			self.account.root_url
		)

		self.ticks_dict = {}
		self.tokens_dict = {}

	def refresh_account_data(self):
		self.account = self.db.get_account(self.account.id)

	def login(self):
		try:
			req_token = self.broker.login()
			# self.broker.generate_session_token(req_token)
			self.connect_broker_ws()

			self.store_master_contract()
			print("setup complete!")

		except Exception as e:
			print(traceback.format_exc())
			self.logger.log(f"Error {e} came while trying to login to account: {self.account['name']}", "ERROR")
			sleep(5)

			return "error"

	def logout(self):
		try:
			self.broker.logout()

		except Exception as e:
			self.logger.log(f"Error {e} came while trying to logout account: {self.account['name']}", "ERROR")
			sleep(5)

			return "error"

	def connect_broker_ws(self):
		self.broker.connect_ws(self.ws_on_connect, self.ws_on_message, self.ws_on_close, self.ws_on_error)
		print("in connect to broker ws ")

	def store_master_contract(self):
		for i in range(10):
			try:
				self.master_contract = self.broker.get_master_contract()
				# self.master_contract = self.master_contract[self.master_contract.exchange.isin(["NSEFO", "NSECM", "MCX"])]
				# self.master_contract = self.master_contract[self.master_contract.instrument_type.isin(["INDEX", "FUTIDX", "FUTCOM", "OPTIDX", "OPTFUT"])]
				print(f"master contract is ")
				print(self.master_contract.head())

				break

			except Exception as e:
				self.logger.log(f"Error {e} came while fetching master contract from Account#{self.account['name']}", "ERROR")
				traceback.print_exc()
				continue

	def ws_on_connect(self):
		self.logger.log(f"Connected to Websocket successfully: {self.account['name']}", "SUCCESS")

		self.ticks_dict = {}
		self.tokens_dict = {}

		self.is_ws_connected = True

	def ws_on_message(self,msg):
		try:
			try:
				msg = json.loads(msg)
				exc, inst = msg["ExchangeSegment"],  msg["ExchangeInstrumentID"]
				ltp = msg["LastTradedPrice"]
				print(f"{msg=}")

				self.ticks_dict[f"{exc}:{inst}"] = ltp
			except:
				print("error")

		except Exception as e:
			self.logger.log(f"Error {e} came in WS on_message", "ERROR")

	def ws_on_close(self, ws, code, reason):
		self.logger.log(f"Multitrade Websocket connection closed @ {code} {reason}, retrying in 1 sec: {self.account['name']}", "ERROR")

		sleep(1)

		self.connect_broker_ws()

	def ws_on_error(self, ws, err):
		self.logger.log(f"Multitrade Websocket error @ {err}: {self.account['name']}", "ERROR")

	def get_ltp(self, exch, token):
		print(f"fetching ltp for {exch=} and {token=}")
		# exch = "2"
		token_str = f"{exch}:{token}"

		if token_str not in list(self.ticks_dict.keys()):
			self.broker.subscribe(int(exch), int(token))
			self.ticks_dict[token_str] = 0.0

			self.logger.log(f"Subscribed to {token_str}", "SUCCESS")

		for i in range(50):
			ltp = self.ticks_dict[token_str]

			if ltp != 0.0:
				return ltp
			else:
				sleep(0.1)

	def get_orderbook(self):
		try:
			orderbook = self.broker.orderbook()

		except Exception as e:
			self.logger.log(f"Error {e} came while fetching orderbook from Account#{self.account['name']}", "ERROR")
			sleep(1)

		return orderbook

	def place_order(self, exch, ins, token, tt, ot, qty, price, port):
		order_id = "0"
		msg = ""

		if port.trading_mode == "Live":
			try:
				order_id, msg = self.broker.place_order(
					exch,
					token,
					tt,
					ot,
					qty,
					price
				)

			except Exception as e:
				self.logger.log(f"Error {e} came while placing order in Account#{self.account['name']}", "ERROR", port.id)
				sleep(1)

		elif port.trading_mode == "Paper":
			msg = "success"

		self.db.add_order(ins, tt, qty, ot, price, port.id, self.account.id)
		self.logger.log(f"Order Placed: {ins} | Trade: {tt} | Qty: {qty} | Type: {ot} | Price: {price} | Account: {self.account['name']}", "SUCCESS", port.id)

		return order_id, msg

	def cancel_order(self, order_id):
		try:
			return self.broker.cancel_order(order_id)

		except Exception as e:
			self.logger.log(f"Error {e} came while cancelling order: {order_id} from Account#{self.account['name']}", "ERROR")
			sleep(1)

	def exit_account(self, str_accounts):
		for strategy in str_accounts[self.account.id]:
			self.db.update_account("locked_profit_1", 0, self.account.id)
			self.db.update_account("locked_profit_2", 0, self.account.id)
			self.db.update_account("is_locked", True, self.account.id)

			strategy.exit_all()