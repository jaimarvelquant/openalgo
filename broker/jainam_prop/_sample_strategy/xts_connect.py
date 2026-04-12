"""
    Connect.py

    API wrapper for XTS Connect REST APIs.

    :copyright:
    :license: see LICENSE for details.
"""


import json
import logging
import requests
from urllib import parse
import os
from datetime import datetime
import socketio
import requests
import json
import traceback
import pandas as pd
from requests import exceptions
from requests.exceptions import HTTPError
from requests import ConnectTimeout, HTTPError, Timeout, ConnectionError
from threading import Thread
log = logging.getLogger(__name__)


class XTS_Symphony:
    def __init__(self, m_api_key, m_api_secret, i_api_key, i_api_secret, root_url, user_id="*****", i_token=None, m_token=None, source="WEBAPI"):
        self.market_api_key = m_api_key
        self.market_api_secret = m_api_secret
        self.interactive_api_key = i_api_key
        self.interactive_api_secret = i_api_secret
        self.root_url = root_url
        self.interactive_token = i_token
        self.market_token = m_token
        self.source = source
        self.user_id = user_id

        self.ws = None
        self.to_verify = False # For SSL Errors, set this to False

    def login(self):
        try:
            self.interactive_session = XTSConnect(self.interactive_api_key, self.interactive_api_secret, self.source, self.root_url)
            intractive_response = self.interactive_session.interactive_login()
            # print(intractive_response)
            self.market_session = XTSConnect(self.market_api_key, self.market_api_secret, self.source, self.root_url)
            market_response = self.market_session.marketdata_login()
            # print(market_response)
            self.interactive_token = intractive_response.get("result", {}).get("token", "Intractive Token didn't fetched")
            self.market_token = market_response.get("result", {}).get("token", "MarketAPI Token didn't fetched")
            return self.interactive_token, self.market_token
        except:
            print(traceback.format_exc())
    
    def logout(self):
        try:
            results = {}

            if hasattr(self, "interactive_session") and self.interactive_session:
                results["interactive_logout"] = self.interactive_session.interactive_logout()
            else:
                results["interactive_logout"] = "Interactive session not initialized"

            if hasattr(self, "market_session") and self.market_session:
                results["market_logout"] = self.market_session.marketdata_logout()
            else:
                results["market_logout"] = "Market session not initialized"

            return results

        except Exception:
            print("Logout failed:\n", traceback.format_exc())
            return None

    def orderbook(self):
        return self.interactive_session.get_dealer_orderbook(self.user_id)

    def place_order(self, exch, token, tt, ot, qty, price):
        # print("inputs are ")
        # print(exch, token, tt, ot, qty, price)
        if exch == "NSEFO":
            exchange_segment = self.interactive_session.EXCHANGE_NSEFO
        elif exch == "BSEFO":
            exchange_segment = self.interactive_session.EXCHANGE_BSEFO
        
        if tt == "BUY":
            tt = self.interactive_session.TRANSACTION_TYPE_BUY
        else:
            tt = self.interactive_session.TRANSACTION_TYPE_SELL
        response = self.interactive_session.place_order(
            exchangeSegment=exchange_segment,
            exchangeInstrumentID=token,
            productType=self.interactive_session.PRODUCT_MIS,
            orderType=self.interactive_session.ORDER_TYPE_MARKET,
            orderSide=tt,
            timeInForce=self.interactive_session.VALIDITY_DAY,
            disclosedQuantity=0,
            orderQuantity=qty,
            limitPrice=price,
            stopPrice=0,
            apiOrderSource="WEB_EXE_PLATFORM",
            orderUniqueIdentifier="WEB_EXE_PLATFORM",
            clientID=self.user_id)

        print("Place Order: ", response)
        return response.get('result', {}).get('AppOrderID', response), response.get('type', 'error')
    
    def cancel_order(self, order_id):
        response = self.interactive_session.cancel_order(
            appOrderID=order_id,
            orderUniqueIdentifier='orderUniqueIdentifier',
            clientID=self.user_id)
        # print("Cancel Order: ", response)
        return response
    
    def get_master_contract(self, exchanges=['NSEFO',"NSECM", "NSECD", "MCXFO", "BSECM", "BSEFO"]):
        exchangesegments = [self.interactive_session.EXCHANGE_NSEFO, self.interactive_session.EXCHANGE_NSECM, self.interactive_session.EXCHANGE_NSECD]
        r = self.interactive_session.get_master(exchangeSegmentList=exchangesegments)
        # column_mapping = {
        #             'Name': 'symbol',
        #             'ExchangeSegment': 'exchange',
        #             'Series': 'instrument_type',
        #             'Description': 'sec_description',
        #             'ExchangeInstrumentID': 'sec_id',
        #             'ContractExpiration': 'expiry_date',
        #             'StrikePrice': 'strike_price',
        #             'OptionType': 'option_type',
        #             'LotSize': 'lot_size'
        #         }
        columns = ['exchange', 'sec_id', 'InstrumentType', 'symbol', 'sec_description',
                    'instrument_type', 'NameWithSeries', 'InstrumentID', 'PriceBand.High', 'PriceBand.Low',
                    'FreezeQty', 'TickSize', 'lot_size', 'Multiplier', 'UnderlyingInstrumentId',
                    'UnderlyingIndexName', 'expiry_date', 'strike_price', 'option_type',
                    'displayName', 'PriceNumerator', 'PriceDenominator', "Extra"]
        # print(f"{r.text=}")

        rows = [row.split("|") for row in r['result'].split('\n') if row.strip()]
        df = pd.DataFrame(rows, columns=columns)
        # print(df.head())
        df["option_type"] = df["instrument_type"]
        def transform_option_type(row):
            if row['instrument_type'] == 'FUTSTK':
                return 'FUT'
            elif row['instrument_type'] == 'OPTSTK':
                # Split display_name and check the 3rd element (index 2)
                parts = row['displayName'].split()
                if len(parts) >= 3:
                    return parts[2]  # This will be either 'CE' or 'PE'
            elif row['instrument_type'] == 'OPTIDX':
                # Split display_name and check the 3rd element (index 2)
                parts = row['displayName'].split()
                if len(parts) >= 3:
                    return parts[2] 
            return row['instrument_type']  # Default return if conditions not met

        # Apply the transformation
        df['option_type'] = df.apply(transform_option_type, axis=1)
        
        # df["expiry_date"] = pd.to_datetime(df['expiry_date']).dt.date
        df['expiry_date'] = pd.to_datetime(df['expiry_date'], errors='coerce').dt.date
        df["expiry_date"] = pd.to_datetime(df["expiry_date"], format="mixed", errors="coerce")
        # print(df.head())
        df.to_csv("kjfdkjfdkjfd.csv", index=False)
        return df
    
    def run_socket(self):
        """Function to run the socket connection in a thread."""
        try:
            self.soc.connect()
        except Exception as e:
            print(f"Socket connection error: {e}")
    
    def connect_ws(self, on_open, on_message, on_close, on_error):
        # print("hereere in XTS")
        self.soc = MDSocket_io(self.market_token, self.user_id, root_url=self.root_url)
        self.soc.on_connect = on_open
        self.soc.on_message = on_message
        self.soc.on_disconnect = on_close
        self.soc.on_error = on_error
        el = self.soc.get_emitter()
        el.on('connect', on_open)
        el.on('1512-json-full', on_message)
        # el.on_disconnect = on_close
        # el.on_error = on_error
        self.ws_thread = Thread(target=self.run_socket, daemon=True)
        self.ws_thread.start()
        # print("new thread spun")

    def subscribe(self, exch, token):
        self.market_session.send_subscription([{
            "exchangeSegment": exch,
            "exchangeInstrumentID": token
        }], 1512)

class XTSException(Exception):
    """
    Base exception class representing a XTS client exception.

    Every specific XTS client exception is a subclass of this
    and  exposes two instance variables `.code` (HTTP error code)
    and `.message` (error text).
    """

    def __init__(self, message, code=500):
        """Initialize the exception."""
        super(XTSException, self).__init__(message)
        self.code = code


class XTSGeneralException(XTSException):
    """An unclassified, general error. Default code is 500."""

    def __init__(self, message, code=500):
        """Initialize the exception."""
        super(XTSGeneralException, self).__init__(message, code)


class XTSTokenException(XTSException):
    """Represents all token and authentication related errors. Default code is 400."""

    def __init__(self, message, code=400):
        """Initialize the exception."""
        super(XTSTokenException, self).__init__(message, code)


class XTSPermissionException(XTSException):
    """Represents permission denied exceptions for certain calls. Default code is 400."""

    def __init__(self, message, code=400):
        """Initialize the exception."""
        super(XTSPermissionException, self).__init__(message, code)


class XTSOrderException(XTSException):
    """Represents all order placement and manipulation errors. Default code is 500."""

    def __init__(self, message, code=400):
        """Initialize the exception."""
        super(XTSOrderException, self).__init__(message, code)


class XTSInputException(XTSException):
    """Represents user input errors such as missing and invalid parameters. Default code is 400."""

    def __init__(self, message, code=400):
        """Initialize the exception."""
        super(XTSInputException, self).__init__(message, code)


class XTSDataException(XTSException):
    """Represents a bad response from the backend Order Management System (OMS). Default code is 500."""

    def __init__(self, message, code=500):
        """Initialize the exception."""
        super(XTSDataException, self).__init__(message, code)


class XTSNetworkException(XTSException):
    """Represents a network issue between XTS and the backend Order Management System (OMS). Default code is 500."""

    def __init__(self, message, code=500):
        """Initialize the exception."""
        super(XTSNetworkException, self).__init__(message, code)


class XTSCommon:
    """
    Base variables class
    """

    def __init__(self, token=None, userID=None, isInvestorClient=None):
        """Initialize the common variables."""
        self.token = token
        self.userID = userID
        self.isInvestorClient = isInvestorClient


class XTSConnect(XTSCommon):
    """
    The XTS Connect API wrapper class.
    In production, you may initialise a single instance of this class per `api_key`.
    """

    # Constants
    # Products
    PRODUCT_MIS = "MIS"
    PRODUCT_NRML = "NRML"

    # Order types
    ORDER_TYPE_MARKET = "MARKET"
    ORDER_TYPE_LIMIT = "LIMIT"
    ORDER_TYPE_STOPMARKET = "STOPMARKET"
    ORDER_TYPE_STOPLIMIT = "STOPLIMIT"

    # Transaction type
    TRANSACTION_TYPE_BUY = "BUY"
    TRANSACTION_TYPE_SELL = "SELL"

    # Squareoff mode
    SQUAREOFF_DAYWISE = "DayWise"
    SQUAREOFF_NETWISE = "Netwise"

    # Squareoff position quantity types
    SQUAREOFFQUANTITY_EXACTQUANTITY = "ExactQty"
    SQUAREOFFQUANTITY_PERCENTAGE = "Percentage"

    # Validity
    VALIDITY_DAY = "DAY"

    # Exchange Segments
    EXCHANGE_NSECM = "NSECM"
    EXCHANGE_NSEFO = "NSEFO"
    EXCHANGE_NSECD = "NSECD"
    EXCHANGE_MCXFO = "MCXFO"
    EXCHANGE_BSECM = "BSECM"
    EXCHANGE_BSEFO = "BSEFO"

    # URIs to various calls
    _routes = {
        # Interactive API endpoints
        "interactive.prefix": "interactive",
        "user.login": "/interactive/user/session",
        "user.logout": "/interactive/user/session",
        "user.profile": "/interactive/user/profile",
        "user.balance": "/interactive/user/balance",

        "orders": "/interactive/orders",
        "trades": "/interactive/orders/trades",
        "order.status": "/interactive/orders",
        "order.place": "/interactive/orders",
        "bracketorder.place": "/interactive/orders/bracket",
	    "bracketorder.modify": "/interactive/orders/bracket",
        "bracketorder.cancel": "/interactive/orders/bracket",
        "order.place.cover": "/interactive/orders/cover",
        "order.exit.cover": "/interactive/orders/cover",
        "order.modify": "/interactive/orders",
        "order.cancel": "/interactive/orders",
        "order.cancelall": "/interactive/orders/cancelall",
        "order.history": "/interactive/orders",

        "portfolio.positions": "/interactive/portfolio/positions",
        "portfolio.holdings": "/interactive/portfolio/holdings",
        "portfolio.positions.convert": "/interactive/portfolio/positions/convert",
        "portfolio.squareoff": "/interactive/portfolio/squareoff",
        "portfolio.dealerpositions": "interactive/portfolio/dealerpositions",
        "order.dealer.status": "/interactive/orders/dealerorderbook",
        "dealer.trades": "/interactive/orders/dealertradebook",




        # Market API endpoints
        "marketdata.prefix": "apimarketdata",
        "market.login": "/apimarketdata/auth/login",
        "market.logout": "/apimarketdata/auth/logout",

        "market.config": "/apimarketdata/config/clientConfig",

        "market.instruments.master": "/apimarketdata/instruments/master",
        "market.instruments.subscription": "/apimarketdata/instruments/subscription",
        "market.instruments.unsubscription": "/apimarketdata/instruments/subscription",
        "market.instruments.ohlc": "/apimarketdata/instruments/ohlc",
        "market.instruments.indexlist": "/apimarketdata/instruments/indexlist",
        "market.instruments.quotes": "/apimarketdata/instruments/quotes",

        "market.search.instrumentsbyid": '/apimarketdata/search/instrumentsbyid',
        "market.search.instrumentsbystring": '/apimarketdata/search/instruments',

        "market.instruments.instrument.series": "/apimarketdata/instruments/instrument/series",
        "market.instruments.instrument.equitysymbol": "/apimarketdata/instruments/instrument/symbol",
        "market.instruments.instrument.futuresymbol": "/apimarketdata/instruments/instrument/futureSymbol",
        "market.instruments.instrument.optionsymbol": "/apimarketdata/instruments/instrument/optionsymbol",
        "market.instruments.instrument.optiontype": "/apimarketdata/instruments/instrument/optionType",
        "market.instruments.instrument.expirydate": "/apimarketdata/instruments/instrument/expiryDate"
    }

    def __init__(self,
                 apiKey,
                 secretKey,
                 source,
                 root=None,
                 debug=False,
                 timeout=None,
                 pool=None,
                 disable_ssl=True):
        """
        Initialise a new XTS Connect client instance.

        - `api_key` is the key issued to you
        - `token` is the token obtained after the login flow. Pre-login, this will default to None,
        but once you have obtained it, you should persist it in a database or session to pass
        to the XTS Connect class initialisation for subsequent requests.
        - `root` is the API end point root. Unless you explicitly
        want to send API requests to a non-default endpoint, this
        can be ignored.
        - `debug`, if set to True, will serialise and print requests
        and responses to stdout.
        - `timeout` is the time (seconds) for which the API client will wait for
        a request to complete before it fails. Defaults to 7 seconds
        - `pool` is manages request pools. It takes a dict of params accepted by HTTPAdapter
        - `disable_ssl` disables the SSL verification while making a request.
        If set requests won't throw SSLError if its set to custom `root` url without SSL.
        """
        self._default_root_uri = root
        self._default_login_uri = self._default_root_uri + "/user/session"
        self._default_timeout = 7  # In seconds

        self.debug = debug
        self.apiKey = apiKey
        self.secretKey = secretKey
        self.source = source
        self.disable_ssl = disable_ssl
        self.root = root or self._default_root_uri
        self.timeout = timeout or self._default_timeout

        super().__init__()

        # Create requests session only if pool exists. Reuse session
        # for every request. Otherwise create session for each request
        if pool:
            self.reqsession = requests.Session()
            reqadapter = requests.adapters.HTTPAdapter(**pool)
            self.reqsession.mount("https://", reqadapter)
        else:
            self.reqsession = requests

        # disable requests SSL warning
        requests.packages.urllib3.disable_warnings()

    def _set_common_variables(self, access_token,userID, isInvestorClient):
        """Set the `access_token` received after a successful authentication."""
        super().__init__(access_token,userID, isInvestorClient)

    def _login_url(self):
        """Get the remote login url to which a user should be redirected to initiate the login flow."""
        return self._default_login_uri

    def interactive_login(self):
        """Send the login url to which a user should receive the token."""
        try:
            params = {
                "appKey": self.apiKey,
                "secretKey": self.secretKey,
                "source": self.source
            }
            response = self._post("user.login", params)

            if "token" in response['result']:
                self._set_common_variables(response['result']['token'], response['result']['userID'],
                                           response['result']['isInvestorClient'])
            return response
        except Exception as e:
            return response['description']

    def get_order_book(self, clientID=None):
        """Request Order book gives states of all the orders placed by an user"""
        try:
            params = {}
            if not self.isInvestorClient:
                params['clientID'] = clientID
            response = self._get("order.status", params)
            return response
        except Exception as e:
            return response['description']
		
    def get_dealer_orderbook(self, clientID=None):
        """Request Order book gives states of all the orders placed by an user"""
        try:
            params = {}
            if not self.isInvestorClient:
                params['clientID'] = clientID
            response = self._get("order.dealer.status", params)
            return response
        except Exception as e:
            return response['description']


    def place_order(self,
                    exchangeSegment,
                    exchangeInstrumentID,
                    productType,
                    orderType,
                    orderSide,
                    timeInForce,
                    disclosedQuantity,
                    orderQuantity,
                    limitPrice,
                    stopPrice,
                    orderUniqueIdentifier,
                    apiOrderSource,
                    clientID=None
                    ):
        """To place an order"""
        try:

            params = {
                "exchangeSegment": exchangeSegment,
                "exchangeInstrumentID": exchangeInstrumentID,
                "productType": productType,
                "orderType": orderType,
                "orderSide": orderSide,
                "timeInForce": timeInForce,
                "disclosedQuantity": disclosedQuantity,
                "orderQuantity": orderQuantity,
                "limitPrice": limitPrice,
                "stopPrice": stopPrice,
                "apiOrderSource":apiOrderSource,
                "orderUniqueIdentifier": orderUniqueIdentifier
            }

            if not self.isInvestorClient:
                params['clientID'] = clientID

            response = self._post('order.place', json.dumps(params))
            return response
        except Exception as e:
            print(traceback.format_exc())
            return response['description']

    def modify_order(self,
                     appOrderID,
                     modifiedProductType,
                     modifiedOrderType,
                     modifiedOrderQuantity,
                     modifiedDisclosedQuantity,
                     modifiedLimitPrice,
                     modifiedStopPrice,
                     modifiedTimeInForce,
                     orderUniqueIdentifier,
                     clientID=None
                     ):
        """The facility to modify your open orders by allowing you to change limit order to market or vice versa,
        change Price or Quantity of the limit open order, change disclosed quantity or stop-loss of any
        open stop loss order. """
        try:
            appOrderID = int(appOrderID)
            params = {
                'appOrderID': appOrderID,
                'modifiedProductType': modifiedProductType,
                'modifiedOrderType': modifiedOrderType,
                'modifiedOrderQuantity': modifiedOrderQuantity,
                'modifiedDisclosedQuantity': modifiedDisclosedQuantity,
                'modifiedLimitPrice': modifiedLimitPrice,
                'modifiedStopPrice': modifiedStopPrice,
                'modifiedTimeInForce': modifiedTimeInForce,
                'orderUniqueIdentifier': orderUniqueIdentifier
            }

            if not self.isInvestorClient:
                params['clientID'] = clientID

            response = self._put('order.modify', json.dumps(params))
            return response
        except Exception as e:
            return response['description']


        
    def place_bracketorder(self,
                    exchangeSegment,
                    exchangeInstrumentID,
                    orderType,
                    orderSide,
                    disclosedQuantity,
                    orderQuantity,
                    limitPrice,
                    squarOff,
                    stopLossPrice,
	                trailingStoploss,
                    isProOrder,
                    apiOrderSource,
                    orderUniqueIdentifier,
                     ):
        """To place a bracketorder"""
        try:

            params = {
                "exchangeSegment": exchangeSegment,
                "exchangeInstrumentID": exchangeInstrumentID,
                "orderType": orderType,
                "orderSide": orderSide,
                "disclosedQuantity": disclosedQuantity,
                "orderQuantity": orderQuantity,
                "limitPrice": limitPrice,
                "squarOff": squarOff,
                "stopLossPrice": stopLossPrice,
                "trailingStoploss": trailingStoploss,
                "isProOrder": isProOrder,
                "apiOrderSource":apiOrderSource,
                "orderUniqueIdentifier": orderUniqueIdentifier
            }
            response = self._post('bracketorder.place', json.dumps(params))
            # print(response)
            return response
        except Exception as e:
            return response['description']

    def bracketorder_cancel(self, appOrderID, clientID=None):
        """This API can be called to cancel any open order of the user by providing correct appOrderID matching with
        the chosen open order to cancel. """
        try:
            params = {'boEntryOrderId': int(appOrderID)}
            if not self.isInvestorClient:
                params['clientID'] = clientID
            response = self._delete('bracketorder.cancel', params)
            return response
        except Exception as e:
            return response['description']   

    def modify_bracketorder(self,
                     appOrderID,
                     orderQuantity,
                     limitPrice,
                     stopPrice,
                     clientID=None
                     ):
        try:
            appOrderID = int(appOrderID)
            params = {
                'appOrderID': appOrderID,
                'bracketorder.modify': orderQuantity,
                'limitPrice': limitPrice,
                'stopPrice': stopPrice
            }

            if not self.isInvestorClient:
                params['clientID'] = clientID

            response = self._put('bracketorder.modify', json.dumps(params))
            return response
        except Exception as e:
            return response['description']


    def place_cover_order(self, 
                          exchangeSegment, 
                          exchangeInstrumentID, 
                          orderSide,orderType, 
                          orderQuantity, 
                          disclosedQuantity,
                          limitPrice, 
                          stopPrice, 
                          apiOrderSource,
                          orderUniqueIdentifier, 
                          clientID=None):
        """A Cover Order is an advance intraday order that is accompanied by a compulsory Stop Loss Order. This helps
        users to minimize their losses by safeguarding themselves from unexpected market movements. A Cover Order
        offers high leverage and is available in Equity Cash, Equity F&O, Commodity F&O and Currency F&O segments. It
        has 2 orders embedded in itself, they are Limit/Market Order Stop Loss Order """
        try:

            params = {'exchangeSegment': exchangeSegment, 
                      'exchangeInstrumentID': exchangeInstrumentID,
                      'orderSide': orderSide, 
                      "orderType": orderType,
                      'orderQuantity': orderQuantity, 
                      'disclosedQuantity': disclosedQuantity,
                      'limitPrice': limitPrice, 
                      'stopPrice': stopPrice, 
                      'apiOrderSource': apiOrderSource,
                      'orderUniqueIdentifier': orderUniqueIdentifier
                      }
            if not self.isInvestorClient:
                params['clientID'] = clientID
            response = self._post('order.place.cover', json.dumps(params))
            return response
        except Exception as e:
            return response['description']

    def exit_cover_order(self, appOrderID, clientID=None):
        """Exit Cover API is a functionality to enable user to easily exit an open stoploss order by converting it
        into Exit order. """
        try:

            params = {'appOrderID': appOrderID}
            if not self.isInvestorClient:
                params['clientID'] = clientID
            response = self._put('order.exit.cover', json.dumps(params))
            return response
        except Exception as e:
            return response['description']



    def get_profile(self, clientID=None):
        """Using session token user can access his profile stored with the broker, it's possible to retrieve it any
        point of time with the http: //ip:port/interactive/user/profile API. """
        try:
            params = {}
            if not self.isInvestorClient:
                params['clientID'] = clientID

            response = self._get('user.profile', params)
            return response
        except Exception as e:
            return response['description']

    def get_balance(self, clientID=None):
        """Get Balance API call grouped under this category information related to limits on equities, derivative,
        upfront margin, available exposure and other RMS related balances available to the user."""
        if self.isInvestorClient:
            try:
                params = {}
                if not self.isInvestorClient:
                    params['clientID'] = clientID
                response = self._get('user.balance', params)
                return response
            except Exception as e:
                return response['description']
        else:
            print("Balance : Balance API available for retail API users only, dealers can watch the same on dealer "
                  "terminal")


    def get_trade(self, clientID=None):
        """Trade book returns a list of all trades executed on a particular day , that were placed by the user . The
        trade book will display all filled and partially filled orders. """
        try:
            params = {}
            if not self.isInvestorClient:
                params['clientID'] = clientID
            response = self._get('trades', params)
            return response
        except Exception as e:
            return response['description']

    def get_dealer_tradebook(self, clientID=None):
        """Trade book returns a list of all trades executed on a particular day , that were placed by the user . The
        trade book will display all filled and partially filled orders. """
        try:
            params = {}
            if not self.isInvestorClient:
                params['clientID'] = clientID
            response = self._get('dealer.trades', params)
            return response
        except Exception as e:
            return response['description']
		
    def get_holding(self, clientID=None):
        """Holdings API call enable users to check their long term holdings with the broker."""
        try:
            params = {}
            if not self.isInvestorClient:
                params['clientID'] = clientID

            response = self._get('portfolio.holdings', params)
            return response
        except Exception as e:
            return response['description']


    def get_dealerposition_netwise(self, clientID=None):
        """The positions API positions by net. Net is the actual, current net position portfolio."""
        try:
            params = {'dayOrNet': 'NetWise'}
            if not self.isInvestorClient:
                params['clientID'] = clientID
            response = self._get('portfolio.dealerpositions', params)
            return response
        except Exception as e:
            return response['description']


           
    def get_dealerposition_daywise(self, clientID=None):
        """The positions API returns positions by day, which is a snapshot of the buying and selling activity for
        that particular day."""
        try:
            params = {'dayOrNet': 'DayWise'}
            if not self.isInvestorClient:
                params['clientID'] = clientID

            response = self._get('portfolio.dealerpositions', params)
            return response
        except Exception as e:
            return response['description']
		
    def get_position_daywise(self, clientID=None):
	    
        """The positions API returns positions by day, which is a snapshot of the buying and selling activity for
        that particular day."""
        try:
            params = {'dayOrNet': 'DayWise'}
            if not self.isInvestorClient:
                params['clientID'] = clientID

            response = self._get('portfolio.positions', params)
            return response
        except Exception as e:
            return response['description']

    def get_position_netwise(self, clientID=None):
        """The positions API positions by net. Net is the actual, current net position portfolio."""
        try:
            params = {'dayOrNet': 'NetWise'}
            if not self.isInvestorClient:
                params['clientID'] = clientID
            response = self._get('portfolio.positions', params)
            return response
        except Exception as e:
            return response['description']

    def convert_position(self, exchangeSegment, exchangeInstrumentID, targetQty, isDayWise, oldProductType,
                         newProductType, clientID=None):
        """Convert position API, enable users to convert their open positions from NRML intra-day to Short term MIS or
        vice versa, provided that there is sufficient margin or funds in the account to effect such conversion """
        try:
            params = {
                'exchangeSegment': exchangeSegment,
                'exchangeInstrumentID': exchangeInstrumentID,
                'targetQty': targetQty,
                'isDayWise': isDayWise,
                'oldProductType': oldProductType,
                'newProductType': newProductType
            }
            if not self.isInvestorClient:
                params['clientID'] = clientID
            response = self._put('portfolio.positions.convert', json.dumps(params))
            return response
        except Exception as e:
            return response['description']

    def cancel_order(self, appOrderID, orderUniqueIdentifier, clientID=None):
        """This API can be called to cancel any open order of the user by providing correct appOrderID matching with
        the chosen open order to cancel. """
        try:
            params = {'appOrderID': int(appOrderID), 'orderUniqueIdentifier': orderUniqueIdentifier}
            if not self.isInvestorClient:
                params['clientID'] = clientID
            response = self._delete('order.cancel', params)
            return response
        except Exception as e:
            return response['description']
        
    def cancelall_order(self, exchangeSegment, exchangeInstrumentID):
        """This API can be called to cancel all open order of the user by providing exchange segment and exchange instrument ID """
        try:
            params = {"exchangeSegment": exchangeSegment, "exchangeInstrumentID": exchangeInstrumentID}
            if not self.isInvestorClient:
                params['clientID'] = self.userID
            response = self._post('order.cancelall', json.dumps(params))
            return response
        except Exception as e:
            return response['description']    


    def squareoff_position(self, exchangeSegment, exchangeInstrumentID, productType, squareoffMode,
                           positionSquareOffQuantityType, squareOffQtyValue, blockOrderSending, cancelOrders,
                           clientID=None):
        """User can request square off to close all his positions in Equities, Futures and Option. Users are advised
        to use this request with caution if one has short term holdings. """
        try:

            params = {'exchangeSegment': exchangeSegment, 'exchangeInstrumentID': exchangeInstrumentID,
                      'productType': productType, 'squareoffMode': squareoffMode,
                      'positionSquareOffQuantityType': positionSquareOffQuantityType,
                      'squareOffQtyValue': squareOffQtyValue, 'blockOrderSending': blockOrderSending,
                      'cancelOrders': cancelOrders
                      }
            if not self.isInvestorClient:
                params['clientID'] = clientID
            response = self._put('portfolio.squareoff', json.dumps(params))
            return response
        except Exception as e:
            return response['description']

    def get_order_history(self, appOrderID, clientID=None):
        """Order history will provide particular order trail chain. This indicate the particular order & its state
        changes. i.e.Pending New to New, New to PartiallyFilled, PartiallyFilled, PartiallyFilled & PartiallyFilled
        to Filled etc """
        try:
            params = {'appOrderID': appOrderID}
            if not self.isInvestorClient:
                params['clientID'] = clientID
            response = self._get('order.history', params)
            return response
        except Exception as e:
            return response['description']

    def interactive_logout(self, clientID=None):
        """This call invalidates the session token and destroys the API session. After this, the user should go
        through login flow again and extract session token from login response before further activities. """
        try:
            params = {}
            if not self.isInvestorClient:
                params['clientID'] = clientID
            response = self._delete('user.logout', params)
            return response
        except Exception as e:
            return response['description']

########################################################################################################
# Market data API
########################################################################################################

    def marketdata_login(self):
        try:
            params = {
                "appKey": self.apiKey,
                "secretKey": self.secretKey,
                "source": self.source
            }
            response = self._post("market.login", params)

            if "token" in response['result']:
                self._set_common_variables(response['result']['token'], response['result']['userID'],False)
            return response
        except Exception as e:
            return response['description']

    def get_config(self):
        try:
            params = {}
            response = self._get('market.config', params)
            return response
        except Exception as e:
            return response['description']

    def get_quote(self, Instruments, xtsMessageCode, publishFormat):
        try:

            params = {'instruments': Instruments, 'xtsMessageCode': xtsMessageCode, 'publishFormat': publishFormat}
            response = self._post('market.instruments.quotes', json.dumps(params))
            return response
        except Exception as e:
            return response['description']

    def send_subscription(self, Instruments, xtsMessageCode):
        try:
            params = {'instruments': Instruments, 'xtsMessageCode': xtsMessageCode}
            response = self._post('market.instruments.subscription', json.dumps(params))
            return response
        except Exception as e:
            return response['description']

    def send_unsubscription(self, Instruments, xtsMessageCode):
        try:
            params = {'instruments': Instruments, 'xtsMessageCode': xtsMessageCode}
            response = self._put('market.instruments.unsubscription', json.dumps(params))
            return response
        except Exception as e:
            return response['description']

    def get_master(self, exchangeSegmentList):
        try:
            params = {"exchangeSegmentList": exchangeSegmentList}
            response = self._post('market.instruments.master', json.dumps(params))
            return response
        except Exception as e:
            return response['description']

    def get_ohlc(self, exchangeSegment, exchangeInstrumentID, startTime, endTime, compressionValue):
        try:
            params = {
                'exchangeSegment': exchangeSegment,
                'exchangeInstrumentID': exchangeInstrumentID,
                'startTime': startTime,
                'endTime': endTime,
                'compressionValue': compressionValue}
            response = self._get('market.instruments.ohlc', params)
            return response
        except Exception as e:
            return response['description']

    def get_series(self, exchangeSegment):
        try:
            params = {'exchangeSegment': exchangeSegment}
            response = self._get('market.instruments.instrument.series', params)
            return response
        except Exception as e:
            return response['description']

    def get_equity_symbol(self, exchangeSegment, series, symbol):
        try:

            params = {'exchangeSegment': exchangeSegment, 'series': series, 'symbol': symbol}
            response = self._get('market.instruments.instrument.equitysymbol', params)
            return response
        except Exception as e:
            return response['description']

    def get_expiry_date(self, exchangeSegment, series, symbol):
        try:
            params = {'exchangeSegment': exchangeSegment, 'series': series, 'symbol': symbol}
            response = self._get('market.instruments.instrument.expirydate', params)
            return response
        except Exception as e:
            return response['description']

    def get_future_symbol(self, exchangeSegment, series, symbol, expiryDate):
        try:
            params = {'exchangeSegment': exchangeSegment, 'series': series, 'symbol': symbol, 'expiryDate': expiryDate}
            response = self._get('market.instruments.instrument.futuresymbol', params)
            return response
        except Exception as e:
            return response['description']

    def get_option_symbol(self, exchangeSegment, series, symbol, expiryDate, optionType, strikePrice):
        try:
            params = {'exchangeSegment': exchangeSegment, 'series': series, 'symbol': symbol, 'expiryDate': expiryDate,
                      'optionType': optionType, 'strikePrice': strikePrice}
            response = self._get('market.instruments.instrument.optionsymbol', params)
            return response
        except Exception as e:
            return response['description']

    def get_option_type(self, exchangeSegment, series, symbol, expiryDate):
        try:
            params = {'exchangeSegment': exchangeSegment, 'series': series, 'symbol': symbol, 'expiryDate': expiryDate}
            response = self._get('market.instruments.instrument.optiontype', params)
            return response
        except Exception as e:
            return response['description']

    def get_index_list(self, exchangeSegment):
        try:
            params = {'exchangeSegment': exchangeSegment}
            response = self._get('market.instruments.indexlist', params)
            return response
        except Exception as e:
            return response['description']

    def search_by_instrumentid(self, Instruments):
        try:
            params = {'source': self.source, 'instruments': Instruments}
            response = self._post('market.search.instrumentsbyid', json.dumps(params))
            return response
        except Exception as e:
            return response['description']

    def search_by_scriptname(self, searchString):
        try:
            params = {'searchString': searchString}
            response = self._get('market.search.instrumentsbystring', params)
            return response
        except Exception as e:
            return response['description']

    def marketdata_logout(self):
        try:
            params = {}
            response = self._delete('market.logout', params)
            return response
        except Exception as e:
            return response['description']

    ########################################################################################################
    # Common Methods
    ########################################################################################################

    def _get(self, route, params=None):
        """Alias for sending a GET request."""
        return self._request(route, "GET", params)

    def _post(self, route, params=None):
        """Alias for sending a POST request."""
        return self._request(route, "POST", params)

    def _put(self, route, params=None):
        """Alias for sending a PUT request."""
        return self._request(route, "PUT", params)

    def _delete(self, route, params=None):
        """Alias for sending a DELETE request."""
        return self._request(route, "DELETE", params)

    def _request(self, route, method, parameters=None):
        """Make an HTTP request."""
        params = parameters if parameters else {}

        # Form a restful URL
        uri = self._routes[route].format(params)
        url = parse.urljoin(self.root, uri)
        headers = {}

        if self.token:
            # set authorization header
            headers.update({'Content-Type': 'application/json', 'Authorization': self.token})

        try:
            r = self.reqsession.request(method,
                                        url,
                                        data=params if method in ["POST", "PUT"] else None,
                                        params=params if method in ["GET", "DELETE"] else None,
                                        headers=headers,
                                        verify=not self.disable_ssl)

        except Exception as e:
            raise e

        if self.debug:
            log.debug("Response: {code} {content}".format(code=r.status_code, content=r.content))

        # Validate the content type.
        if "json" in r.headers["content-type"]:
            try:
                data = json.loads(r.content.decode("utf8"))
            except ValueError:
                raise XTSDataException("Couldn't parse the JSON response received from the server: {content}".format(
                    content=r.content))

            # api error
            if data.get("type"):

                if r.status_code == 400 and data["type"] == "error" and data["description"] == "Invalid Token":
                    raise XTSTokenException(data["description"])

                if r.status_code == 400 and data["type"] == "error" and data["description"] == "Bad Request":
                    message = "Description: " + data["description"] + " errors: " + str(data['result']["errors"])
                    raise XTSInputException(str(message))

            return data
        else:
            raise XTSDataException("Unknown Content-Type ({content_type}) with response: ({content})".format(
                content_type=r.headers["content-type"],
                content=r.content))


class OrderSocket_io(socketio.Client):
    """A Socket.IO client.
    This class implements a fully compliant Socket.IO web client with support
    for websocket and long-polling transports.
    :param reconnection: 'True'. if the client should automatically attempt to
                         reconnect to the server after an interruption, or
                         'False' to not reconnect. The default is 'True'.
    :param reconnection_attempts: How many reconnection attempts to issue
                                  before giving up, or 0 for infinity attempts.
                                  The default is 0.
    :param reconnection_delay: How long to wait in seconds before the first
                               reconnection attempt. Each successive attempt
                               doubles this delay.
    :param reconnection_delay_max: The maximum delay between reconnection
                                   attempts.
    :param randomization_factor: Randomization amount for each delay between
                                 reconnection attempts. The default is 0.5,
                                 which means that each delay is randomly
                                 adjusted by +/- 50%.
    :param logger: To enable logging set to 'True' or pass a logger object to
                   use. To disable logging set to 'False'. The default is
                   'False'.
    :param binary: 'True' to support binary payloads, 'False' to treat all
                   payloads as text. On Python 2, if this is set to 'True',
                   'unicode' values are treated as text, and 'str' and
                   'bytes' values are treated as binary.  This option has no
                   effect on Python 3, where text and binary payloads are
                   always automatically discovered.
    :param json: An alternative json module to use for encoding and decoding
                 packets. Custom json modules must have 'dumps' and 'loads'
                 functions that are compatible with the standard library
                 versions.
    """

    def __init__(self, token, userID, reconnection=True, reconnection_attempts=0, reconnection_delay=1,
                 reconnection_delay_max=50000, randomization_factor=0.5, logger=False, binary=False, json=None,
                 root_url=None, **kwargs):
        self.sid = socketio.Client(logger=True, engineio_logger=True)
        self.eventlistener = self.sid
        self.sid.on('connect', self.on_connect)
        self.sid.on('message', self.on_message)
        self.sid.on('joined', self.on_joined)
        self.sid.on('error', self.on_error)
        self.sid.on('order', self.on_order)
        self.sid.on('trade', self.on_trade)
        self.sid.on('position', self.on_position)
        self.sid.on('tradeConversion', self.on_tradeconversion)
        self.sid.on('logout', self.on_messagelogout)
        self.sid.on('disconnect', self.on_disconnect)

        self.userID = userID
        self.token = token

        self.port = root_url
        port = f'{self.port}/?token='

        self.connection_url = port + self.token + '&userID=' + self.userID + "&apiType=INTERACTIVE"

    def connect(self, headers={}, transports='websocket', namespaces=None, socketio_path='/interactive/socket.io',
                verify=False):
        """Connect to a Socket.IO server.
        :param url: The URL of the Socket.IO server. It can include custom
                    query string parameters if required by the server.
        :param headers: A dictionary with custom headers to send with the
                        connection request.
        :param transports: The list of allowed transports. Valid transports
                           are 'polling' and 'websocket'. If not
                           given, the polling transport is connected first,
                           then an upgrade to websocket is attempted.
        :param namespaces: The list of custom namespaces to connect, in
                           addition to the default namespace. If not given,
                           the namespace list is obtained from the registered
                           event handlers.
        :param socketio_path: The endpoint where the Socket.IO server is
                              installed. The default value is appropriate for
                              most cases.

        """
        """Connect to the socket."""
        url = self.connection_url

        """Connected to the socket."""
        self.sid.connect(url, headers, transports, namespaces, socketio_path)
        self.sid.wait()
        """Disconnect from the socket."""
        # self.sid.disconnect()

    def on_connect(self):
        """Connect from the socket"""
        print('Interactive socket connected successfully!')

    def on_message(self):
        """On message from socket"""
        print('I received a message!')

    def on_joined(self, data):
        """On socket joined"""
        print('Interactive socket joined successfully!' + data)

    def on_error(self, data):
        """On receiving error from socket"""
        print('Interactive socket error!' + data)

    def on_order(self, data):
        """On receiving order placed data from socket"""
        print("Order placed!" + data)

    def on_trade(self, data):
        """On receiving trade data from socket"""
        print("Trade Received!" + data)

    def on_position(self, data):
        """On receiving position data from socket"""
        print("Position Retrieved!" + data)

    def on_tradeconversion(self, data):
        """On receiving trade conversion data from socket"""
        print("Trade Conversion Received!" + data)

    def on_messagelogout(self, data):
        """On receiving user logout message"""
        print("User logged out!" + data)

    def on_disconnect(self):
        """On receiving disconnection from socket"""
        print('Interactive Socket disconnected!')

    def get_emitter(self):
        """For getting event listener"""
        return self.eventlistener


class MDSocket_io(socketio.Client):
    """A Socket.IO client.
    This class implements a fully compliant Socket.IO web client with support
    for websocket and long-polling transports.
    :param reconnection: 'True'. if the client should automatically attempt to
                         reconnect to the server after an interruption, or
                         'False' to not reconnect. The default is 'True'.
    :param reconnection_attempts: How many reconnection attempts to issue
                                  before giving up, or 0 for infinity attempts.
                                  The default is 0.
    :param reconnection_delay: How long to wait in seconds before the first
                               reconnection attempt. Each successive attempt
                               doubles this delay.
    :param reconnection_delay_max: The maximum delay between reconnection
                                   attempts.
    :param randomization_factor: Randomization amount for each delay between
                                 reconnection attempts. The default is 0.5,
                                 which means that each delay is randomly
                                 adjusted by +/- 50%.
    :param logger: To enable logging set to 'True' or pass a logger object to
                   use. To disable logging set to 'False'. The default is
                   'False'.
    :param binary: 'True' to support binary payloads, 'False' to treat all
                   payloads as text. On Python 2, if this is set to 'True',
                   'unicode' values are treated as text, and 'str' and
                   'bytes' values are treated as binary.  This option has no
                   effect on Python 3, where text and binary payloads are
                   always automatically discovered.
    :param json: An alternative json module to use for encoding and decoding
                 packets. Custom json modules must have 'dumps' and 'loads'
                 functions that are compatible with the standard library
                 versions.
    """

    def __init__(self, token, userID, reconnection=True, reconnection_attempts=0, reconnection_delay=1,
                 reconnection_delay_max=50000, randomization_factor=0.5, logger=False, binary=False, json=None,
                 root_url=None, **kwargs):
        self.sid = socketio.Client(logger=False, engineio_logger=False)
        self.eventlistener = self.sid

        self.sid.on('connect', self.on_connect)
        self.sid.on('message', self.on_message)

        """Similarly implement partial json full and binary json full."""
        self.sid.on('1501-json-full', self.on_message1501_json_full)
        self.sid.on('1501-json-partial', self.on_message1501_json_partial)

        self.sid.on('1502-json-full', self.on_message1502_json_full)
        self.sid.on('1502-json-partial', self.on_message1502_json_partial)

        self.sid.on('1505-json-full', self.on_message1505_json_full)
        self.sid.on('1505-json-partial', self.on_message1505_json_partial)


        self.sid.on('1510-json-full', self.on_message1510_json_full)
        self.sid.on('1510-json-partial', self.on_message1510_json_partial)

        self.sid.on('1512-json-full', self.on_message1512_json_full)
        self.sid.on('1512-json-partial', self.on_message1512_json_partial)

        self.sid.on('disconnect', self.on_disconnect)

        self.port = root_url
        self.userID = userID
        publishFormat = 'JSON'
        self.broadcastMode = "Full"
        self.token = token

        port = f'{self.port}/?token='

        self.connection_url = port + token + '&userID=' + self.userID + '&publishFormat=' + publishFormat + '&broadcastMode=' + self.broadcastMode

    def connect(self, headers={}, transports='websocket', namespaces=None, socketio_path='/apimarketdata/socket.io',
                verify=False):
        """Connect to a Socket.IO server.
        :param verify: Verify SSL
        :param url: The URL of the Socket.IO server. It can include custom
                    query string parameters if required by the server.
        :param headers: A dictionary with custom headers to send with the
                        connection request.
        :param transports: The list of allowed transports. Valid transports
                           are 'polling' and 'websocket'. If not
                           given, the polling transport is connected first,
                           then an upgrade to websocket is attempted.
        :param namespaces: The list of custom namespaces to connect, in
                           addition to the default namespace. If not given,
                           the namespace list is obtained from the registered
                           event handlers.
        :param socketio_path: The endpoint where the Socket.IO server is
                              installed. The default value is appropriate for
                              most cases.

        self.url = self.connection_url
        self.connection_headers = headers
        self.connection_transports = transports
        self.connection_namespaces = namespaces
        self.socketio_path = socketio_path
        
        Connect to the socket.
        """
        url = self.connection_url
        """Connected to the socket."""
        self.sid.connect(url, headers, transports, namespaces, socketio_path)
        self.sid.wait()
        """Disconnected from the socket."""
        # self.sid.disconnect()

    def on_connect(self):
        """Connect from the socket."""
        print('Market Data Socket connected successfully!')

    def on_message(self, data):
        """On receiving message"""
        print('I received a message!' + data)

    def on_message1502_json_full(self, data):
        """On receiving message code 1502 full"""
        print('I received a 1502 Market depth message!' + data)
            
    def on_message1512_json_full(self, data):
            """On receiving message code 1512 full"""
            print('I received a 1512 LTP message!' + data)     

    def on_message1505_json_full(self, data):
        """On receiving message code 1505 full"""
        print('I received a 1505 Candle data message!' + data)

    def on_message1510_json_full(self, data):
        """On receiving message code 1510 full"""
        print('I received a 1510 Open interest message!' + data)

    def on_message1501_json_full(self, data):
        """On receiving message code 1501 full"""
        print('I received a 1501 Level1,Touchline message!' + data)

    def on_message1502_json_partial(self, data):
        """On receiving message code 1502 partial"""
        print('I received a 1502 partial message!' + data)
    
    def on_message1512_json_partial(self, data):
        """On receiving message code 1512 partial"""
        print('I received a 1512 LTP message!' + data)

    def on_message1505_json_partial(self, data):
        """On receiving message code 1505 partial"""
        print('I received a 1505 Candle data message!' + data)

    def on_message1510_json_partial(self, data):
        """On receiving message code 1510 partial"""
        print('I received a 1510 Open interest message!' + data)

    def on_message1501_json_partial(self, data):
        """On receiving message code 1501 partial"""
        now = datetime.now()
        today = now.strftime("%H:%M:%S")
        print(today, 'in main 1501 partial Level1,Touchline message!' + data + ' \n')

    def on_disconnect(self):
        """Disconnected from the socket"""
        print('Market Data Socket disconnected!')

    def on_error(self, data):
        """Error from the socket"""
        print('Market Data Error', data)

    def get_emitter(self):
        """For getting the event listener"""
        return self.eventlistener
