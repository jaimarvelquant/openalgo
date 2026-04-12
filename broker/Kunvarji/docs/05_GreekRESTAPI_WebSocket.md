 
 
 
 
 
 
 
 
 
Trading Disclaimer  
No offer or solicitation to buy or sell securities, securities derivative or futures products of any kind, or any  type of 
trading or investment advice, recommendation or strategy, is made, given or in any manner  endorsed by 
GREESOFT TECHNOLOGIES PVT.LTD.  Past performance, whether actual or indicated by historical tests of  
strategies, is no guarantee of future performance or success. Active trading is gene rally not appropriate for  
someone of limited resources, limited investment or trading experience, or low -risk tolerance, or who does  not 
have capital to risk. There is a risk of loss in stock and futures trading . Under no circumstance GREESOFT 
TECHNOLOGIES  PVT.LTD. shall be held liable or is not liable to indemnify the user for any loss or damage 
directly or indirectly, special or consequential arising out of use of the software. The user shall assume total risk 
and responsibility for use of  software . Marke t data may be delayed or  unavailable at times due to system and 
software errors, Internet traffic, outages and other factors. Computer hardware & software settings are complex in 
nature we cannot guarantee that our software will work in all permutations & combinations.  Trading  carries a high 
level of risk and may not be suitable for all investors. There is a possibility that you may  sustain a loss equal to or 
greater than your entire investment; therefore, you should not invest or risk money  that you cannot  afford to lose. 
You should be aware of all risks associated with trading.  
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
Introducing   Greek -RESTAP I  
 
GREEK Rest -API is a REST based HTTP APIs . Our REST API’s will help you to develop your 
own trading and investment platform and integrate with our Trading system. Using our REST 
API you can execute orders in real time, monitor your positions, manage your 
portfol io  stream live market data over WebSockets, and more.  
Requests & Responses can be in  JSON or BASE64 form (apart from a c ouple exceptions) .  
 
 Authorization  
 
Sessiontoken url   : http://182.76.70.89:3001/auth/greek/sessiontoken   
Request Type  : Post  
This is used to get the session -Token that is used for authorization in the REST API Server 
requests.  
 
Request  :  
 
 
 
 
 
Response :  
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 API Server Commands  
 
 
  { 
    "username": "REST",  
    "password": "rest@123",  
    "validFor": "1d"  
  } 
 
  { 
    "id": 162,  
    "sessionToken": 
"eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MTYyLCJnc2NpZCI6IlJFU1QiLCJicm9rZXIi
OiJTaWx2ZXJfU3RyZWFtIiwibWVzc2FnZV9yYXRlIjoyMDAwMCwiaWF0IjoxNjkzNDY1MzY0L
CJleHAiOjE2OTM1NTE3NjQsImlzcyI6ImF1dGgwIn0.DVrbWlrrFJfQm2mHEF2ys5O_lWuQ5T3
KIKJs9i z1fFJmuSHr -RApS -LFGS -IN2IHbm -
z5CCXIrvOuxDykQQXVXA6k4P9FGhKi1KbjLGYP8v7l181nLHjmVlybUM1rTAcWUQ3jqwZvTY
B8ANp_Ly9NkFOyn1dCt3SknBsiRJZtdXTqQ28b3zv6zybm -
AsZB_JPgLVgWoJRxiCQK7k9knBrzGBeYS9iOf_H_hIj9FU4A5JsqtQl4AOpR47G9hUHHlaAjB90s
f26lBqZ4i9oypRRPAfs3XWJv1wtvSCWN WhsLtnLonWc0ibmr8YQa88yz3EWz3bQWl8r9OXPz
6PR8EU5Al1luYTcPqBvc0aDb63jO0N9CJOqOFvgDVjOQR5FANZlBz0qLeDZb5yU8AfkULsjdV
X3zQcTIBVw_      q0XUBGGcbousDOxmoR -
sbDOZWKlYJ4UWbdwUhBqzhh2cPLBbO_wBql1935vRh -     
mrIYDGaI7QWhgUFrwVlN7adRokxFiaSt"  
  } 
 
 
 Interactive Websocket  ( Iris ) 
 
1. Websocket Login R equest : 
After creating  interactive websocket send  login request  in below format :  
Request :  
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
Response :  
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
  { 
    "request": {  
      "data": {  
        "gscid": "REST",  
        "gcid": 34,  
        "sessionId": "$2a$10$q74i4JT8VePI8ajLc5bWCu",  
        "device_type": "0"  
      }, 
      "response_format": "json",  
      "request_type": "subscribe",  
      "streaming_type": "login"  
    } 
  } 
  
 { 
    "response": {  
      "svcName": "login",  
      "serverTime": "1694599075000",  
      "infoID": "0",  
      "streaming_type": "LoginResponse",  
      "data": {  
        "error_code": "0",  
        "gscid": "UkVTVA==",  
        "gcid": "34",  
        "reconnect": "1",  
        "logtime": "1694596621"  
      }, 
      "appID": "bc90bb525bc9739a9595bb9e176dab17"  
    } 
  } 
 
 
 
2. Websocket Heartbeat R equest  : 
Send heartbeat request in every interval  (seconds) received in flag values request.  
Request :  
 
 
 
 
 
 
 
 
 
Response :  
 
 
 
 
 
 
 
 
 
 
 
 
 
  { 
    "request": {  
      "data": {  
        "gcid": "REST",  
        "sessionId": "$2a$10$q74i4JT8VePI8ajLc5bWCu"  
      }, 
      "response_format": "json",  
      "request_type": "subscribe",  
      "streaming_type": "HeartBeat"  
    } 
  } 
  { 
    "response": {  
      "svcName": "login",  
      "streaming_type": "HeartBeat",  
      "data": {  
        "curr_time": "1694599075",  
        "error_code": "0",  
        "gcid": "34",  
        "apptype": "0"  
      }, 
      "appID": "bc90bb525bc9739a9595bb9e176dab17"  
    } 
  } 
 
3. Place Order/trade request through REST or W ebsocket and Receive 
Response  . 
Place Order Request :  
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
  { 
    "request": {  
      "data": {  
        "gtoken": "102036187",  
        "side": "1",  
        "gcid": "20",  
        "price": "18500",  
        "iprocli": "0",  
        "order_type": "1",  
        "qty": "50"  
      }, 
      "response_format": "json",  
      "request_type": "subscribe",  
      "streaming_type": "NewOrderReques t" 
    } 
  } 
 
Response  is received in Websocket.  
Response :  
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
  { 
    "response": {  
      "svcName": "order",  
      "serverTime": "1685016746000",  
      "infoID": "0",  
      "streaming_type": "OrderResponse",  
      "data": {  
        "side": "1",  
        "qty": "50",  
        "product": "0",  
        "gtoken": "102036187",  
        "order_status": "Pending",  
        "eorderid": "1000000000101012",  
        "gorderid": "120140064",  
        "lu_time_exchange": "1369503632",  
        "lu_time": "1685016632",  
        "symbol": "NIFTY 25MAY23",  
        "regular_lot": "50",  
        "validity": "8",  
        "order_type": "1",  
        "price": "18500.00",  
        "order_state": "0",  
        "trigger_price": "0.00",  
        "disclosed_qty": " 0", 
        "code": "0",  
        "reason": "",  
        "pending_qty": "50",  
        "pending_disclosed_qty": "0",  
        "qty_filled_today": "0",  
        "goodTillDate": "0",  
        "cancelledBy": "",  
        "expiryDate": "1685005200",  
        "tradeSymbol": "NIFTY",  
        "instrument": "FUTIDX",  
        "optionType": "XX",  
        "strikePrice": "0.00"  
      }, 
      "appID": "bc90bb525bc9739a9595bb9e176dab17"  
    } 
  } 
 
 Marketdata  Websocket  ( Apollo )  
 
1. Websocket L ogin R equest :  
After creating  marketdata  websocket send  login request  in below format :  
Request :  
 
 
 
 
 
 
 
 
 
 
Response :  
 
 
 
 
 
 
 
 
 
 
 
 
  { 
    "request": {  
      "data": {  
        "gscid": "REST",  
        "gcid": 34,  
        "sessionId": "$2a$10$q74i4JT8VePI8ajLc5bWCu",  
        "device_type": "0"  
      }, 
      "response_format": "json",  
      "request_type": "subscribe",  
      "streaming_type": "login"  
    } 
  } 
 
  { 
    "response": {  
      "svcName": "login",  
      "serverTime": "1694605069000",  
      "streaming_type": "LoginResponse",  
      "data": {  
        "error_code": "0",  
        "gscid": "rest",  
        "gcid": "34",  
        "reconnect": "1"  
      } 
    } 
  } 
 
2. Websocket Heartbeat R equest :  
Send heartbeat request in every interval  (seconds) received in flag values request.  
Request :  
 
 
 
 
 
 
 
 
 
3. Subscribe Request  for Market Feed:  
 
For e g : 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
   
  { 
    "request": {  
      "data": {  
        "symbols": [  
          { 
            "symbol": "101002885"  
          } 
        ] 
      }, 
      "response_format": "json",  
      "gscid": "REST",  
      "gcid": "33",  
      "request_type": "subscribe",  
      "streaming_type": "  marketPicture " 
    } 
  } 
  
 { 
    "request": {  
      "data": {  
        "gcid": 34,  
        "sessionId": "$2a$10$q74i4JT8VePI8ajLc5bWCu"  
      }, 
      "response_format": "json",  
      "request_type": "subscribe",  
      "streaming_type": "HeartBeat"  
    } 
  } 
 
Response i s received in Websocket .  
Response :  
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
   { 
    "response": {  
      "svcName": "Broadcast",  
      "serverTime": "1692174637000",  
      "streaming_type": "marketPicture",  
      "data": {  
        "l52w": "0.00",  
        "bidqty": "28",  
        "tbq": "246669",  
        "h52w": "0.00",  
        "askqty": "24",  
        "p_change": " -0.34",  
        "ltp": "2568.50",  
        "atp": "2566.26",  
        "high": "2582.80",  
        "change": " -8.75",  
        "asset_type": "",  
        "open": "2551.00",  
        "ask": "2568.50",  
        "oi": "0",  
        "close": "2577.25",  
        "tot_vol": "3746202",  
        "tot_buyQty": "246669.00",  
        "tot_sel lQty": "475495.00",  
        "ltq": "5",  
        "level2": [  
          { 
            "bid": {  
              "price": "2567.75",  
              "no": "3",  
              "qty": "28"  
            }, 
            "ask": {  
              "price": "2568.50",  
              "no": "1",  
              "qty": "24"  
            } 
          }, 
          { 
            "bid": {  
              "price": "2567.70",  
              "no": "2",  
              "qty": "251"  
            }, 
            "ask": {  
              "price": "2568.70",  
              "no": "1",  
              "qty": "4"  
            } 
          }, 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
  
          { 
            "bid": {  
              "price": "2567.65",  
              "no": "3",  
              "qty": "81"  
            }, 
            "ask": {  
              "price": "2568.75",  
              "no": "1",  
              "qty": "1"  
            } 
          }, 
          { 
            "bid": {  
              "price": "2567.60",  
              "no": "4",  
              "qty": "291"  
            }, 
            "ask": {  
              "price": "2568.80",  
              "no": "1",  
              "qty": "63"  
            } 
          }, 
          { 
            "bid": {  
              "price": "2567.55",  
              "no": "1",  
              "qty": "1"  
            }, 
            "ask": {  
              "price": "2568.90",  
              "no": "2",  
              "qty": "41"  
            } 
          } 
        ], 
        "symbol": "101002885",  
        "bid": "2567.7500",  
        "taq": "0",  
        "exch": "NSE",  
        "ltt": "16 -08-2023 14:00:36",  
        "lut": "16 -08-2023 14:00:37",  
        "low": "2551.00",  
        "name": "RELIANCE"  
      } 
    } 
  } 
 
Request  for U nsubscribe token : 
 
   
  { 
    "request": {  
      "data": {  
        "symbols": [  
          { 
            "symbol": "101002885"  
          } 
        ] 
      }, 
      "response_format": "json",  
      "gscid": "REST",  
      "gcid": "33",  
      "request_type": " unsubscribe",  
      "streaming_type": "  marketPicture " 
    } 
  } 