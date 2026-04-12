Greeksoft Technologies Pvt Ltd
RESTAPI Document
Release Notice

| Name of Document | RESTAPI Document |
| --- | --- |
| Document No. | SDLC/G/01 |
| Version No. | 1.0 |
| Release date | 01/03/2022 |

Copyrights
All rights reserved. No part of this document may be reproduced or transmitted in any form and by any means without the prior permission of GTPL.
Table of content
1	Authorization
2	GetFlagValues
3	GetLoginInfo
4	Web Socket Login Request
5	Allowed Product
6	Market Status
7	Broadcast
8	Orders
9	NetPosition
10	Holdings
Authentication Token:
Session token will be provided from below request
REQUEST :
Below Request is POST Request
HEADER : http://182.76.70.89:3001/auth/greek/sessiontoken
BODY :
{
"username":"User",
"password":"Password
}
RESPONSE :
{
"id": 162,
"sessionToken": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MTYyLCJnc2NpZCI6IlJFU1QiLCJicm9rZXIiOiJTaWx2ZXJfc3RyZWFtIiwiaWF0IjoxNjc2ODgzNDA1LCJleHAiOjE2NzY5Njk4MDUsImlzcyI6ImF1dGgwIn0.IRp99dgCAtDW5LytCWTOwOcy_eHtphdpK30P_9QjC2uOZoCEBwFNMi38YxT9bRyPyndHALK68YhLX_DSOze_CAcVb2NuPyU6aL3wuv4-niu6gEP4HO8qGbD5TOWT0Y5tRqEK2BFGSehgbSLfCAdYhUjMR-V5vKAFe5NLoMyek3jFDjrrafc5bE21Wl23j5a5esWIAfFp7ozGf4GJ1jRHnhRwhzWH6_Kf7v0d8VA48LDh5kAiYuF8MTGwHoBWbvGrv-oGNFkwwczcfskRnnF01t3t2lbgApjLq7mrHsrK7Mwlah3TpcRoGi76roGZKZ0OhrqGTl87sfXZPVCW5fVCszvXMDGj2nIqdeKto9vKAi08TbrB-wVHoJEjLnHa-ETucSiW98MzktNttHr6Xe_xCtAZXyhf7SQxWe92gY3ZIoxVvYfPZFPGmqCKeivs6dhVwQ-EwtHAKZDcII2j2JQ8OBnHxn7F6WbRU8_3N2uPQRZep6bhSZ_PEtb8kR-rDJm2"
}
GETFLAGVALUES
We get all flag-related information from below request
REQUEST  TYPE : POST

| Request | http://restapi.greeksoft.in:3333/getFlagValues |


| Parameter | Parameter | Type | Default | Required | Description/Remark |
| --- | --- | --- | --- | --- | --- |
| svcName |  | String | getFlagValues | Yes |  |
| svcGroup |  | String |  | yes |  |
| assetType |  | String |  | Yes |  |

RESPONSE :
{"config":{"app":12,"label":8,"message":9},"response":{"ErrorCode":0,"appID":"bc90bb525bc9739a9595bb9e176dab17","data":{"Apollo_IP":"restapi.greeksoft.in","Apollo_Port":8082,"Arachne_IP":"restapi.greeksoft.in","Arachne_Port":3333,"BroadcastSender_Port":"true","ChartSetting":"192.168.207.92","DPType":"CDSL","Iris_IP":"restapi.greeksoft.in","Iris_Port":8085,"IsBOReport":"true","IsEDISProduct":0,"IsRedisEnabled":"false","IsStrategyProduct":"true","OrderSender_Port":8085,"accord_Token":"","apr_version":"","defaultProduct":"Delivery","ft_testing_bypass":"false","heartbeat_Intervals":10,"holdingFlag":"false","isSecure":"false","posCode":"","reconnection_attempts":1800,"showDescription":"false","showLogin":"true","validate2FA":"false","validateGuest":"false","validatePasswordOnce":"1","validateThrough":0,"validateTransaction":"false"},"infoID":"0","msgID":"a9bfad10-92ce-4fd7-968f- c25877c1bbb3","serverTime":"1450349681701","sessionId":"","svcGroup":"","svcName":"getFlagValues","svcVersion":"1.0.0"}}
GetLoginInfo
This request returns us with gscid value which will be client code
Request Type: Post

| Request | <Base URL>:3000/getLoginInfo |


| Parameter | Parameter | Type | Default | Required | Description/Remark |
| --- | --- | --- | --- | --- | --- |
| svcName |  | String | getLoginInfo | Yes |  |
| svcGroup |  | String | Portfolio | Yes |  |
| data |  | Object | { "gscid": "<GSCID>"} | Yes |  |
| svcVersion |  | String | 1.0.0 | Yes |  |

Request Example:-
{
"request": {
"svcVersion": "1.0.0",
"svcGroup": "Login",
"svcName": "getLoginInfo",
"assetType": "",
"data": { "gscid": "<GSCID>"}
}
}
Response:-
{
"config": {
"app": 12,
"label": 8,
"message": 9
},
"response": {
"appID": "bc90bb525bc9739a9595bb9e176dab17",
"data": {
"AllowedMarket": [
{
"market_id": 1
},
{
"market_id": 2
}
],
"gcid":<GCID>,
"gscid": "<GSCID>"
},
"infoID": "0",
"msgID": "a9bfad10-92ce-4fd7-968f- c25877c1bbb3",
"serverTime": "1450349681701",
"svcGroup": "Login",
"svcName": "getLoginInfo",
"svcVersion": "1.0.0"
}
}
4.  WEBSOCKET LOGIN REQUEST
For Web socket login request, you need to first send a jloginnew request, then an IRIS login request, and an IRIS heartbeat.
jloginNew:-
Request Type: Post
After getting the response to the getflagValue request, we get the archane IP and port for sending the following login request.
.

| Request | http:restapi.greeksoft.in:3333/jloginNew |


| Parameter | Parameter | Type | Default | Required | Description/Remark |
| --- | --- | --- | --- | --- | --- |
| svcName |  | String | jloginNew | Yes |  |
| svcGroup |  | String | Login | Yes |  |
| Data |  |  |  |  |  |
| pan_dob |  | String | N/A | Yes |  |
| deviceId |  | String | N/A |  | Getting from Android Setting |
| Gscid |  | String | N/A | YES | User name  (inputed in username field) |
| deviceDetails |  | String | N/A |  | manufacturer + "-" + model + "-" + version; |
| deviceType |  | String | N/A |  | For 0- Android |
| pass |  | String | N/A | YES | Password(input) |
| transPass |  | String | N/A | NO |  |
| userType |  | String | Customer |  |  |
| brokerid |  | String | 1 |  |  |
| passType |  | String | 0 |  |  |
| version_no |  | String | 1.0.1.10 |  | Send default value |
| encryptionType |  | String | 1 |  |  |

Request Example :-
http://restapi.greeksoft.in:3333/jloginNew
{
"request": {
"data": {
"pan_dob": "01/01/1901",
"deviceId": "4f89423bab1280c9",
"gscid": "TEST1",
"deviceDetails": "",
"deviceType": "0",
"pass": "b12b46ba4bba0a32b03559649d16bae1",
"transPass": "",
"userType": "Customer",
"brokerid": "1",
"passType": "0",
"version_no": "1.0.1.10",
"encryptionType": "1"
},
"svcName": "jloginNew",
"svcGroup": "Login"
}
}
Response:-
{"config":{"app":12,"label":8,"message":9},"response":{"ErrorCode":0,"appID":"bc90bb525bc9739a9595bb9e176dab17","data":{"AllowedMarket":[{"market_id":1},{"market_id":2}],"Apollo_IP":"restapi.greeksoft.in","Apollo_Port":8082,"Arachne_IP":"restapi.greeksoft.in","Arachne_Port":3333,"BroadcastSender_Port":8082,"ChartSetting":"192.168.207.92","ClientCode":3,"DPType":"CDSL","ErrorCode":0,"Executioncode":0,"Iris_IP":"restapi.greeksoft.in","Iris_Port":8085,"IsBOReport":"true","IsEDISProduct":"true","IsRedisEnabled":"false","IsSameDevice":"false","IsStrategyProduct":"true","IsValidateSecondary":"false","KYCStatus":"N","OrderSender_Port":8085,"OrderTime":"1500","Theme":"","cCategory":"Dealer","clientName":"TEST1","defaultProduct":"Delivery","dob":"","gscid":"TEST1","holdingFlag":"false","isMPINSet":"false","isStrategyLogin":"","mandateId":0,"panNo":"TDEJHVJH13","quote":"","userType":0,"validate2FA":"false","validateTransaction":"false"},"infoID":"0","msgID":"a9bfad10-92ce-4fd7-968f- c25877c1bbb3","serverTime":"1450349681701","sessionId":"$2a$10$q1ECqJPvOAh8JwAjMlAfTu","svcGroup":"Login","svcName":"jloginNew","svcVersion":"1.0.0"}}
If error codes are received while sending the request, kindly refer to the below error codes.
ERROR CODES FOR JLOGINNEW
1: "Password Expired"
2: "Invalid Password"
3:"Failure"
4:"Duplicate Password  not Allowed "
5:"Max Attempts Exceeded for wrong Password"
6:"Inactive User"
7:"Inactive User"
8:"Invalid 2FAAnswer"
9:"Same Id password"
10:"Same Login and Transaction passwords"
11:"Guest not registered"
12:"Guest already registered"
13:"Retailer does not exist"
14:"Version mismatch"
17:"Account Locked,Please Contact Admin and Change Password"
18:"Login & Transaction Password Expired"
IRISLogin Request:-
Type :WebSocket Request
We need to create websocket and using this websocket  we need to send Login request to iris server .

| Request | ws://restapi.greeksoft.in:8085 |


| Parameter | Parameter | Type | Default | Required | Description/Remark |
| --- | --- | --- | --- | --- | --- |
| response_format |  | String | Json | Yes |  |
| request_type |  | String | subscribe | Yes |  |
| streaming_type |  | String | login |  |  |
| Data |  |  |  |  |  |
| Gscid |  | String | N/A | Yes |  |
| Gcid |  | String | N/A | Yes | ClientCode from jloginNew Response |
| sessionId |  | String | N/A |  | SessionId from JloginNEW response |
| device_id |  | String | N/A |  |  |
| device_type |  | String | N/A |  |  |

Request Example:-
{
"request": {
"data": {
"gscid": "TEST1",
"gcid": "3",
"sessionId": "$2a$10$q1ECqJPvOAh8JwAjMlAfTu ",
"device_id": "a21f0390f4f7d9cc",
"device_type": "0"
},
"response_format": "json",
"request_type": "subscribe",
"streaming_type": "login"
}
}
Response:-
{"response":{"svcName":"login","serverTime":"1677145575000","infoID":"0","streaming_type":"LoginResponse","data":{"error_code":"0","gscid":"VEVTVDE=","gcid":"3","reconnect":"1","logtime":"1677145576"},"appID":"bc90bb525bc9739a9595bb9e176dab17"}}
Iris heartbeat:-
Type :WebSocket request
We need to send heartbeat request per heartbeat_Intervals(getting from getflagvalue request) to iris server.

| Request | ws://restapi.greeksoft.in:8085 |


| Parameter | Parameter | Type | Default | Required | Description/Remark |
| --- | --- | --- | --- | --- | --- |
| response_format |  | String | Json | Yes |  |
| request_type |  | String | subscribe | Yes |  |
| streaming_type |  | String | HeartBeat |  |  |
| Data |  |  |  |  |  |
| Gcid |  | String | N/A | Yes | ClientCode from jlogin Response |
| sessionId |  | String | N/A |  | SessionId from jlogin Response |

Request Example:-
{
"request": {
"data": {
"gcid": "3",
"sessionId": ""$2a$10$q1ECqJPvOAh8JwAjMlAfTu "
},
"response_format": "json",
"request_type": "subscribe",
"streaming_type": "HeartBeat"
}
}
Response:-
{
"response": {
"svcName": "login",
"streaming_type": "HeartBeat",
"data": {
"curr_time": "1649830766",
"error_code": "0",
"gcid": "3",
"apptype": "0"
},
"appID": "bc90bb525bc9739a9595bb9e176dab17"
}
}
5. AllowedProduct :-
Request Type: Post
This API returns with allowed product details

| Request | http://restapi.greeksoft.in:3333/getAllowedProduct |


| Parameter | Parameter | Type | Default | Required | Description/Remark |
| --- | --- | --- | --- | --- | --- |
| svcName |  | String | getAllowedProduct | Yes |  |
| svcGroup |  | String | Login | Yes |  |
| Data |  |  |  |  |  |

Request Example:-
{
"request": {
"data": {},
"svcName": "getAllowedProduct",
"svcGroup": "Login"
}
}
Response Example:-
{
"response": {
"svcName": "getAllowedProduct",
"serverTime": "1450349681701",
"infoID": "0",
"appID": "bc90bb525bc9739a9595bb9e176dab17",
"svcVersion": "1.0.0",
"msgID": "a9bfad10-92ce-4fd7-968f- c25877c1bbb3",
"svcGroup": "Login",
"ErrorCode": 0,
"data": {
"AllowedProduct": [
{
"iProductToken": 0,
"cProductName": "DELIVERY"
},
{
"iProductToken": 1,
"cProductName": "INTRADAY"
},
{
"iProductToken": 2,
"cProductName": "MTF"
},
{
"iProductToken": 3,
"cProductName": "TNC"
},
{
"iProductToken": 4,
"cProductName": "CATALYST"
},
{
"iProductToken": 5,
"cProductName": "SSEQ"
}
]
}
},
"config": {
"label": 8,
"message": 9,
"app": 12
}
}
6. GetMarketStatus :-
Request Type: Post
This API returns with current market status of exchanges

| Request | http://restapi.greeksoft.in:3333/getMarketStatus |


| Parameter | Parameter | Type | Default | Required | Description/Remark |
| --- | --- | --- | --- | --- | --- |
| svcName |  | String | getMarketStatus | Yes |  |
| svcGroup |  | String | Markets | Yes |  |
| Data |  |  |  |  |  |
| Gscid |  | String |  | Yes |  |

Request Example:-
{
"request": {
"data": {
"gscid": "TEST1"
},
"svcName": "getMarketStatus",
"svcGroup": "Markets"
}
}
Response:-
{
"response": {
"svcName": "getMarketStatus",
"serverTime": "1450349681701",
"infoID": "0",
"appID": "bc90bb525bc9739a9595bb9e176dab17",
"svcVersion": "1.0.0",
"msgID": "a9bfad10-92ce-4fd7-968f- c25877c1bbb3",
"svcGroup": "Markets",
"ErrorCode": 0,
"data": {
"MarketStatus": [
{
"market_id": 1,
"status": 1,
"session": 1
}
],
"config": {
"label": 8,
"message": 9,
"app": 12
}
}
}
}
BROADCAST
GETFULLSCRIPDETAILSBYSYMBOL_MOBILE
This API returns details of scrip required for requesting broadcast.
Request Type : GET
http://restapi.greeksoft.in:3333/getFullScripDetailsBySymbol_Mobile?ZXhjaGFuZ2U9TlNFJmFzc2V0VHlwZT1mdXR1cmUmY29kZT1kR0YwWVcxdmRHOXljdz09JnR5cGU9ZnV0dXJl
(exchange=NSE&assetType=future&code=dGF0YW1vdG9ycw==&type=future)
Response:
{"ErrorCode":0,"data":[{"Name":"TATAMOTORS 29MAR23","OptionType":"XX","ScriptName":"TATAMOTORS","Series":"FUTSTK","UniqueId":52508,"assetType":"future","description":"TATAMOTORS 29MAR23","exchange":"nse","expiryDate":1680080400,"instrumentName":"FUTSTK","lotQty":1425,"multiplier":1,"strickPrice":0,"tickSize":0.050000000000000003,"token":102052508,"tradeSymbol":"TATAMOTORS 29MAR23"},{"Name":"TATAMOTORS 27APR23","OptionType":"XX","ScriptName":"TATAMOTORS","Series":"FUTSTK","UniqueId":53088,"assetType":"future","description":"TATAMOTORS 27APR23","exchange":"nse","expiryDate":1682586000,"instrumentName":"FUTSTK","lotQty":1425,"multiplier":1,"strickPrice":0,"tickSize":0.050000000000000003,"token":102053088,"tradeSymbol":"TATAMOTORS 27APR23"}],"message":"","success":"true"}
GETQUOTEFORSINGLESYMBOL
This API returns most up-to-date market data for a single stock ticker like open,high,close ,etc
Request Type  : POST
http://restapi.greeksoft.in:3333/getQuoteForSingleSymbol_V2
Body:
{
"request": {
"data": {
"token": "101000048",
"assetType": "equity",
"gscid": "TEST",
"gcid": "2"
},
"svcName": "getQuoteForSingleSymbol_V2",
"svcGroup": "Markets"
}
}
RESPONSE:
{"config":{"app":12,"label":8,"message":9},"response":{"appID":"bc90bb525bc9739a9595bb9e176dab17","data":{"AssetToken":0,"ask":0,"assetLtp":0,"atp":0,"authorizedQty":0,"bid":0,"change":0,"close":0,"description":"HAPPSTMNDS","expiryDate":0,"freezQty":114112,"high":0,"highRange":1051.55,"instrument":"EQ","isinumber":"INE419U01012","last":0,"level2":[{"ask":{"no":0,"price":0,"qty":0},"bid":{"no":0,"price":0,"qty":0}}],"lot":1,"low":0,"lowRange":701.04999999999995,"ltt":0,"oi":0,"oi_pChange":0,"open":0,"optiontype":"XX","p_change":0,"reason":"","sqOffQty":0,"strikeprice":0,"symbol":"HAPPSTMNDS","tickSize":0.050000000000000003,"token":101000048,"tot_buyQty":0,"tot_sellQty":0,"tot_vol":0,"yhigh":0,"ylow":0},"infoID":"0","msgID":"a9bfad10-92ce-4fd7-968f- c25877c1bbb3","serverTime":"1450349681701","svcGroup":"Markets","svcName":"getQuoteForSingleSymbol_V2","svcVersion":"1.0.0"}}
GETQUOTEFORMULTIPLESYMBOLS
This API returns details of multiple symbols simultaneously.
Request :
http://restapi.greeksoft.in:3333/getQuoteForMultipleSymbols
Body :
{"request":{"data":{"symbolList":[{"assetType":"future","exchange":"NSE","token":"102089544"} ,{"assetType":"equity","exchange":"NSE","token":"101011536"}]},
"svcName":"getQuoteForMultipleSymbols","svcGroup":"Markets"}}
Response:
{"response":{"svcName":"getQuoteForMultipleSymbols","serverTime":"1450349681701","infoID":"0","appID":"bc90bb525bc9739a9595bb9e176dab17","svcVersion":"1.0.0","msgID":"a9bfad10-92ce-4fd7-968f- c25877c1bbb3",
"svcGroup":"Markets","ErrorCode":null,
"data":{"quoteList":[{"ylow":"0","bidqty":28,"yhigh":0,"askqty":1,"p_change":1.488944,"last":2971.85,"avgPrice":2967.01,
"high":2987.9,"change":43.6,"asset_type":"equity","open":2950,"ask":2971.5,"oi":11363700,"close":2928.25,
"tot_vol":1828247,"symbol":"TCS","ltt":1294227769,"bid":2970.9,"exch":"NSE","low":2940.95,
"name":"TATA CONSULTANCY SERV LT","token":101011536,"optionType":"XX","expiryDate":0,"strikePrice":0,
"instrumentName":"EQ","lot":1,"scriptname":"TCS","tickSize":0.05,"multiplier":1}]}},
"config":{"label":8,"message":9,"app":12}}
ORDERS
New Order Request
REQUEST :
http://restapi.greeksoft.in:3333/NewOrderRequest
BODY :
{
"request": {
"data": {
"trigger_price": "0",
"gtoken": "101011536",
"side": "1",
"gcid": "3",
"validity": "0",
"price": "3373",
"exchange": "NSE",
"disclosed_qty": "0",
"tradeSymbol": "TCS",
"lot": "1",
"order_type": "1",
"product": "0",
"qty": "2",
"corderid": "3",
"amo": "0",
"gtdExpiry": 0,
"is_post_closed": "0",
"is_preopen_order": "0",
"isSqOffOrder": "false",
"offline": "0"
},
"response_format": "json",
"request_type": "subscribe",
"streaming_type": "NewOrderRequest"
}
}
RESPONSE:
{"response":{"svcName":"NewOrderRequestResponse","serverTime":"1677240618000","infoID":"0","streaming_type":"OrderResponse","data":{"gscid":"TEST1","gorderid":"120000009","ErrorCode":"0","tag":""},"appID":"bc90bb525bc9739a9595bb9e176dab17"}}
GETORDERDETAILS
Request Type :GET
ALL ORDERBOOK
http://restapi.greeksoft.in:3333/getOrderBookDetailWithLegV2?ZXhjaGFuZ2VUeXBlPUFsbCZDbGllbnRDb2RlPTImT3JkZXJfU3RhdHVzPUFMTCZPcmRlcnR5cGU9QWxsJmdzY2lkPVRFU1Qx
(exchangeType=All&ClientCode=2&Order_Status=ALL&Ordertype=All&gscid=TEST1)
RESPONSE :
{"ErrorCode":0,"data":[{"BookType":1,"LegInfo":[],"LogTime":1677241066,"OrderFlags":8,"action":1,"amount":6720,"assetType":"0","cPANNumber":"TDEJHVJH13","clientCode":"TEST1","dSLPrice":0,"dSLTPrice":0,"dTargetPrice":0,"description":"TATA CONSULTANCY SERV LT","discQty":0,"errorCode":0,"exchange":"0","expiryDate":0,"filterKey":"0","flowType":"0","iNoOfLegs":0,"iStrategyId":0,"instrument":"EQ","isCancellable":"True","isEditable":"TRUE","lIOMRuleNo":0,"lastModBy":0,"lgoodtilldate":0,"lotSize":1,"multiplier":100,"optionType":"XX","ordID":0,"ordLiveDays":0,"ordModTime":1361728066,"ordTime":"24-2-2023 17:47:46","orderType":1,"otype":1,"pendingQty":2,"pendingdiscQty":0,"price":3360,"product":0,"qty":2,"remarks":"0","scripName":"TCS","status":"Pending","strategyName":"GREEKSOFT","strikePrice":0,"tag":"","tickSize":0.05000000074505806,"tmplotSize":"0","token":101011536,"tradeSymbol":"TCS","trdQty":0,"trigPrice":0,"uniqueID":120000011,"uniqueOrderID":"1300000000130700","userID":"TEST1"},{"BookType":1,"LegInfo":[],"LogTime":1677241033,"OrderFlags":8,"action":1,"amount":6746,"assetType":"0","cPANNumber":"TDEJHVJH13","clientCode":"TEST1","dSLPrice":0,"dSLTPrice":0,"dTargetPrice":0,"description":"TATA CONSULTANCY SERV LT","discQty":0,"errorCode":0,"exchange":"0","expiryDate":0,"filterKey":"0","flowType":"0","iNoOfLegs":0,"iStrategyId":0,"instrument":"EQ","isCancellable":"True","isEditable":"TRUE","lIOMRuleNo":0,"lastModBy":0,"lgoodtilldate":0,"lotSize":1,"multiplier":100,"optionType":"XX","ordID":0,"ordLiveDays":0,"ordModTime":1361728033,"ordTime":"24-2-2023 17:47:13","orderType":1,"otype":1,"pendingQty":0,"pendingdiscQty":0,"price":3373,"product":0,"qty":2,"remarks":"0","scripName":"TCS","status":"Traded","strategyName":"GREEKSOFT","strikePrice":0,"tag":"","tickSize":0.05000000074505806,"tmplotSize":"0","token":101011536,"tradeSymbol":"TCS","trdQty":2,"trigPrice":0,"uniqueID":120000010,"uniqueOrderID":"1300000000130676","userID":"TEST1"},{"BookType":1,"LegInfo":[],"LogTime":1677241033,"OrderFlags":8,"action":1,"amount":6746,"assetType":"0","cPANNumber":"TDEJHVJH13","clientCode":"TEST1","dSLPrice":0,"dSLTPrice":0,"dTargetPrice":0,"description":"TATA CONSULTANCY SERV LT","discQty":0,"errorCode":0,"exchange":"0","expiryDate":0,"filterKey":"0","flowType":"0","iNoOfLegs":0,"iStrategyId":0,"instrument":"EQ","isCancellable":"True","isEditable":"TRUE","lIOMRuleNo":0,"lastModBy":0,"lgoodtilldate":0,"lotSize":1,"multiplier":100,"optionType":"XX","ordID":0,"ordLiveDays":0,"ordModTime":1361728033,"ordTime":"24-2-2023 17:47:13","orderType":1,"otype":1,"pendingQty":0,"pendingdiscQty":0,"price":3373,"product":0,"qty":2,"remarks":"0","scripName":"TCS","status":"Traded","strategyName":"GREEKSOFT","strikePrice":0,"tag":"","tickSize":0.05000000074505806,"tmplotSize":"0","token":101011536,"tradeSymbol":"TCS","trdQty":2,"trigPrice":0,"uniqueID":120000009,"uniqueOrderID":"1300000000130505","userID":"TEST1"},{"BookType":1,"LegInfo":[],"LogTime":1677217778,"OrderFlags":8,"action":1,"amount":0,"assetType":"0","cPANNumber":"0","clientCode":"TEST1","dSLPrice":0,"dSLTPrice":0,"dTargetPrice":0,"description":"TATA CONSULTANCY SERV LT","discQty":0,"errorCode":0,"exchange":"0","expiryDate":0,"filterKey":"0","flowType":"0","iNoOfLegs":0,"iStrategyId":0,"instrument":"EQ","isCancellable":"True","isEditable":"TRUE","lIOMRuleNo":0,"lastModBy":0,"lgoodtilldate":0,"lotSize":1,"multiplier":100,"optionType":"XX","ordID":120000008,"ordLiveDays":0,"ordModTime":0,"ordTime":"24-2-2023 11:19:38","orderType":1,"otype":0,"pendingQty":0,"pendingdiscQty":0,"price":40100,"product":0,"qty":2,"remarks":"0R","scripName":"TCS","status":"RMS Rejected","strategyName":"GEEKSOFT","strikePrice":0,"tag":"Ageing","tickSize":0.05000000074505806,"tmplotSize":"0","token":101011536,"tradeSymbol":"TATA CONSULTANCY SERV LT","trdQty":0,"trigPrice":0,"uniqueID":120000008,"uniqueOrderID":"0","userID":"0"},{"BookType":1,"LegInfo":[],"LogTime":1677217751,"OrderFlags":8,"action":1,"amount":0,"assetType":"0","cPANNumber":"0","clientCode":"TEST1","dSLPrice":0,"dSLTPrice":0,"dTargetPrice":0,"description":"TATA CONSULTANCY SERV LT","discQty":0,"errorCode":0,"exchange":"0","expiryDate":0,"filterKey":"0","flowType":"0","iNoOfLegs":0,"iStrategyId":0,"instrument":"EQ","isCancellable":"True","isEditable":"TRUE","lIOMRuleNo":0,"lastModBy":0,"lgoodtilldate":0,"lotSize":1,"multiplier":100,"optionType":"XX","ordID":120000007,"ordLiveDays":0,"ordModTime":0,"ordTime":"24-2-2023 11:19:11","orderType":1,"otype":0,"pendingQty":0,"pendingdiscQty":0,"price":40100,"product":0,"qty":25,"remarks":"0","scripName":"TCS","status":"RMS Rejected","strategyName":"GREEKSOFT","strikePrice":0,"tag":"Ageing","tickSize":0.05000000074505806,"tmplotSize":"0","token":101011536,"tradeSymbol":"TATA CONSULTANCY SERV LT","trdQty":0,"trigPrice":0,"uniqueID":120000007,"uniqueOrderID":"0","userID":"0"},{"BookType":1,"LegInfo":[],"LogTime":1677217532,"OrderFlags":8,"action":1,"amount":0,"assetType":"0","cPANNumber":"0","clientCode":"TEST1","dSLPrice":0,"dSLTPrice":0,"dTargetPrice":0,"description":"TCS 23FEB23","discQty":0,"errorCode":0,"exchange":"0","expiryDate":1677142800,"filterKey":"0","flowType":"0","iNoOfLegs":0,"iStrategyId":0,"instrument":"FUTSTK","isCancellable":"True","isEditable":"TRUE","lIOMRuleNo":0,"lastModBy":0,"lgoodtilldate":0,"lotSize":175,"multiplier":100,"optionType":"XX","ordID":120000006,"ordLiveDays":0,"ordModTime":0,"ordTime":"24-2-2023 11:15:32","orderType":1,"otype":0,"pendingQty":0,"pendingdiscQty":0,"price":40100,"product":0,"qty":25,"remarks":"0","scripName":"TCS","status":"RMS Rejected","strategyName":"GREEKSOFT","strikePrice":0,"tag":"Ageing","tickSize":0.05000000074505806,"tmplotSize":"0","token":102057719,"tradeSymbol":"TCS 23FEB23","trdQty":0,"trigPrice":0,"uniqueID":120000006,"uniqueOrderID":"0","userID":"0"},{"BookType":1,"LegInfo":[],"LogTime":1677217478,"OrderFlags":8,"action":1,"amount":0,"assetType":"0","cPANNumber":"0","clientCode":"TEST1","dSLPrice":0,"dSLTPrice":0,"dTargetPrice":0,"description":"TCS 23FEB23","discQty":0,"errorCode":0,"exchange":"0","expiryDate":1677142800,"filterKey":"0","flowType":"0","iNoOfLegs":0,"iStrategyId":0,"instrument":"FUTSTK","isCancellable":"True","isEditable":"TRUE","lIOMRuleNo":0,"lastModBy":0,"lgoodtilldate":0,"lotSize":175,"multiplier":100,"optionType":"XX","ordID":120000005,"ordLiveDays":0,"ordModTime":0,"ordTime":"24-2-2023 11:14:38","orderType":1,"otype":0,"pendingQty":0,"pendingdiscQty":0,"price":41650,"product":0,"qty":25,"remarks":"0","scripName":"TCS","status":"RMS Rejected","strategyName":"GREEKSOFT","strikePrice":0,"tag":"Ageing","tickSize":0.05000000074505806,"tmplotSize":"0","token":102057719,"tradeSymbol":"TCS 23FEB23","trdQty":0,"trigPrice":0,"uniqueID":120000005,"uniqueOrderID":"0","userID":"0"},{"BookType":1,"LegInfo":[],"LogTime":1677240196,"OrderFlags":8,"action":1,"amount":1041250,"assetType":"0","cPANNumber":"TDEJHVJH13","clientCode":"TEST1","dSLPrice":0,"dSLTPrice":0,"dTargetPrice":0,"description":"BANKNIFTY 23FEB23","discQty":0,"errorCode":16280,"exchange":"0","expiryDate":1677142800,"filterKey":"0","flowType":"0","iNoOfLegs":0,"iStrategyId":0,"instrument":"FUTIDX","isCancellable":"True","isEditable":"TRUE","lIOMRuleNo":0,"lastModBy":0,"lgoodtilldate":0,"lotSize":25,"multiplier":100,"optionType":"XX","ordID":0,"ordLiveDays":0,"ordModTime":0,"ordTime":"24-2-2023 17:33:16","orderType":1,"otype":1,"pendingQty":25,"pendingdiscQty":0,"price":41650,"product":0,"qty":25,"remarks":"0","scripName":"BANKNIFTY","status":"Exchange Rejected","strategyName":"GREEKSOFT","strikePrice":0,"tag":"","tickSize":0.05000000074505806,"tmplotSize":"0","token":102048756,"tradeSymbol":"BANKNIFTY 23FEB23","trdQty":0,"trigPrice":0,"uniqueID":120000004,"uniqueOrderID":"1100000000003294","userID":"TEST1"},{"BookType":1,"LegInfo":[],"LogTime":1677240103,"OrderFlags":8,"action":1,"amount":1041250,"assetType":"0","cPANNumber":"TDEJHVJH13","clientCode":"TEST1","dSLPrice":0,"dSLTPrice":0,"dTargetPrice":0,"description":"BANKNIFTY 23FEB23","discQty":0,"errorCode":16280,"exchange":"0","expiryDate":1677142800,"filterKey":"0","flowType":"0","iNoOfLegs":0,"iStrategyId":0,"instrument":"FUTIDX","isCancellable":"True","isEditable":"TRUE","lIOMRuleNo":0,"lastModBy":0,"lgoodtilldate":0,"lotSize":25,"multiplier":100,"optionType":"XX","ordID":0,"ordLiveDays":0,"ordModTime":0,"ordTime":"24-2-2023 17:31:43","orderType":1,"otype":1,"pendingQty":25,"pendingdiscQty":0,"price":41650,"product":0,"qty":25,"remarks":"0","scripName":"BANKNIFTY","status":"Exchange Rejected","strategyName":"GREEKSOFT","strikePrice":0,"tag":"","tickSize":0.05000000074505806,"tmplotSize":"0","token":102048756,"tradeSymbol":"BANKNIFTY 23FEB23","trdQty":0,"trigPrice":0,"uniqueID":120000003,"uniqueOrderID":"1100000000003274","userID":"TEST1"}],"message":"","success":"true"}
TRADED ORDERBOOK
REQUEST :
GET REQUEST
http://restapi.greeksoft.in:3333/getOrderBookDetailWithLegV2?ZXhjaGFuZ2VUeXBlPUFsbCZDbGllbnRDb2RlPTMmT3JkZXJfU3RhdHVzPVRSQURFRCZPcmRlcnR5cGU9QWxsJmdzY2lkPVRFU1Qx
(exchangeType=All&ClientCode=3&Order_Status=TRADED&Ordertype=All&gscid=TEST1)
RESPONSE:
{"ErrorCode":0,"data":[{"BookType":1,"LegInfo":[],"LogTime":1677241033,"OrderFlags":8,"action":1,"amount":6746,"assetType":"0","cPANNumber":"TDEJHVJH13","clientCode":"TEST1","dSLPrice":0,"dSLTPrice":0,"dTargetPrice":0,"description":"TATA CONSULTANCY SERV LT","discQty":0,"errorCode":0,"exchange":"0","expiryDate":0,"filterKey":"0","flowType":"0","iNoOfLegs":0,"iStrategyId":0,"instrument":"EQ","isCancellable":"True","isEditable":"TRUE","lIOMRuleNo":0,"lastModBy":0,"lgoodtilldate":0,"lotSize":1,"multiplier":100,"optionType":"XX","ordID":0,"ordLiveDays":0,"ordModTime":1361728033,"ordTime":"24-2-2023 17:47:13","orderType":1,"otype":1,"pendingQty":0,"pendingdiscQty":0,"price":3373,"product":0,"qty":2,"remarks":"0","scripName":"TCS","status":"Traded","strategyName":"GREEKSOFT","strikePrice":0,"tag":"","tickSize":0.05000000074505806,"tmplotSize":"0","token":101011536,"tradeSymbol":"TATA CONSULTANCY SERV LT","trdQty":2,"trigPrice":0,"uniqueID":120000009,"uniqueOrderID":"1300000000130505","userID":"TEST1"},{"BookType":1,"LegInfo":[],"LogTime":1677241033,"OrderFlags":8,"action":1,"amount":6746,"assetType":"0","cPANNumber":"TDEJHVJH13","clientCode":"TEST1","dSLPrice":0,"dSLTPrice":0,"dTargetPrice":0,"description":"TATA CONSULTANCY SERV LT","discQty":0,"errorCode":0,"exchange":"0","expiryDate":0,"filterKey":"0","flowType":"0","iNoOfLegs":0,"iStrategyId":0,"instrument":"EQ","isCancellable":"True","isEditable":"TRUE","lIOMRuleNo":0,"lastModBy":0,"lgoodtilldate":0,"lotSize":1,"multiplier":100,"optionType":"XX","ordID":0,"ordLiveDays":0,"ordModTime":1361728033,"ordTime":"24-2-2023 17:47:13","orderType":1,"otype":1,"pendingQty":0,"pendingdiscQty":0,"price":3373,"product":0,"qty":2,"remarks":"0","scripName":"TCS","status":"Traded","strategyName":"GREEKSOFT","strikePrice":0,"tag":"","tickSize":0.05000000074505806,"tmplotSize":"0","token":101011536,"tradeSymbol":"TATA CONSULTANCY SERV LT","trdQty":2,"trigPrice":0,"uniqueID":120000010,"uniqueOrderID":"1300000000130676","userID":"TEST1"}],"message":"","success":"true"}
REJECTED ORDERBOOK
REQUEST
REQUEST TYPE : GET
http://restapi.greeksoft.in:3333/getOrderBookDetailWithLegV2?ZXhjaGFuZ2VUeXBlPUFsbCZDbGllbnRDb2RlPTMmT3JkZXJfU3RhdHVzPVJNUyBSRUpFQ1RFRCZPcmRlcnR5cGU9QWxsJmdzY2lkPVRFU1Qx
(exchangeType=All&ClientCode=3&Order_Status=RMS REJECTED&Ordertype=All&gscid=TEST1)
RESPONSE:
{"ErrorCode":0,"data":[{"BookType":1,"LegInfo":[],"LogTime":1677217478,"OrderFlags":8,"action":1,"amount":0,"assetType":"0","cPANNumber":"0","clientCode":"TEST1","dSLPrice":0,"dSLTPrice":0,"dTargetPrice":0,"description":"TCS 23FEB23","discQty":0,"errorCode":0,"exchange":"0","expiryDate":1677142800,"filterKey":"0","flowType":"0","iNoOfLegs":0,"iStrategyId":0,"instrument":"FUTSTK","isCancellable":"True","isEditable":"TRUE","lIOMRuleNo":0,"lastModBy":0,"lgoodtilldate":0,"lotSize":175,"multiplier":100,"optionType":"XX","ordID":120000005,"ordLiveDays":0,"ordModTime":0,"ordTime":"24-2-2023 11:14:38","orderType":1,"otype":0,"pendingQty":0,"pendingdiscQty":0,"price":41650,"product":0,"qty":25,"remarks":"0","scripName":"TCS","status":"RMS Rejected","strategyName":"GREEKSOFT","strikePrice":0,"tag":"Ageing","tickSize":0.05000000074505806,"tmplotSize":"0","token":102057719,"tradeSymbol":"TCS 23FEB23","trdQty":0,"trigPrice":0,"uniqueID":120000005,"uniqueOrderID":"0","userID":"0"},{"BookType":1,"LegInfo":[],"LogTime":1677217532,"OrderFlags":8,"action":1,"amount":0,"assetType":"0","cPANNumber":"0","clientCode":"TEST1","dSLPrice":0,"dSLTPrice":0,"dTargetPrice":0,"description":"TCS 23FEB23","discQty":0,"errorCode":0,"exchange":"0","expiryDate":1677142800,"filterKey":"0","flowType":"0","iNoOfLegs":0,"iStrategyId":0,"instrument":"FUTSTK","isCancellable":"True","isEditable":"TRUE","lIOMRuleNo":0,"lastModBy":0,"lgoodtilldate":0,"lotSize":175,"multiplier":100,"optionType":"XX","ordID":120000006,"ordLiveDays":0,"ordModTime":0,"ordTime":"24-2-2023 11:15:32","orderType":1,"otype":0,"pendingQty":0,"pendingdiscQty":0,"price":40100,"product":0,"qty":25,"remarks":"0","scripName":"TCS","status":"RMS Rejected","strategyName":"GREEKSOFT","strikePrice":0,"tag":"Ageing","tickSize":0.05000000074505806,"tmplotSize":"0","token":102057719,"tradeSymbol":"TCS 23FEB23","trdQty":0,"trigPrice":0,"uniqueID":120000006,"uniqueOrderID":"0","userID":"0"},{"BookType":1,"LegInfo":[],"LogTime":1677217751,"OrderFlags":8,"action":1,"amount":0,"assetType":"0","cPANNumber":"0","clientCode":"TEST1","dSLPrice":0,"dSLTPrice":0,"dTargetPrice":0,"description":"TATA CONSULTANCY SERV LT","discQty":0,"errorCode":0,"exchange":"0","expiryDate":0,"filterKey":"0","flowType":"0","iNoOfLegs":0,"iStrategyId":0,"instrument":"EQ","isCancellable":"True","isEditable":"TRUE","lIOMRuleNo":0,"lastModBy":0,"lgoodtilldate":0,"lotSize":1,"multiplier":100,"optionType":"XX","ordID":120000007,"ordLiveDays":0,"ordModTime":0,"ordTime":"24-2-2023 11:19:11","orderType":1,"otype":0,"pendingQty":0,"pendingdiscQty":0,"price":40100,"product":0,"qty":25,"remarks":"0","scripName":"TCS","status":"RMS Rejected","strategyName":"GREEKSOFT","strikePrice":0,"tag":"Ageing","tickSize":0.05000000074505806,"tmplotSize":"0","token":101011536,"tradeSymbol":"TATA CONSULTANCY SERV LT","trdQty":0,"trigPrice":0,"uniqueID":120000007,"uniqueOrderID":"0","userID":"0"},{"BookType":1,"LegInfo":[],"LogTime":1677217778,"OrderFlags":8,"action":1,"amount":0,"assetType":"0","cPANNumber":"0","clientCode":"TEST1","dSLPrice":0,"dSLTPrice":0,"dTargetPrice":0,"description":"TATA CONSULTANCY SERV LT","discQty":0,"errorCode":0,"exchange":"0","expiryDate":0,"filterKey":"0","flowType":"0","iNoOfLegs":0,"iStrategyId":0,"instrument":"EQ","isCancellable":"True","isEditable":"TRUE","lIOMRuleNo":0,"lastModBy":0,"lgoodtilldate":0,"lotSize":1,"multiplier":100,"optionType":"XX","ordID":120000008,"ordLiveDays":0,"ordModTime":0,"ordTime":"24-2-2023 11:19:38","orderType":1,"otype":0,"pendingQty":0,"pendingdiscQty":0,"price":40100,"product":0,"qty":2,"remarks":"0","scripName":"TCS","status":"RMS Rejected","strategyName":"GREEKSOFT","strikePrice":0,"tag":"Ageing","tickSize":0.05000000074505806,"tmplotSize":"0","token":101011536,"tradeSymbol":"TATA CONSULTANCY SERV LT","trdQty":0,"trigPrice":0,"uniqueID":120000008,"uniqueOrderID":"0","userID":"0"},{"BookType":1,"LegInfo":[],"LogTime":1677240103,"OrderFlags":8,"action":1,"amount":1041250,"assetType":"0","cPANNumber":"TDEJHVJH13","clientCode":"TEST1","dSLPrice":0,"dSLTPrice":0,"dTargetPrice":0,"description":"BANKNIFTY 23FEB23","discQty":0,"errorCode":16280,"exchange":"0","expiryDate":1677142800,"filterKey":"0","flowType":"0","iNoOfLegs":0,"iStrategyId":0,"instrument":"FUTIDX","isCancellable":"True","isEditable":"TRUE","lIOMRuleNo":0,"lastModBy":0,"lgoodtilldate":0,"lotSize":25,"multiplier":100,"optionType":"XX","ordID":0,"ordLiveDays":0,"ordModTime":0,"ordTime":"24-2-2023 17:31:43","orderType":1,"otype":1,"pendingQty":25,"pendingdiscQty":0,"price":41650,"product":0,"qty":25,"remarks":"0","scripName":"BANKNIFTY","status":"Exchange Rejected","strategyName":"GREEKSOFT","strikePrice":0,"tag":"","tickSize":0.05000000074505806,"tmplotSize":"0","token":102048756,"tradeSymbol":"BANKNIFTY 23FEB23","trdQty":0,"trigPrice":0,"uniqueID":120000003,"uniqueOrderID":"1100000000003274","userID":"TEST1"},{"BookType":1,"LegInfo":[],"LogTime":1677240196,"OrderFlags":8,"action":1,"amount":1041250,"assetType":"0","cPANNumber":"TDEJHVJH13","clientCode":"TEST1","dSLPrice":0,"dSLTPrice":0,"dTargetPrice":0,"description":"BANKNIFTY 23FEB23","discQty":0,"errorCode":16280,"exchange":"0","expiryDate":1677142800,"filterKey":"0","flowType":"0","iNoOfLegs":0,"iStrategyId":0,"instrument":"FUTIDX","isCancellable":"True","isEditable":"TRUE","lIOMRuleNo":0,"lastModBy":0,"lgoodtilldate":0,"lotSize":25,"multiplier":100,"optionType":"XX","ordID":0,"ordLiveDays":0,"ordModTime":0,"ordTime":"24-2-2023 17:33:16","orderType":1,"otype":1,"pendingQty":25,"pendingdiscQty":0,"price":41650,"product":0,"qty":25,"remarks":"0","scripName":"BANKNIFTY","status":"Exchange Rejected","strategyName":"GREEKSOFT","strikePrice":0,"tag":"","tickSize":0.05000000074505806,"tmplotSize":"0","token":102048756,"tradeSymbol":"BANKNIFTY 23FEB23","trdQty":0,"trigPrice":0,"uniqueID":120000004,"uniqueOrderID":"1100000000003294","userID":"TEST1"}],"message":"","success":"true"}
REJECTED ORDERBOOK
REQUEST TYPE : GET
http://restapi.greeksoft.in:3333/getOrderBookDetailWithLegV2?ZXhjaGFuZ2VUeXBlPUFsbCZDbGllbnRDb2RlPTMmT3JkZXJfU3RhdHVzPVBFTkRJTkcmT3JkZXJ0eXBlPUFsbCZnc2NpZD1URVNUMQ
(exchangeType=All&ClientCode=3&Order_Status=PENDING&Ordertype=All&gscid=TEST1)
RESPONSE:
{"ErrorCode":0,"data":[{"BookType":1,"LegInfo":[],"LogTime":1677241066,"OrderFlags":8,"action":1,"amount":6720,"assetType":"0","cPANNumber":"TDEJHVJH13","clientCode":"TEST1","dSLPrice":0,"dSLTPrice":0,"dTargetPrice":0,"description":"TATA CONSULTANCY SERV LT","discQty":0,"errorCode":0,"exchange":"0","expiryDate":0,"filterKey":"0","flowType":"0","iNoOfLegs":0,"iStrategyId":0,"instrument":"EQ","isCancellable":"True","isEditable":"TRUE","lIOMRuleNo":0,"lastModBy":0,"lgoodtilldate":0,"lotSize":1,"multiplier":100,"optionType":"XX","ordID":0,"ordLiveDays":0,"ordModTime":1361728066,"ordTime":"24-2-2023 17:47:46","orderType":1,"otype":1,"pendingQty":2,"pendingdiscQty":0,"price":3360,"product":0,"qty":2,"remarks":"0","scripName":"TCS","status":"Pending","strategyName":"GREEKSOFT","strikePrice":0,"tag":"","tickSize":0.05000000074505806,"tmplotSize":"0","token":101011536,"tradeSymbol":"TATA CONSULTANCY SERV LT","trdQty":0,"trigPrice":0,"uniqueID":120000011,"uniqueOrderID":"1300000000130700","userID":"TEST1"}],"message":"","success":"true"}
NETPOSITION
NPRequest
Request Type : POST
http://restapi.greeksoft.in:3333/NPRequest
BODY :
{"request":{"FormFactor":"M","data":{"gscid":"TEST1"},"svcGroup":"portfolio","svcVersion":"1.0.0","streaming_type":"NPRequest","request_type":"subscribe"}}
RESPONSE :
{"response":{"svcName":"NPResponse","serverTime":"1677248340000","infoID":"0","streaming_type":"NPResponse","data":{"noofrecords":"1","islast":"2","stockDetails":[{"NSEToken":"101011536","BSEToken":"101011536","token":"101011536","netQty":"4","DayNetAmt":"13492.00","preNetQty":"0","PAmt":"0.00","ProductType":"0","symbol":"TCS","isin":"INE467B01029","instrument":"EQ","description":"TCS","lotQty":"1","sqoffToken":"101011536","account":"TEST1","multiplier":"1","price_multiplier":"1"}]},"appID":"bc90bb525bc9739a9595bb9e176dab17"}}
NPDetailRequest
Request type: POST
http://restapi.greeksoft.in:3333/NPDetailRequest
BODY:
{"request":{"FormFactor":"M","data":{"gscid":"TEST1"},"svcGroup":"portfolio","svcVersion":"1.0.0","streaming_type":"NPDetailRequest","request_type":"subscribe"}}
RESPONSE :
{"response":{"svcName":"NPDetailResponse","serverTime":"1677248268000","infoID":"0","streaming_type":"NPDetailResponse","data":{"noofrecords":"1","islast":"2","stockDetails":[{"NSEToken":"101011536","BSEToken":"101011536","token":"101011536","buyQty":"4","buyAmt":"13492.00","sellQty":"0","sellAmt":"0.00","preNetQty":"0","PAmt":"0.00","ProductType":"0","symbol":"TCS","isin":"INE467B01029","instrument":"EQ","tradeSymbol":"TCS","lotQty":"1","sqoffToken":"101011536","account":"TEST1","multiplier":"1","tickSize":"0.05","expiry_date":"0","option_type":"XX","strike_price":"0.00","ltp":"3571.70","close":"3482.30","price_multiplier":"1"}]},"appID":"bc90bb525bc9739a9595bb9e176dab17"}}
GETNETPOSITIONMTM
Request Type : GET
BODY :
http://restapi.greeksoft.in:3333/getNetPositionMTM?Z3NjaWQ9dGVzdDE
(gscid=test1)
Response :
{"ErrorCode":0,"data":[{"MTM":794.79999999999927}],"message":"","success":"true"}
HOLDINGS
HoldingValueInfo
Request Type : POST
http://restapi.greeksoft.in:3333/HoldingValueInfo
BODY:
{"request":{"FormFactor":"M","data":{"gscid":"pixstox","gcid":"122","sessionId":""},"svcGroup":"portfolio","svcVersion":"1.0.0","streaming_type":"HoldingValueInfo","request_type":"subscribe"}}
RESPONSE :
{"response":{"svcName":"HoldingValueInfoResp","serverTime":"1677249350000","infoID":"0","streaming_type":"HoldingValueInfoResp","data":{"gscid":"pixstox","HValue":"33000.00","CValue":"35717.00"},"appID":"bc90bb525bc9739a9595bb9e176dab17"}}