REST Auth Services
Authorization
{BASE_URL}/auth/login
(http://182.76.70.89:3001/auth/greek/sessiontoken)
Request Type: Post
Description: This is used to get the session-Token that is used for authorization in the REST API Server requests

| Property | Property | Type | Default | Required | Description/Remark |
| --- | --- | --- | --- | --- | --- |
| username |  | String |  | Yes |  |
| password |  | String |  | Yes |  |

{
"username":"TEST1",
"password":"test@123"
}
Description: This is a service given to authenticate the User who is existing In the System
Dependencies: This Username should be available in the CTCL. If the username and password matches with the Gscid and password respectively, A response with the JWT token ( sessionToken ) is received (sample provided below).
All the requests to REST API Server must be having the header property
Authorization: sessionToken
If the token does not match the details or if the token is expired, a Reponse of 401 – UnAuthorized Error is returned. A time period of 4 hrs is set as default expiry period
Every request to the REST API Server must contain request header Authorization as sessionToken like the followingrequest ( i.e.jloginNew )
API Server Commands
Description:-
Every request send to server in base64 encoded formatand received response from server is also in base64 encoded format we need to decode response in base64.
In following document we assume that 3000 is default archane port and 8081 is iris port.(it received from following getflag value request).
GetFlagValue:-
Request Type: Post
Start of the application we first request getFlagValuefor getting all flags related to functionality and server side. And get all ip and port of server.

| Request | http://restapi.greeksoft.in:3333/getFlagValues |


| Parameter | Parameter | Type | Default | Required | Description/Remark |
| --- | --- | --- | --- | --- | --- |
| svcName |  | String | getFlagValues | Yes |  |
| svcGroup |  | String |  | yes |  |
| assetType |  | String |  | Yes |  |

Request Example:-
{
"request": {
"svcVersion": "1.0.0",
"svcGroup": "",
"svcName": "getFlagValues",
"gscid": "",
"assetType": "",
"data": {}
}
}
Response:-
{
"response": {
"svcName": "getFlagValues",
"serverTime": "1450349681701",
"infoID": "0",
"appID": "bc90bb525bc9739a9595bb9e176dab17",
"svcVersion": "1.0.0",
"msgID": "a9bfad10-92ce-4fd7-968f- c25877c1bbb3",
"svcGroup": "",
"ErrorCode": 0,
"data": {
"validateTransaction": "false",
"defaultProduct": "Delivery",
"validate2FA": "false",
"holdingFlag": "false",
"validateGuest": "true",
"validateThrough": "2",
"showLogin": "true",
"heartbeat_Intervals": 10,
"reconnection_attempts": 1800,
"showDescription": "true",
"validatePasswordOnce": "1",
"ft_testing_bypass": "false",
"isSecure": "true",
"Arachne_IP": "tester.greeksoft.in",
"Apollo_IP": "tester.greeksoft.in",
"Iris_IP": "tester.greeksoft.in",
"Arachne_Port": 3000,
"OrderSender_Port": 8081,
"BroadcastSender_Port": 8082,
"Iris_Port": 4246,
"Apollo_Port": 4447,
"ChartSetting": "chartiq",
"IsStrategyProduct": "true",
"IsEDISProduct": "true",
"IsRedisEnabled": "false",
"apr_version": "Version 5.0",
"IsBOReport": "true",
"PaymentGateway": "atom",
"upiPaymentEnabled": "true",
"ft_Link": "https://payment.atomtech.in/paynetz",
"ft_Link_Upi": "https://payment.atomtech.in/paynetz",
"IsPledgeProduct": "true",
"DPType": "CDSL",
"ssl_url": ""
}
},
"config": {
"label": 8,
"message": 9,
"app": 12
}
}
jloginNew:-
Request Type: Post
After getting  response of getflagValue request, we get the archaneip and port for sent the following Login request.

| Request | <Base URL>:3000/jloginNew |


| Parameter | Parameter | Type | Default | Required | Description/Remark |
| --- | --- | --- | --- | --- | --- |
| svcName |  | String | jloginNew | Yes |  |
| svcGroup |  | String | Login | Yes |  |
| data |  |  |  |  |  |
| pan_dob |  | String | N/A | Yes |  |
| deviceId |  | String | N/A | Yes | Getting from Android Setting |
| gscid |  | String | N/A |  | User name  (inputed in username field) |
| deviceDetails |  | String | N/A |  | manufacturer + "-" + model + "-" + version; |
| deviceType |  | String | N/A |  | For 0- Android |
| pass |  | String | N/A |  | Password(input) |
| transPass |  | String | N/A | NO |  |
| userType |  | String | Customer |  |  |
| brokerid |  | String | 1 |  |  |
| passType |  | String | 0 |  |  |
| version_no |  | String | 1.0.1.10 |  |  |
| encryptionType |  | String | 1 |  |  |

Request Example :-
<Base URL>:3000/jloginNew
{
"request": {
"data": {
"pan_dob": "01/01/1901",
"deviceId": "4f89423bab1280c9",
"gscid": "E024",
"deviceDetails": "Genymotion Google Pixel_1-Google Pixel_1-28",
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
{
"response": {
"svcName": "jloginNew",
"serverTime": "1450349681701",
"infoID": "0",
"appID": "bc90bb525bc9739a9595bb9e176dab17",
"svcVersion": "1.0.0",
"msgID": "a9bfad10-92ce-4fd7-968f- c25877c1bbb3",
"svcGroup": "Login",
"sessionId": "$2a$10$YNsnrjRmaCO1VKYluf3yZu",
"ErrorCode": 0,
"data": {
"ClientCode": 8360,
"Executioncode": 0,
"ErrorCode": 0,
"OrderTime": "2",
"Theme": "DarkTheme",
"AllowedMarket": [
{
"market_id": 1
},
{
"market_id": 2
},
{
"market_id": 4
}
],
"defaultProduct": "Intraday",
"holdingFlag": "false",
"validate2FA": "false",
"validateTransaction": "false",
"cCategory": "Retail",
"mandateId": 0,
"userType": 0,
"panNo": "AQPWS5673D",
"KYCStatus": "N",
"dob": "",
"gscid": "E024",
"quote": "Enable",
"clientName": "arun",
"Arachne_IP": "tester.greeksoft.in",
"Apollo_IP": "tester.greeksoft.in",
"Iris_IP": "tester.greeksoft.in",
"Arachne_Port": 3000,
"OrderSender_Port": 8081,
"BroadcastSender_Port": 8082,
"Iris_Port": 4246,
"Apollo_Port": 4447,
"ChartSetting": "chartiq",
"IsStrategyProduct": "true",
"IsEDISProduct": "true",
"IsSameDevice": "true",
"IsValidateSecondary": "true",
"IsRedisEnabled": "false",
"isMPINSet": "true",
"IsBOReport": "false"
}
},
"config": {
"label": 8,
"message": 9,
"app": 12
}
}
Validate Mpin:-
Request Type: Post
After successful response of jloginnew request, need to send ValidateMpinrequestto server. (MPIN created by user).

| Request | <Base URL>:3000/validateMPIN |


| Parameter | Parameter | Type | Default | Required | Description/Remark |
| --- | --- | --- | --- | --- | --- |
| svcName |  | String | validateMPIN | Yes |  |
| svcGroup |  | String | Login | Yes |  |
| data |  |  |  |  |  |
| mpin |  | String | N/A | Yes | input |
| gscid |  | String | N/A | Yes | Getting from Jlogin ‘ClientCode’ |

Request Example:-
{
"request": {
"data": {
"gscid": "E024",
"mpin": "111111"
},
"svcName": "validateMPIN",
"svcGroup": "Login"
}
}
Response Example:-
{
"response": {
"svcName": "validateMPIN",
"serverTime": "1450349681701",
"infoID": "0",
"appID": "bc90bb525bc9739a9595bb9e176dab17",
"svcVersion": "1.0.0",
"msgID": "a9bfad10-92ce-4fd7-968f- c25877c1bbb3",
"svcGroup": "Login",
"ErrorCode": 0,
"data": {
"ErrorCode": 0
}
},
"config": {
"label": 8,
"message": 9,
"app": 12
}
}
Jheartbeat:-
Request Type: Post
After successfully verifiedMpin ,We need to send Jheartbeat request per heartbeat_Intervals(getting from getflagvalue request) to archane server.

| Request | <Base URL>:3000/jheartbeat |


| Parameter | Parameter | Type | Default | Required | Description/Remark |
| --- | --- | --- | --- | --- | --- |
| svcName |  | String | Jheartbeat | Yes |  |
| svcGroup |  | String | Jheartbeat | Yes |  |
| Data |  |  |  |  |  |
| Gscid |  | String | N/A | Yes | Jlogin Response ‘ClientCode’ |
| sessionId |  | String | N/A | Yes | Jlogin Response Session id |

Request Example:-
http://tester.greeksoft.in:3000/jheartbeat
{
"request": {
"data": {
"gscid": "E024",
"sessionId": "$2a$10$fPRC9WUhb6NNPoFX4.D2MO"
},
"svcName": "jheartbeat",
"svcGroup": "jheartbeat"
}
}
Response Example:-
{
"response": {
"svcName": "jheartbeat",
"serverTime": "1450349681701",
"infoID": "0",
"appID": "bc90bb525bc9739a9595bb9e176dab17",
"svcVersion": "1.0.0",
"msgID": "a9bfad10-92ce-4fd7-968f- c25877c1bbb3",
"svcGroup": "jheartbeat",
"ErrorCode": 0,
"data": {
"ErrorCode": 0
}
},
"config": {
"label": 8,
"message": 9,
"app": 12
}
}
IRISLogin Request:-
Type :WebSocekt request
Get iris ip and ordesenderport(e.g. 8081) from getflagvalue response.
After successfully verified Mpin , We need to create websocket and using this websocket  we need to send Login request to iris server .

| Request | ws://<Base URL>:8081 |


| Parameter | Parameter | Type | Default | Required | Description/Remark |
| --- | --- | --- | --- | --- | --- |
| response_format |  | String | Json | Yes |  |
| request_type |  | String | subscribe | Yes |  |
| streaming_type |  | String | login |  |  |
| Data |  |  |  |  |  |
| Gscid |  | String | N/A | Yes |  |
| Gcid |  | String | N/A | Yes | ClientCode from jlogin Response |
| sessionId |  | String | N/A |  | SessionId from Jlogin response |
| device_id |  | String | N/A |  |  |
| device_type |  | String | N/A |  |  |

Reuest Example:-
{
"request": {
"data": {
"gscid": "RET12",
"gcid": "8466",
"sessionId": "$2a$10$XIhIclhEIJtsANllTQHDi.",
"device_id": "a21f0390f4f7d9cc",
"device_type": "0"
},
"response_format": "json",
"request_type": "subscribe",
"streaming_type": "login"
}
}
Response:-
{
"response": {
"svcName": "login",
"serverTime": "1649830062000",
"infoID": "0",
"streaming_type": "LoginResponse",
"data": {
"error_code": "0",
"gscid": "UkVUMTI=",
"gcid": "8466",
"reconnect": "1",
"logtime": "1649829777"
},
"appID": "bc90bb525bc9739a9595bb9e176dab17"
}
}
Iris heartbeat:-
Type :WebSocekt request
After successfully verified Mpin , We need to send Jheartbeat request per heartbeat_Intervals(getting from getflagvalue request) to iris server.

| Request | ws://<Base URL>:8081 |


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
"gcid": "8466",
"sessionId": "$2a$10$ylT59HFlFa6zcqt6Fucq/O"
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
"gcid": "8466",
"apptype": "0"
},
"appID": "bc90bb525bc9739a9595bb9e176dab17"
}
}
If heart beat response not received 3 times then Login request send to iris. And if in heart beat response error code other than 0 then user getting logged out.
AllowedProduct:-
Request Type: Post
Getting all allowed product.

| Request | <Base URL>:3000/getAllowedProduct |


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
GetMarketStatus:-
Request Type: Post
Getting market status.

| Request | <Base URL>:3000/getMarketStatus |


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
"gscid": "E026"
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
GetWatchlistGroup:-
Request Type: Post
Get Watchlist group created by user and getting Symbol list of default group with symbol token(every symbol is different token in different exchange). Token are used for order request.

| Request | <Base URL>:3000/getWatchlistGroupsNew_MobileV2 |


| Parameter | Parameter | Type | Default | Required | Description/Remark |
| --- | --- | --- | --- | --- | --- |
| svcName |  | String | getWatchlistGroupsNew_MobileV2 | Yes |  |
| svcGroup |  | String | Portfolio | Yes |  |
| Data |  |  |  |  |  |
| Gscid |  | String | N/A |  |  |

Request Example:-
{
"request": {
"data": {
"gscid": "E024"
},
"svcName": "getWatchlistGroupsNew_MobileV2",
"svcGroup": "Portfolio"
}
}
Response:-
{
"response": {
"svcName": "getWatchlistGroupsNew_MobileV2",
"serverTime": "1450349681701",
"infoID": "0",
"appID": "bc90bb525bc9739a9595bb9e176dab17",
"svcVersion": "1.0.0",
"msgID": "a9bfad10-92ce-4fd7-968f- c25877c1bbb3",
"svcGroup": "Portfolio",
"ErrorCode": 0,
"data": {
"getwatchlistdata": [
{
"watchtype": "user",
"watchlistName": "WatchList1",
"symbolList": [
{
"lot": 1,
"exchange": "BSE",
"p_change": 0,
"instrumentName": "F",
"ScriptName": "150HDFCL27A",
"token": 201956208,(Token)----------------------------------
"multiplier": 1,
"change": 10000000,
"assetType": "Equity",
"close": 0,
"tradeSymbol": "HDFCL-1.50%-24-4-27-PVT",
"tickSize": 0.01,
"description": "HDFCL-1.50%-24-4-27-PVT",
"ltp": 10000000,
"optionType": "XX",
"strickPrice": 0,
"expiryDate": 0,
"seqNo": 0
}
],
"default": "true"
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
getWatchlistDataByGroupName_MobileV2:-
Request Type: Post
Get symbol list of selected watchlist group.

| Request | <Base URL>:3000/ getWatchlistDataByGroupName_MobileV2 |


| Parameter | Parameter | Type | Default | Required | Description/Remark |
| --- | --- | --- | --- | --- | --- |
| svcName |  | String | getWatchlistDataByGroupName_MobileV2 | Yes |  |
| svcGroup |  | String | Portfolio | Yes |  |
| data |  |  |  |  |  |
| gscid |  | String |  | Yes |  |
| WatchListType |  | String |  | Yes |  |
| WatchListGroup |  | String |  | Yes |  |

Request Example:-
{
"request": {
"data": {
"gscid": "RET11",
"WatchListType": "USER",
"WatchListGroup": "WatchList2"
},
"svcName": "getWatchlistDataByGroupName_MobileV2",
"svcGroup": "Portfolio"
}
}
Response:-
{
"response": {
"svcName": "getWatchlistDataByGroupName_MobileV2",
"serverTime": "1450349681701",
"infoID": "0",
"appID": "bc90bb525bc9739a9595bb9e176dab17",
"svcVersion": "1.0.0",
"msgID": "a9bfad10-92ce-4fd7-968f- c25877c1bbb3",
"svcGroup": "Portfolio",
"ErrorCode": 0,
"data": {
"getwatchlistdata": [
{
"watchtype": "user",
"watchlistName": "WatchList2",
"symbolList": [
{
"lot": 1,
"exchange": "BSE",
"p_change": 0,
"instrumentName": "F",
"ScriptName": "12VDPL22",
"token": 201956741,
"multiplier": 1,
"change": 0,
"assetType": "Equity",
"close": 0,
"tradeSymbol": "VDPL-12%-30-6-22-PVT",
"tickSize": 0.01,
"description": "VDPL-12%-30-6-22-PVT",
"ltp": 0,
"optionType": "XX",
"strickPrice": 0,
"expiryDate": 0,
"seqNo": 0
},
{
"lot": 1,
"exchange": "NSE",
"p_change": -1.7226761909915762,
"instrumentName": "EQ",
"ScriptName": "HDFC",
"token": 101001330,
"multiplier": 1,
"change": -47.75,
"assetType": "Equity",
"close": 2771.85,
"tradeSymbol": "HDFC LTD",
"tickSize": 0.05,
"description": "HDFC LTD",
"ltp": 2724.1,
"optionType": "XX",
"strickPrice": 0,
"expiryDate": 0,
"seqNo": 1
},
{
"lot": 1,
"exchange": "NSE",
"p_change": -0.933608521601825,
"instrumentName": "EQ",
"ScriptName": "TCS",
"token": 101011536,
"multiplier": 1,
"change": -33.70000000000027,
"assetType": "Equity",
"close": 3609.65,
"tradeSymbol": "TATA CONSULTANCY SERV LT",
"tickSize": 0.05,
"description": "TATA CONSULTANCY SERV LT",
"ltp": 3575.95,
"optionType": "XX",
"strickPrice": 0,
"expiryDate": 0,
"seqNo": 2
}
],
"default": "true"
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
OrderBook
Pending Screen:-
Request Type: Get
Get All pending orders with all details.

| Request | <Base URL>:3000/getOrderBookDetailWithLegV2?ZXhjaGFuZ2VUeXBlPUFsbCZDbGllbnRDb2RlPTg0NjAmT3JkZXJfU3RhdHVzPVBFTkRJTkdfQkFKQUomT3JkZX J0eXBlPUFsbCZnc2NpZD1SRVQxMQ== |


| Parameter | Parameter | Type | Default | Required | Description/Remark |
| --- | --- | --- | --- | --- | --- |
| exchangeType |  | String | All | Yes |  |
| ClientCode |  | String | N/A | Yes |  |
| Order_Status |  | String | PENDING_BAJAJ | Yes |  |
| Ordertype |  | String | All |  |  |
| Gscid |  | String | N/A | Yes |  |

Request Example:-
http://tester.greeksoft.in:3000/getOrderBookDetailWithLegV2?ZXhjaGFuZ2VUeXBlPUFsbCZDbGllbnRDb2RlPTg0NjAmT3JkZXJfU3RhdHVzPVBFTkRJTkdfQkFKQUomT3JkZXJ0eXBlPUFsbCZnc2NpZD1SRVQxMQ==
exchangeType=All&ClientCode=8413&Order_Status=PENDING_BAJAJ&Ordertype=All&gscid=SRET1
Executed Screen:-
Request Type: Get
Get alltradeds orders with all details.

| Request | <Base URL>:3000/getOrderBookDetailWithLegV2?ZXhjaGFuZ2VUeXBlPUFsbCZDbGllbnRDb2RlPTg0NjAmT3JkZXJfU3RhdHVzPVRSQURFRCZPcmRlcnR5cGU9QWxsJmdzY2lkPVJFVDEx |


| Parameter | Parameter | Type | Default | Required | Description/Remark |
| --- | --- | --- | --- | --- | --- |
| exchangeType |  | String | All | Yes |  |
| ClientCode |  | String | N/A | Yes |  |
| Order_Status |  | String | TRADED | Yes |  |
| Ordertype |  | String | All |  |  |
| Gscid |  | String | N/A | Yes |  |

Request Example:-
http://tester.greeksoft.in:3000/getOrderBookDetailWithLegV2?ZXhjaGFuZ2VUeXBlPUFsbCZDbGllbnRDb2RlPTg0NjAmT3JkZXJfU3RhdHVzPVRSQURFRCZPcmRlcnR5cGU9QWxsJmdzY2lkPVJFVDEx
Rejected Screen:-
Request Type: Get
Get all rejected orders with all details.

| Request | <Base URL>:3000/getOrderBookDetailWithLegV2?ZXhjaGFuZ2VUeXBlPUFsbCZDbGllbnRDb2RlPTg0NjAmT3JkZXJfU3RhdHVzPVJNUyBSRUpFQ1RFRCZPcmRlcnR5cGU9QWxsJmdzY2lkPVJFVDEx |


| Parameter | Parameter | Type | Default | Required | Description/Remark |
| --- | --- | --- | --- | --- | --- |
| exchangeType |  | String | All | Yes |  |
| ClientCode |  | String | N/A | Yes |  |
| Order_Status |  | String | RMS REJECTED | Yes |  |
| Ordertype |  | String | All |  |  |
| Gscid |  | String | N/A | Yes |  |

Request Example:-
<Base URL>:3000/getOrderBookDetailWithLegV2?ZXhjaGFuZ2VUeXBlPUFsbCZDbGllbnRDb2RlPTg0NjAmT3JkZXJfU3RhdHVzPVJNUyBSRUpFQ1RFRCZPcmRlcnR5cGU9QWxsJmdzY2lkPVJFVDEx
Cancelled Screen:-
Request Type: Get
Get all cancelled orders with all details.

| Request | http://tester.greeksoft.in:3000/getOrderBookDetailWithLegV2?ZXhjaGFuZ2VUeXBlPUFsbCZDbGllbnRDb2RlPTg0NjAmT3JkZXJfU3RhdHVzPVJNUyBSRUpFQ1RFRCZPcmRlcnR5cGU9QWxsJmdzY2lkPVJFVDEx |


| Parameter | Parameter | Type | Default | Required | Description/Remark |
| --- | --- | --- | --- | --- | --- |
| exchangeType |  | String | All | Yes |  |
| ClientCode |  | String | N/A | Yes |  |
| Order_Status |  | String | CANCELLED | Yes |  |
| Ordertype |  | String | All |  |  |
| Gscid |  | String | N/A | Yes |  |

Request Example:-
<Base URL>:3000/getOrderBookDetailWithLegV2?ZXhjaGFuZ2VUeXBlPUFsbCZDbGllbnRDb2RlPTg0NjAmT3JkZXJfU3RhdHVzPUNBTkNFTExFRCZPcmRlcnR5cGU9QWxsJmdzY2lkPVJFVDEx
Common response for all above get request.
Response:-
{
"success": "true",
"message": "",
"ErrorCode": 0,
"data": [
{
"ordLiveDays": 0,
"ordTime": "29-12-2020 12:54:29",
"uniqueID": 120010007,
"product": 0,
"ordID": 0,
"exchange": "0",
"trdQty": 0,
"remarks": "0",
"isCancellable": "True",
"amount": 0,
"token": 101005258,
"discQty": 0,
"uniqueOrderID": "0",
"multiplier": 100,
"qty": 1,
"isEditable": "TRUE",
"orderType": 1,
"lastModBy": "E026",
"ordLife": 0,
"assetType": "0",
"trigPrice": 0,
"lotSize": 1,
"ordModTime": 0,
"tradeSymbol": "INDUSIND BANK LIMITED",
"tickSize": 0.05,
"pendingQty": 1,
"status": "Unconfirmed",
"clientCode": "E026",
"price": 0,
"action": 1,
"description": "INDUSINDBANKLIMITED",
"userID": "E026",
"tmplotSize": "0",
"filterKey": "0",
"flowType": "0",
"pendingdiscQty": 0,
"LogTime": 1609226669,
"BookType": 1,
"OrderFlags": 8,
"instrument": "EQ",
"lgoodtilldate": 0,
"errorCode": 101,
"optionType": "XX",
"strikePrice": 0,
"expiryDate": 0,
"otype": 5,
"scripName": "INDUSINDBK",
"dSLPrice": 0,
"dTargetPrice": 0,
"dSLTPrice": 0,
"lIOMRuleNo": 0,
"iStrategyId": 0,
"cPANNumber": "AADDI4444A",
"NoOfLegs": 0,
"strategyName": null,
"tag": "",
"LegInfo": []
}
]
}
getQuoteForSingleSymbol_V2:-
Request Type: Post
Get all details of selected script. (In request send Token of script getting from getWatchlistGroupsNew_MobileV2 )

| Request | <Base URL>:3000/getQuoteForSingleSymbol_V2 |


| Parameter | Parameter | Type | Default | Required | Description/Remark |
| --- | --- | --- | --- | --- | --- |
| svcName |  | String | getQuoteForSingleSymbol_V2 | Yes |  |
| svcGroup |  | String | Markets | Yes |  |
| data |  |  |  |  |  |
| token |  | String |  | Yes |  |
| assetType |  | String |  | Yes |  |
| gscid |  | String |  | Yes |  |
| gcid |  | String |  | Yes |  |

Request Example:-
{
"request": {
"data": {
"token": "101011536",
"assetType": "equity",
"gscid": "RET11",
"gcid": "8461"
},
"svcName": "getQuoteForSingleSymbol_V2",
"svcGroup": "Markets"
}
}
Response Example:-
{
"response": {
"svcName": "getQuoteForSingleSymbol_V2",
"serverTime": "1450349681701",
"infoID": "0",
"appID": "bc90bb525bc9739a9595bb9e176dab17",
"svcVersion": "1.0.0",
"msgID": "a9bfad10-92ce-4fd7-968f- c25877c1bbb3",
"svcGroup": "Markets",
"ErrorCode": 0,
"data": {
"ylow": 3004,
"lot": 1,
"instrument": "EQ",
"yhigh": 4043,
"p_change": 2.2825,
"last": 3775.35,
"high": 3780,
"change": 84.25,
"open": 3762,
"oi": 0,
"close": 3691.1,
"tot_vol": 1254906,
"symbol": "TCS",
"low": 3737.1,
"description": "TATA CONSULTANCY SERV LT",
"token": 101011536,
"expiryDate": 0,
"strikeprice": 0,
"optiontype": "XX",
"level2": [
{
"bid": {
"price": 3775,
"no": 1,
"qty": 15
},
"ask": {
"price": 3775.35,
"no": 3,
"qty": 37
}
},
{
"bid": {
"price": 3774.45,
"no": 1,
"qty": 150
},
"ask": {
"price": 3775.4,
"no": 2,
"qty": 13
}
},
{
"bid": {
"price": 3774.3,
"no": 2,
"qty": 54
},
"ask": {
"price": 3775.7,
"no": 2,
"qty": 40
}
},
{
"bid": {
"price": 3774.25,
"no": 1,
"qty": 49
},
"ask": {
"price": 3775.85,
"no": 1,
"qty": 8
}
},
{
"bid": {
"price": 3774.15,
"no": 1,
"qty": 150
},
"ask": {
"price": 3775.9,
"no": 2,
"qty": 57
}
}
],
"lowRange": 3322,
"highRange": 4060.2,
"isinumber": "INE467B01029",
"atp": 3766.53,
"assetToken": 0,
"assetLtp": 0,
"oi_pChange": 0,
"ask": 3775.35,
"bid": 3775,
"freezQty": 25893,
"sqOffQty": 0,
"authorizedQty": 0,
"tot_buyQty": 141113,
"tot_sellQty": 686033,
"tickSize": 0.05,
"ltt": "04-4-2022 14:48:51",
"reason": ""
}
},
"config": {
"label": 8,
"message": 9,
"app": 12
}
}
NewOrderRequest:-
Type :WebSocekt request
Before send new Order request first check market status if market is close then offline order sent. Or if select order type as a amo(After Market Order) then sent as a amo order.
When user clicked on buy butten firstly check iris server is connected or not if connected then allow to send order.

| Request | ws://tester.greeksoft.in:8081 |


| Parameter | Parameter | Type | Default | Required | Description/Remark |
| --- | --- | --- | --- | --- | --- |
| response_format |  | String | Json | Yes |  |
| request_type |  | String | subscribe | Yes |  |
| streaming_type |  | String | NewOrderRequest |  |  |
| data |  |  |  |  |  |
| trigger_price |  | String | N/A | Yes |  |
| gtoken |  | String | N/A | Yes | Token from getQuoteForSingleSymbol_V2 |
| side |  | String | N/A |  | Buy/Sell |
| gcid |  | String | N/A |  | Client Code |
| validity |  | String | N/A |  | Day/ioc/GTD |
| price |  | String | N/A |  |  |
| exchange |  | String | N/A |  |  |
| disclosed_qty |  | String |  |  |  |
| tradeSymbol |  | String | N/A |  |  |
| lot |  | String | N/A |  | lot from getQuoteForSingleSymbol_V2 |
| order_type |  | String | N/A |  | Selected order type |
| product |  | String | N/A |  | Selected product id(allowed product ->iProductToken) |
| qty |  | String | N/A |  |  |
| corderid |  | String | N/A |  | Number to place order from user logged in |
| amo |  | String | N/A |  | If market close and send order then select amoinorder type to set 1 other wise 0 |
| gtdExpiry |  | String | N/A |  | If validity select gtd send date in timestamp |
| is_post_closed |  | String | N/A |  | Market status |
| is_preopen_order |  | String | N/A |  | Market status |
| isSqOffOrder |  | String | N/A |  | Set 0 for new order |
| offline |  | String | N/A |  | Set 0 for within market, after maket set 1 |

Request Example:-
{
"request": {
"data": {
"trigger_price": "0",
"gtoken": "101011536",
"side": "1",
"gcid": "8461",
"validity": "0",
"price": "3322",
"exchange": "NSE",
"disclosed_qty": "0",
"tradeSymbol": "TCS",
"lot": "1",
"order_type": "1",
"product": "0",
"qty": "1",
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
Response:-
{
"response": {
"svcName": "order",
"serverTime": "1649914034000",
"infoID": "0",
"streaming_type": "OrderResponse",
"data": {
"side": "1",
"qty": "1",
"product": "0",
"gtoken": "101011536",
"order_status": "Pending",
"eorderid": "20220414000002",
"gorderid": "120000004",
"lu_time_exchange": "1334401099",
"lu_time": "1649914099",
"symbol": "TATA CONSULTANCY SERV LT",
"regular_lot": "1",
"validity": "8",
"order_type": "1",
"price": "3322.00",
"order_state": "0",
"trigger_price": "0.00",
"disclosed_qty": "0",
"code": "0",
"reason": "",
"pending_qty": "1",
"pending_disclosed_qty": "0",
"qty_filled_today": "0",
"goodTillDate": "0",
"cancelledBy": "",
"expiryDate": "0",
"tradeSymbol": "TCS",
"instrument": "EQ",
"optionType": "XX",
"strikePrice": "0.00"
},
"appID": "bc90bb525bc9739a9595bb9e176dab17"
}
}
CancelOrderRequest:-
Type :WebSocekt request
Select order tab from bottom tab.
Go to Pending tab select order .
Click on Cancel button to send request to iris with token for cancel order.(Only Pending order can cancelled)

| Request | ws://<Base URL>:8081 |


| Parameter | Parameter | Type | Default | Required | Description/Remark |
| --- | --- | --- | --- | --- | --- |
| response_format |  | String | Json | Yes |  |
| request_type |  | String | subscribe | Yes |  |
| streaming_type |  | String | NewOrderRequest |  |  |
| appID |  | String |  | Yes |  |
| Data |  |  |  |  |  |
| trigger_price |  | String | N/A | Yes |  |
| iStrategyNo |  | String |  | Yes | iStrategyId from order book response |
| Gtoken |  | String | N/A | Yes | Token from getQuoteForSingleSymbol_V2 |
| Side |  | String | N/A | Yes |  |
| Gcid |  | String | N/A | Yes |  |
| Validity |  | String | N/A | Yes |  |
| Price |  | String | N/A | Yes |  |
| Exchange |  | String | N/A | Yes |  |
| disclosed_qty |  | String | N/A | Yes |  |
| tradeSymbol |  | String | N/A | Yes |  |
| Lot |  | String | N/A | Yes |  |
| order_type |  | String | N/A | Yes |  |
| Product |  | String | N/A | Yes |  |
| Qty |  | String | N/A | Yes |  |
| lu_time_exchange |  | String | N/A | Yes | ordModTime from orderbook response |
| pending_disclosed_qty |  | String | N/A | Yes | pendingdiscQty from Orderbook response |
| pending_qty |  | String | N/A | Yes | pendingQty from orderbook response |
| qty_filled_today |  | String | N/A | Yes | trdQty from Orderbookresponse |
| Gorderid |  | String | N/A | Yes | uniqueID from Orderook response |
| Eorderid |  | String | N/A | Yes | uniqueOrderID from Order book response |
| Amo |  | String | N/A | Yes | Otype=6 from Order book response |
| Offline |  | String | N/A | Yes | Otype=5 from Order book response |
| lexchangeOrderNo1 |  | String | N/A | Yes | ordID from Order book response. |
| is_preopen_order |  | String | N/A | Yes | Market status |
| is_post_closed |  | String | N/A | Yes | Market status |
| gtdExpiry |  | String | N/A | Yes | Lgoodtilldate from order book response |
| iomRuleNo |  | String | N/A | Yes | iomRuleNo from Orderbook response |

Request Example:-
{
"request": {
"data": {
"trigger_price": "0",
"iStrategyNo": "0",
"gtoken": "101011536",
"side": "1",
"gcid": "8461",
"validity": "0",
"price": "3322",
"exchange": "NSE",
"disclosed_qty": "0",
"tradeSymbol": "TATA CONSULTANCY SERV LT",
"lot": "1",
"order_type": "1",
"product": "0",
"qty": "2",
"lu_time_exchange": "1334401491",
"pending_disclosed_qty": "1",
"pending_qty": "2",
"qty_filled_today": "0",
"gorderid": "120000004",
"eorderid": "20220414000002",
"amo": "0",
"offline": "0",
"lexchangeOrderNo1": "0",
"is_preopen_order": "0",
"is_post_closed": "0",
"gtdExpiry": 0,
"iomRuleNo": "0"
},
"response_format": "json",
"request_type": "subscribe",
"streaming_type": "CancelOrderRequest"
}
}
Response:-
{
"response": {
"svcName": "order",
"serverTime": "1649914579000",
"infoID": "0",
"streaming_type": "OrderResponse",
"data": {
"side": "1",
"qty": "2",
"product": "0",
"gtoken": "101011536",
"order_status": "Cancelled",
"eorderid": "20220414000002",
"gorderid": "120000004",
"lu_time_exchange": "1334401644",
"lu_time": "1649914644",
"symbol": "TATA CONSULTANCY SERV LT",
"regular_lot": "1",
"validity": "520",
"order_type": "1",
"price": "3322.00",
"order_state": "2",
"trigger_price": "0.00",
"disclosed_qty": "0",
"code": "0",
"reason": "",
"pending_qty": "2",
"pending_disclosed_qty": "1",
"qty_filled_today": "0",
"goodTillDate": "0",
"cancelledBy": "T",
"expiryDate": "0",
"tradeSymbol": "TCS",
"instrument": "EQ",
"optionType": "XX",
"strikePrice": "0.00"
},
"appID": "bc90bb525bc9739a9595bb9e176dab17"
}
}
Modify Request:-
Type :WebSocektrequeast
Select order tab from bottom tab.
Go to Pending tab select order .
Click on modify button to open buy sell window and modify order (like price quantity order type(Market/Limit)).
And click on buy/sell button to modify order.(Only Pending order can Modify)

| Request | ws://<Base URL>:8081 |


| Parameter | Parameter | Type | Default | Required | Description/Remark |
| --- | --- | --- | --- | --- | --- |
| response_format |  | String | Json | Yes |  |
| request_type |  | String | subscribe | Yes |  |
| streaming_type |  | String | ModifyOrderRequest |  |  |
| appID |  | String |  | Yes |  |
| Data |  |  |  |  |  |
| trigger_price |  | String | N/A | Yes |  |
| iStrategyNo |  | String |  | Yes | iStrategyId from order book response |
| Gtoken |  | String | N/A | Yes | Token |
| Side |  | String | N/A | Yes |  |
| Gcid |  | String | N/A | Yes |  |
| Validity |  | String | N/A | Yes | Validity from Order book response 0- day 1 – IOC 3- GTD |
| Price |  | String | N/A | Yes |  |
| Exchange |  | String | N/A | Yes |  |
| disclosed_qty |  | String | N/A | Yes |  |
| tradeSymbol |  | String | N/A | Yes |  |
| Lot |  | String | N/A | Yes |  |
| order_type |  | String | N/A | Yes |  |
| Product |  | String | N/A | Yes |  |
| Qty |  | String | N/A | Yes |  |
| lu_time_exchange |  | String | N/A | Yes | ordModTime from orderbook response |
| pending_disclosed_qty |  | String | N/A | Yes | pendingdiscQty from Orderbook response |
| pending_qty |  | String | N/A | Yes | pendingQty from orderbook response |
| qty_filled_today |  | String | N/A | Yes | trdQty from Orderbook response |
| Gorderid |  | String | N/A | Yes | uniqueID from Orderook response |
| Eorderid |  | String | N/A | Yes | uniqueOrderID from Order book response |
| Amo |  | String | N/A | Yes | Otype=6 from Order book response |
| Offline |  | String | N/A | Yes | Otype=5 from Order book response |
| lexchangeOrderNo1 |  | String | N/A | Yes | ordID from Order book response. |
| is_preopen_order |  | String | N/A | Yes | Market status |
| is_post_closed |  | String | N/A | Yes | Market status |
| gtdExpiry |  | String | N/A | Yes | Lgoodtilldate from order book response |
| iomRuleNo |  | String | N/A | Yes | iomRuleNo from Orderbook response |

Request Example:
{
"request": {
"data": {
"trigger_price": "0",
"gtoken": "101011536",
"side": "1",
"gcid": "8461",
"validity": "0",
"price": "3322.00",
"exchange": "NSE",
"disclosed_qty": "0",
"tradeSymbol": "TCS",
"lot": "1",
"order_type": "1",
"product": "0",
"qty": "2",
"lu_time_exchange": "1334401099",
"pending_disclosed_qty": "1",
"pending_qty": "1",
"qty_filled_today": "0",
"gorderid": "120000004",
"eorderid": "20220414000002",
"lexchangeOrderNo1": "0",
"amo": "0",
"offline": "0",
"gtdExpiry": 0,
"is_preopen_order": "0",
"is_post_closed": "0",
"iomRuleNo": "0",
"iStrategyNo": "0",
"isSqOffOrder": "false"
},
"response_format": "json",
"request_type": "subscribe",
"streaming_type": "ModifyOrderRequest"
}
}
Response:
{
"response": {
"svcName": "order",
"serverTime": "1649914426000",
"infoID": "0",
"streaming_type": "OrderResponse",
"data": {
"side": "1",
"qty": "2",
"product": "0",
"gtoken": "101011536",
"order_status": "Pending",
"eorderid": "20220414000002",
"gorderid": "120000004",
"lu_time_exchange": "1334401491",
"lu_time": "1649914491",
"symbol": "TATA CONSULTANCY SERV LT",
"regular_lot": "1",
"validity": "520",
"order_type": "1",
"price": "3322.00",
"order_state": "1",
"trigger_price": "0.00",
"disclosed_qty": "0",
"code": "0",
"reason": "",
"pending_qty": "2",
"pending_disclosed_qty": "1",
"qty_filled_today": "0",
"goodTillDate": "0",
"cancelledBy": "T",
"expiryDate": "0",
"tradeSymbol": "TCS",
"instrument": "EQ",
"optionType": "XX",
"strikePrice": "0.00"
},
"appID": "bc90bb525bc9739a9595bb9e176dab17"
}
}
getLoginInfo:-
Request Type: Post
Get the info required for requests like .

| Request | <Base URL>:3000/ getLoginInfo |


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
"gcid": <GCID>,
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
getFullScripDetailsBySymbol_Mobile
Request-
http://restapi.greeksoft.in:3333/getFullScripDetailsBySymbol_Mobile?ZXhjaGFuZ2U9TlNFJmFzc2V0VHlwZT1mdXR1cmUmY29kZT1Ra0ZLUVVvdFFWVlVUdz09JnR5cGU9ZnV0dXJl
exchange=NSE&assetType=future&code=BAJAJ-AUTO==&type=future
Response-
{"success":"true","message":"","ErrorCode":0,
"data":[{"UniqueId":49961,"token":102049961,"instrumentName":"FUTSTK",
"ScriptName":"BAJAJ-AUTO","Series":"FUTSTK","expiryDate":1611824400,
"strickPrice":0,"OptionType":"XX","Name":"BAJAJ-AUTO28JAN21","exchange":"NSE",
"tradeSymbol":"BAJAJ-AUTO28JAN21","description":"BAJAJ-AUTO28JAN21",
"assetType":"future","lotQty":250,"multiplier":1,"tickSize":0.05}]}
getFullScripDetailsBySymbol_Option
Request-
http://restapi.greeksoft.in:3333/getFullScripDetailsBySymbol_Option?ZXhjaGFuZ2U9TlNFJmFzc2V0VHlwZT1mdXR1cmUmY29kZT1Ra0ZLUVVvdFFWVlVUdz09JnR5cGU9Y2FsbG9wdGlvbiZleHBpcnk9MTYxMTgyNDQwMA==
exchange=NSE&assetType=future&code=QkFKQUotQVVUTw==&type=calloption&expiry=1611824400
Response-
{"success":"true","message":"","ErrorCode":0,"data":[{"UniqueId":35677,"token":102035677,"instrumentName":"OPTSTK","ScriptName":"BAJAJ-AUTO","Series":"OPTSTK","expiryDate":1611824400,"strickPrice":1650,"OptionType":"CE","Name":"BAJAJ-AUTO28JAN21CE1650.00","exchange":"NSE","tradeSymbol":"BAJAJ-AUTO28JAN21CE1650.00","description":"BAJAJ-AUTO28JAN21CE1650.00","assetType":"future","lotQty":250,"multiplier":1,"tic
kSize":0.05}]}
getFullScripDetailsBySymbol_Expiry
Request-
http://restapi.greeksoft.in:3333/getFullScripDetailsBySymbol_Expiry?ZXhjaGFuZ2U9TlNFJmFzc2V0VHlwZT1mdXR1cmUmY29kZT1Ra0ZLUVVvdFFWVlVUdz09JnR5cGU9Y2FsbG9wdGlvbg==
exchange=NSE&assetType=future&code=QkFKQUotQVVUTw==&type=calloption
Respone-
{"success":"true","message":"","ErrorCode":0,"data":[{"expiry":1611824400},{"expiry":1614243600},{"expiry":1616662800}]}
getFullScripDetailsBySymbol_Mobile
FUTURE:
Request :
http://restapi.greeksoft.in:3333/getFullScripDetailsBySymbol_Mobile?ZXhjaGFuZ2U9TlNFJmFzc2V0VHlwZT1mdXR1cmUmY29kZT1Va1ZNU1VGT1EwVT09JnR5cGU9ZnV0dXJl
exchange=NSE&assetType=future&code=UkVMSUFOQ0U==&type=future
UkVMSUFOQ0U - Reliance
Response :
{"ErrorCode":0,"data":[{"Name":"RELIANCE 23FEB23","OptionType":"XX","ScriptName":"RELIANCE","Series":"FUTSTK","UniqueId":57701,"assetType":"future","description":"RELIANCE 23FEB23","exchange":"nse","expiryDate":1677142800,"instrumentName":"FUTSTK","lotQty":250,"multiplier":1,"strickPrice":0,"tickSize":0.050000000000000003,"token":102057701,"tradeSymbol":"RELIANCE 23FEB23"},{"Name":"RELIANCE 29MAR23","OptionType":"XX","ScriptName":"RELIANCE","Series":"FUTSTK","UniqueId":52481,"assetType":"future","description":"RELIANCE 29MAR23","exchange":"nse","expiryDate":1680080400,"instrumentName":"FUTSTK","lotQty":250,"multiplier":1,"strickPrice":0,"tickSize":0.050000000000000003,"token":102052481,"tradeSymbol":"RELIANCE 29MAR23"},{"Name":"RELIANCE 27APR23","OptionType":"XX","ScriptName":"RELIANCE","Series":"FUTSTK","UniqueId":53063,"assetType":"future","description":"RELIANCE 27APR23","exchange":"nse","expiryDate":1682586000,"instrumentName":"FUTSTK","lotQty":250,"multiplier":1,"strickPrice":0,"tickSize":0.050000000000000003,"token":102053063,"tradeSymbol":"RELIANCE 27APR23"}],"message":"","success":"true"}
EQUITY:
Request :
http://restapi.greeksoft.in:3333/getFullScripDetailsBySymbol_Mobile?ZXhjaGFuZ2U9TlNFJmFzc2V0VHlwZT1lcXVpdHkmY29kZT1Va1ZNU1VGT1EwVT09JnR5cGU9ZXF1aXR5
exchange=NSE&assetType=equity&code=UkVMSUFOQ0U==&type=equity
Response :
{"ErrorCode":0,"data":[{"Name":"RELIANCE","OptionType":"XX","ScriptName":"RELIANCE","Series":"EQ","UniqueId":2885,"assetType":"equity","description":"RELIANCE","exchange":"nse","expiryDate":0,"instrumentName":"EQ","lotQty":1,"multiplier":1,"strickPrice":0,"tickSize":0.050000000000000003,"token":101002885,"tradeSymbol":"RELIANCE"}],"message":"","success":"true"}
OPTION:
Request :
http://restapi.greeksoft.in:3333/getFullScripDetailsBySymbol_Mobile?ZXhjaGFuZ2U9TlNFJmFzc2V0VHlwZT1mdXR1cmUmY29kZT1jbVZzYVdGdVkyVT09JnR5cGU9Y2FsbG9wdGlvbg
exchange=NSE&assetType=future&code=cmVsaWFuY2U==&type=calloption
Response:
{"ErrorCode":0,"data":[{"Name":"RELIANCE 23FEB23 CE 1300","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":39992,"assetType":"future","description":"RELIANCE 23FEB23 CE 1300","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":1300,"tickSize":0.050000000000000003,"token":102039992,"tradeSymbol":"RELIANCE 23FEB23 CE 1300"},{"Name":"RELIANCE 23FEB23 CE 1320","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":39998,"assetType":"future","description":"RELIANCE 23FEB23 CE 1320","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":1320,"tickSize":0.050000000000000003,"token":102039998,"tradeSymbol":"RELIANCE 23FEB23 CE 1320"},{"Name":"RELIANCE 23FEB23 CE 1340","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":142548,"assetType":"future","description":"RELIANCE 23FEB23 CE 1340","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":1340,"tickSize":0.050000000000000003,"token":102142548,"tradeSymbol":"RELIANCE 23FEB23 CE 1340"},{"Name":"RELIANCE 23FEB23 CE 1360","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":142550,"assetType":"future","description":"RELIANCE 23FEB23 CE 1360","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":1360,"tickSize":0.050000000000000003,"token":102142550,"tradeSymbol":"RELIANCE 23FEB23 CE 1360"},{"Name":"RELIANCE 23FEB23 CE 1380","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":52969,"assetType":"future","description":"RELIANCE 23FEB23 CE 1380","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":1380,"tickSize":0.050000000000000003,"token":102052969,"tradeSymbol":"RELIANCE 23FEB23 CE 1380"},{"Name":"RELIANCE 23FEB23 CE 1400","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":44733,"assetType":"future","description":"RELIANCE 23FEB23 CE 1400","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":1400,"tickSize":0.050000000000000003,"token":102044733,"tradeSymbol":"RELIANCE 23FEB23 CE 1400"},{"Name":"RELIANCE 23FEB23 CE 1420","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":40722,"assetType":"future","description":"RELIANCE 23FEB23 CE 1420","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":1420,"tickSize":0.050000000000000003,"token":102040722,"tradeSymbol":"RELIANCE 23FEB23 CE 1420"},{"Name":"RELIANCE 23FEB23 CE 1440","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":44532,"assetType":"future","description":"RELIANCE 23FEB23 CE 1440","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":1440,"tickSize":0.050000000000000003,"token":102044532,"tradeSymbol":"RELIANCE 23FEB23 CE 1440"},{"Name":"RELIANCE 23FEB23 CE 1460","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":50989,"assetType":"future","description":"RELIANCE 23FEB23 CE 1460","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":1460,"tickSize":0.050000000000000003,"token":102050989,"tradeSymbol":"RELIANCE 23FEB23 CE 1460"},{"Name":"RELIANCE 23FEB23 CE 1480","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":50992,"assetType":"future","description":"RELIANCE 23FEB23 CE 1480","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":1480,"tickSize":0.050000000000000003,"token":102050992,"tradeSymbol":"RELIANCE 23FEB23 CE 1480"},{"Name":"RELIANCE 23FEB23 CE 1500","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":50994,"assetType":"future","description":"RELIANCE 23FEB23 CE 1500","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":1500,"tickSize":0.050000000000000003,"token":102050994,"tradeSymbol":"RELIANCE 23FEB23 CE 1500"},{"Name":"RELIANCE 23FEB23 CE 1520","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":45764,"assetType":"future","description":"RELIANCE 23FEB23 CE 1520","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":1520,"tickSize":0.050000000000000003,"token":102045764,"tradeSymbol":"RELIANCE 23FEB23 CE 1520"},{"Name":"RELIANCE 23FEB23 CE 1540","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":103195,"assetType":"future","description":"RELIANCE 23FEB23 CE 1540","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":1540,"tickSize":0.050000000000000003,"token":102103195,"tradeSymbol":"RELIANCE 23FEB23 CE 1540"},{"Name":"RELIANCE 23FEB23 CE 1560","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":103197,"assetType":"future","description":"RELIANCE 23FEB23 CE 1560","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":1560,"tickSize":0.050000000000000003,"token":102103197,"tradeSymbol":"RELIANCE 23FEB23 CE 1560"},{"Name":"RELIANCE 23FEB23 CE 1580","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":103199,"assetType":"future","description":"RELIANCE 23FEB23 CE 1580","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":1580,"tickSize":0.050000000000000003,"token":102103199,"tradeSymbol":"RELIANCE 23FEB23 CE 1580"},{"Name":"RELIANCE 23FEB23 CE 1600","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":103201,"assetType":"future","description":"RELIANCE 23FEB23 CE 1600","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":1600,"tickSize":0.050000000000000003,"token":102103201,"tradeSymbol":"RELIANCE 23FEB23 CE 1600"},{"Name":"RELIANCE 23FEB23 CE 1620","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":103203,"assetType":"future","description":"RELIANCE 23FEB23 CE 1620","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":1620,"tickSize":0.050000000000000003,"token":102103203,"tradeSymbol":"RELIANCE 23FEB23 CE 1620"},{"Name":"RELIANCE 23FEB23 CE 1640","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":103205,"assetType":"future","description":"RELIANCE 23FEB23 CE 1640","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":1640,"tickSize":0.050000000000000003,"token":102103205,"tradeSymbol":"RELIANCE 23FEB23 CE 1640"},{"Name":"RELIANCE 23FEB23 CE 1660","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":103207,"assetType":"future","description":"RELIANCE 23FEB23 CE 1660","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":1660,"tickSize":0.050000000000000003,"token":102103207,"tradeSymbol":"RELIANCE 23FEB23 CE 1660"},{"Name":"RELIANCE 23FEB23 CE 1680","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":103209,"assetType":"future","description":"RELIANCE 23FEB23 CE 1680","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":1680,"tickSize":0.050000000000000003,"token":102103209,"tradeSymbol":"RELIANCE 23FEB23 CE 1680"},{"Name":"RELIANCE 23FEB23 CE 1700","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":103211,"assetType":"future","description":"RELIANCE 23FEB23 CE 1700","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":1700,"tickSize":0.050000000000000003,"token":102103211,"tradeSymbol":"RELIANCE 23FEB23 CE 1700"},{"Name":"RELIANCE 23FEB23 CE 1720","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":103213,"assetType":"future","description":"RELIANCE 23FEB23 CE 1720","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":1720,"tickSize":0.050000000000000003,"token":102103213,"tradeSymbol":"RELIANCE 23FEB23 CE 1720"},{"Name":"RELIANCE 23FEB23 CE 1740","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":103215,"assetType":"future","description":"RELIANCE 23FEB23 CE 1740","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":1740,"tickSize":0.050000000000000003,"token":102103215,"tradeSymbol":"RELIANCE 23FEB23 CE 1740"},{"Name":"RELIANCE 23FEB23 CE 1760","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":103217,"assetType":"future","description":"RELIANCE 23FEB23 CE 1760","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":1760,"tickSize":0.050000000000000003,"token":102103217,"tradeSymbol":"RELIANCE 23FEB23 CE 1760"},{"Name":"RELIANCE 23FEB23 CE 1780","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":103219,"assetType":"future","description":"RELIANCE 23FEB23 CE 1780","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":1780,"tickSize":0.050000000000000003,"token":102103219,"tradeSymbol":"RELIANCE 23FEB23 CE 1780"},{"Name":"RELIANCE 23FEB23 CE 1800","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":103221,"assetType":"future","description":"RELIANCE 23FEB23 CE 1800","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":1800,"tickSize":0.050000000000000003,"token":102103221,"tradeSymbol":"RELIANCE 23FEB23 CE 1800"},{"Name":"RELIANCE 23FEB23 CE 1820","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":103223,"assetType":"future","description":"RELIANCE 23FEB23 CE 1820","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":1820,"tickSize":0.050000000000000003,"token":102103223,"tradeSymbol":"RELIANCE 23FEB23 CE 1820"},{"Name":"RELIANCE 23FEB23 CE 1840","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":103225,"assetType":"future","description":"RELIANCE 23FEB23 CE 1840","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":1840,"tickSize":0.050000000000000003,"token":102103225,"tradeSymbol":"RELIANCE 23FEB23 CE 1840"},{"Name":"RELIANCE 23FEB23 CE 1860","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":103349,"assetType":"future","description":"RELIANCE 23FEB23 CE 1860","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":1860,"tickSize":0.050000000000000003,"token":102103349,"tradeSymbol":"RELIANCE 23FEB23 CE 1860"},{"Name":"RELIANCE 23FEB23 CE 1880","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":103443,"assetType":"future","description":"RELIANCE 23FEB23 CE 1880","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":1880,"tickSize":0.050000000000000003,"token":102103443,"tradeSymbol":"RELIANCE 23FEB23 CE 1880"},{"Name":"RELIANCE 23FEB23 CE 1900","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":103445,"assetType":"future","description":"RELIANCE 23FEB23 CE 1900","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":1900,"tickSize":0.050000000000000003,"token":102103445,"tradeSymbol":"RELIANCE 23FEB23 CE 1900"},{"Name":"RELIANCE 23FEB23 CE 1920","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":103490,"assetType":"future","description":"RELIANCE 23FEB23 CE 1920","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":1920,"tickSize":0.050000000000000003,"token":102103490,"tradeSymbol":"RELIANCE 23FEB23 CE 1920"},{"Name":"RELIANCE 23FEB23 CE 1940","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":103492,"assetType":"future","description":"RELIANCE 23FEB23 CE 1940","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":1940,"tickSize":0.050000000000000003,"token":102103492,"tradeSymbol":"RELIANCE 23FEB23 CE 1940"},{"Name":"RELIANCE 23FEB23 CE 1960","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":103494,"assetType":"future","description":"RELIANCE 23FEB23 CE 1960","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":1960,"tickSize":0.050000000000000003,"token":102103494,"tradeSymbol":"RELIANCE 23FEB23 CE 1960"},{"Name":"RELIANCE 23FEB23 CE 1980","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":103496,"assetType":"future","description":"RELIANCE 23FEB23 CE 1980","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":1980,"tickSize":0.050000000000000003,"token":102103496,"tradeSymbol":"RELIANCE 23FEB23 CE 1980"},{"Name":"RELIANCE 23FEB23 CE 2000","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":103537,"assetType":"future","description":"RELIANCE 23FEB23 CE 2000","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":2000,"tickSize":0.050000000000000003,"token":102103537,"tradeSymbol":"RELIANCE 23FEB23 CE 2000"},{"Name":"RELIANCE 23FEB23 CE 2020","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":103539,"assetType":"future","description":"RELIANCE 23FEB23 CE 2020","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":2020,"tickSize":0.050000000000000003,"token":102103539,"tradeSymbol":"RELIANCE 23FEB23 CE 2020"},{"Name":"RELIANCE 23FEB23 CE 2040","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":103541,"assetType":"future","description":"RELIANCE 23FEB23 CE 2040","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":2040,"tickSize":0.050000000000000003,"token":102103541,"tradeSymbol":"RELIANCE 23FEB23 CE 2040"},{"Name":"RELIANCE 23FEB23 CE 2060","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":103543,"assetType":"future","description":"RELIANCE 23FEB23 CE 2060","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":2060,"tickSize":0.050000000000000003,"token":102103543,"tradeSymbol":"RELIANCE 23FEB23 CE 2060"},{"Name":"RELIANCE 23FEB23 CE 2080","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":103598,"assetType":"future","description":"RELIANCE 23FEB23 CE 2080","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":2080,"tickSize":0.050000000000000003,"token":102103598,"tradeSymbol":"RELIANCE 23FEB23 CE 2080"},{"Name":"RELIANCE 23FEB23 CE 2100","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":103600,"assetType":"future","description":"RELIANCE 23FEB23 CE 2100","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":2100,"tickSize":0.050000000000000003,"token":102103600,"tradeSymbol":"RELIANCE 23FEB23 CE 2100"},{"Name":"RELIANCE 23FEB23 CE 2120","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":103602,"assetType":"future","description":"RELIANCE 23FEB23 CE 2120","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":2120,"tickSize":0.050000000000000003,"token":102103602,"tradeSymbol":"RELIANCE 23FEB23 CE 2120"},{"Name":"RELIANCE 23FEB23 CE 2140","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":103604,"assetType":"future","description":"RELIANCE 23FEB23 CE 2140","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":2140,"tickSize":0.050000000000000003,"token":102103604,"tradeSymbol":"RELIANCE 23FEB23 CE 2140"},{"Name":"RELIANCE 23FEB23 CE 2160","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":103606,"assetType":"future","description":"RELIANCE 23FEB23 CE 2160","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":2160,"tickSize":0.050000000000000003,"token":102103606,"tradeSymbol":"RELIANCE 23FEB23 CE 2160"},{"Name":"RELIANCE 23FEB23 CE 2180","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":103608,"assetType":"future","description":"RELIANCE 23FEB23 CE 2180","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":2180,"tickSize":0.050000000000000003,"token":102103608,"tradeSymbol":"RELIANCE 23FEB23 CE 2180"},{"Name":"RELIANCE 23FEB23 CE 2200","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":103610,"assetType":"future","description":"RELIANCE 23FEB23 CE 2200","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":2200,"tickSize":0.050000000000000003,"token":102103610,"tradeSymbol":"RELIANCE 23FEB23 CE 2200"},{"Name":"RELIANCE 23FEB23 CE 2220","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":103612,"assetType":"future","description":"RELIANCE 23FEB23 CE 2220","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":2220,"tickSize":0.050000000000000003,"token":102103612,"tradeSymbol":"RELIANCE 23FEB23 CE 2220"},{"Name":"RELIANCE 23FEB23 CE 2240","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":103614,"assetType":"future","description":"RELIANCE 23FEB23 CE 2240","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":2240,"tickSize":0.050000000000000003,"token":102103614,"tradeSymbol":"RELIANCE 23FEB23 CE 2240"},{"Name":"RELIANCE 23FEB23 CE 2260","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":103616,"assetType":"future","description":"RELIANCE 23FEB23 CE 2260","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":2260,"tickSize":0.050000000000000003,"token":102103616,"tradeSymbol":"RELIANCE 23FEB23 CE 2260"},{"Name":"RELIANCE 23FEB23 CE 2280","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":103618,"assetType":"future","description":"RELIANCE 23FEB23 CE 2280","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":2280,"tickSize":0.050000000000000003,"token":102103618,"tradeSymbol":"RELIANCE 23FEB23 CE 2280"},{"Name":"RELIANCE 23FEB23 CE 2300","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":103620,"assetType":"future","description":"RELIANCE 23FEB23 CE 2300","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":2300,"tickSize":0.050000000000000003,"token":102103620,"tradeSymbol":"RELIANCE 23FEB23 CE 2300"},{"Name":"RELIANCE 23FEB23 CE 2320","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":103622,"assetType":"future","description":"RELIANCE 23FEB23 CE 2320","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":2320,"tickSize":0.050000000000000003,"token":102103622,"tradeSymbol":"RELIANCE 23FEB23 CE 2320"},{"Name":"RELIANCE 23FEB23 CE 2340","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":103624,"assetType":"future","description":"RELIANCE 23FEB23 CE 2340","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":2340,"tickSize":0.050000000000000003,"token":102103624,"tradeSymbol":"RELIANCE 23FEB23 CE 2340"},{"Name":"RELIANCE 23FEB23 CE 2360","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":103626,"assetType":"future","description":"RELIANCE 23FEB23 CE 2360","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":2360,"tickSize":0.050000000000000003,"token":102103626,"tradeSymbol":"RELIANCE 23FEB23 CE 2360"},{"Name":"RELIANCE 23FEB23 CE 2380","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":103628,"assetType":"future","description":"RELIANCE 23FEB23 CE 2380","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":2380,"tickSize":0.050000000000000003,"token":102103628,"tradeSymbol":"RELIANCE 23FEB23 CE 2380"},{"Name":"RELIANCE 23FEB23 CE 2400","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":103630,"assetType":"future","description":"RELIANCE 23FEB23 CE 2400","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":2400,"tickSize":0.050000000000000003,"token":102103630,"tradeSymbol":"RELIANCE 23FEB23 CE 2400"},{"Name":"RELIANCE 23FEB23 CE 2420","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":103632,"assetType":"future","description":"RELIANCE 23FEB23 CE 2420","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":2420,"tickSize":0.050000000000000003,"token":102103632,"tradeSymbol":"RELIANCE 23FEB23 CE 2420"},{"Name":"RELIANCE 23FEB23 CE 2440","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":103634,"assetType":"future","description":"RELIANCE 23FEB23 CE 2440","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":2440,"tickSize":0.050000000000000003,"token":102103634,"tradeSymbol":"RELIANCE 23FEB23 CE 2440"},{"Name":"RELIANCE 23FEB23 CE 2460","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":103636,"assetType":"future","description":"RELIANCE 23FEB23 CE 2460","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":2460,"tickSize":0.050000000000000003,"token":102103636,"tradeSymbol":"RELIANCE 23FEB23 CE 2460"},{"Name":"RELIANCE 23FEB23 CE 2480","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":103638,"assetType":"future","description":"RELIANCE 23FEB23 CE 2480","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":2480,"tickSize":0.050000000000000003,"token":102103638,"tradeSymbol":"RELIANCE 23FEB23 CE 2480"},{"Name":"RELIANCE 23FEB23 CE 2500","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":103640,"assetType":"future","description":"RELIANCE 23FEB23 CE 2500","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":2500,"tickSize":0.050000000000000003,"token":102103640,"tradeSymbol":"RELIANCE 23FEB23 CE 2500"},{"Name":"RELIANCE 23FEB23 CE 2520","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":103642,"assetType":"future","description":"RELIANCE 23FEB23 CE 2520","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":2520,"tickSize":0.050000000000000003,"token":102103642,"tradeSymbol":"RELIANCE 23FEB23 CE 2520"},{"Name":"RELIANCE 23FEB23 CE 2540","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":103644,"assetType":"future","description":"RELIANCE 23FEB23 CE 2540","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":2540,"tickSize":0.050000000000000003,"token":102103644,"tradeSymbol":"RELIANCE 23FEB23 CE 2540"},{"Name":"RELIANCE 23FEB23 CE 2560","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":103646,"assetType":"future","description":"RELIANCE 23FEB23 CE 2560","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":2560,"tickSize":0.050000000000000003,"token":102103646,"tradeSymbol":"RELIANCE 23FEB23 CE 2560"},{"Name":"RELIANCE 23FEB23 CE 2580","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":103648,"assetType":"future","description":"RELIANCE 23FEB23 CE 2580","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":2580,"tickSize":0.050000000000000003,"token":102103648,"tradeSymbol":"RELIANCE 23FEB23 CE 2580"},{"Name":"RELIANCE 23FEB23 CE 2600","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":103650,"assetType":"future","description":"RELIANCE 23FEB23 CE 2600","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":2600,"tickSize":0.050000000000000003,"token":102103650,"tradeSymbol":"RELIANCE 23FEB23 CE 2600"},{"Name":"RELIANCE 23FEB23 CE 2620","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":103652,"assetType":"future","description":"RELIANCE 23FEB23 CE 2620","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":2620,"tickSize":0.050000000000000003,"token":102103652,"tradeSymbol":"RELIANCE 23FEB23 CE 2620"},{"Name":"RELIANCE 23FEB23 CE 2640","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":103654,"assetType":"future","description":"RELIANCE 23FEB23 CE 2640","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":2640,"tickSize":0.050000000000000003,"token":102103654,"tradeSymbol":"RELIANCE 23FEB23 CE 2640"},{"Name":"RELIANCE 23FEB23 CE 2660","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":103656,"assetType":"future","description":"RELIANCE 23FEB23 CE 2660","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":2660,"tickSize":0.050000000000000003,"token":102103656,"tradeSymbol":"RELIANCE 23FEB23 CE 2660"},{"Name":"RELIANCE 23FEB23 CE 2680","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":103658,"assetType":"future","description":"RELIANCE 23FEB23 CE 2680","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":2680,"tickSize":0.050000000000000003,"token":102103658,"tradeSymbol":"RELIANCE 23FEB23 CE 2680"},{"Name":"RELIANCE 23FEB23 CE 2700","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":103660,"assetType":"future","description":"RELIANCE 23FEB23 CE 2700","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":2700,"tickSize":0.050000000000000003,"token":102103660,"tradeSymbol":"RELIANCE 23FEB23 CE 2700"},{"Name":"RELIANCE 23FEB23 CE 2720","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":103662,"assetType":"future","description":"RELIANCE 23FEB23 CE 2720","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":2720,"tickSize":0.050000000000000003,"token":102103662,"tradeSymbol":"RELIANCE 23FEB23 CE 2720"},{"Name":"RELIANCE 23FEB23 CE 2740","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":103664,"assetType":"future","description":"RELIANCE 23FEB23 CE 2740","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":2740,"tickSize":0.050000000000000003,"token":102103664,"tradeSymbol":"RELIANCE 23FEB23 CE 2740"},{"Name":"RELIANCE 23FEB23 CE 2760","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":103666,"assetType":"future","description":"RELIANCE 23FEB23 CE 2760","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":2760,"tickSize":0.050000000000000003,"token":102103666,"tradeSymbol":"RELIANCE 23FEB23 CE 2760"},{"Name":"RELIANCE 23FEB23 CE 2780","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":103668,"assetType":"future","description":"RELIANCE 23FEB23 CE 2780","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":2780,"tickSize":0.050000000000000003,"token":102103668,"tradeSymbol":"RELIANCE 23FEB23 CE 2780"},{"Name":"RELIANCE 23FEB23 CE 2800","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":103670,"assetType":"future","description":"RELIANCE 23FEB23 CE 2800","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":2800,"tickSize":0.050000000000000003,"token":102103670,"tradeSymbol":"RELIANCE 23FEB23 CE 2800"},{"Name":"RELIANCE 23FEB23 CE 2820","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":103672,"assetType":"future","description":"RELIANCE 23FEB23 CE 2820","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":2820,"tickSize":0.050000000000000003,"token":102103672,"tradeSymbol":"RELIANCE 23FEB23 CE 2820"},{"Name":"RELIANCE 23FEB23 CE 2840","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":103674,"assetType":"future","description":"RELIANCE 23FEB23 CE 2840","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":2840,"tickSize":0.050000000000000003,"token":102103674,"tradeSymbol":"RELIANCE 23FEB23 CE 2840"},{"Name":"RELIANCE 23FEB23 CE 2860","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":103676,"assetType":"future","description":"RELIANCE 23FEB23 CE 2860","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":2860,"tickSize":0.050000000000000003,"token":102103676,"tradeSymbol":"RELIANCE 23FEB23 CE 2860"},{"Name":"RELIANCE 23FEB23 CE 2880","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":103678,"assetType":"future","description":"RELIANCE 23FEB23 CE 2880","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":2880,"tickSize":0.050000000000000003,"token":102103678,"tradeSymbol":"RELIANCE 23FEB23 CE 2880"},{"Name":"RELIANCE 23FEB23 CE 2900","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":103683,"assetType":"future","description":"RELIANCE 23FEB23 CE 2900","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":2900,"tickSize":0.050000000000000003,"token":102103683,"tradeSymbol":"RELIANCE 23FEB23 CE 2900"},{"Name":"RELIANCE 23FEB23 CE 2920","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":103685,"assetType":"future","description":"RELIANCE 23FEB23 CE 2920","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":2920,"tickSize":0.050000000000000003,"token":102103685,"tradeSymbol":"RELIANCE 23FEB23 CE 2920"},{"Name":"RELIANCE 23FEB23 CE 2940","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":103763,"assetType":"future","description":"RELIANCE 23FEB23 CE 2940","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":2940,"tickSize":0.050000000000000003,"token":102103763,"tradeSymbol":"RELIANCE 23FEB23 CE 2940"},{"Name":"RELIANCE 23FEB23 CE 2960","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":103765,"assetType":"future","description":"RELIANCE 23FEB23 CE 2960","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":2960,"tickSize":0.050000000000000003,"token":102103765,"tradeSymbol":"RELIANCE 23FEB23 CE 2960"},{"Name":"RELIANCE 23FEB23 CE 2980","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":103767,"assetType":"future","description":"RELIANCE 23FEB23 CE 2980","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":2980,"tickSize":0.050000000000000003,"token":102103767,"tradeSymbol":"RELIANCE 23FEB23 CE 2980"},{"Name":"RELIANCE 23FEB23 CE 3000","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":103778,"assetType":"future","description":"RELIANCE 23FEB23 CE 3000","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":3000,"tickSize":0.050000000000000003,"token":102103778,"tradeSymbol":"RELIANCE 23FEB23 CE 3000"},{"Name":"RELIANCE 23FEB23 CE 3020","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":103780,"assetType":"future","description":"RELIANCE 23FEB23 CE 3020","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":3020,"tickSize":0.050000000000000003,"token":102103780,"tradeSymbol":"RELIANCE 23FEB23 CE 3020"},{"Name":"RELIANCE 23FEB23 CE 3040","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":103923,"assetType":"future","description":"RELIANCE 23FEB23 CE 3040","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":3040,"tickSize":0.050000000000000003,"token":102103923,"tradeSymbol":"RELIANCE 23FEB23 CE 3040"},{"Name":"RELIANCE 23FEB23 CE 3060","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":103997,"assetType":"future","description":"RELIANCE 23FEB23 CE 3060","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":3060,"tickSize":0.050000000000000003,"token":102103997,"tradeSymbol":"RELIANCE 23FEB23 CE 3060"},{"Name":"RELIANCE 23FEB23 CE 3080","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":103999,"assetType":"future","description":"RELIANCE 23FEB23 CE 3080","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":3080,"tickSize":0.050000000000000003,"token":102103999,"tradeSymbol":"RELIANCE 23FEB23 CE 3080"},{"Name":"RELIANCE 23FEB23 CE 3100","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":104001,"assetType":"future","description":"RELIANCE 23FEB23 CE 3100","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":3100,"tickSize":0.050000000000000003,"token":102104001,"tradeSymbol":"RELIANCE 23FEB23 CE 3100"},{"Name":"RELIANCE 23FEB23 CE 3120","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":104003,"assetType":"future","description":"RELIANCE 23FEB23 CE 3120","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":3120,"tickSize":0.050000000000000003,"token":102104003,"tradeSymbol":"RELIANCE 23FEB23 CE 3120"},{"Name":"RELIANCE 23FEB23 CE 3140","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":104005,"assetType":"future","description":"RELIANCE 23FEB23 CE 3140","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":3140,"tickSize":0.050000000000000003,"token":102104005,"tradeSymbol":"RELIANCE 23FEB23 CE 3140"},{"Name":"RELIANCE 23FEB23 CE 3160","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":104007,"assetType":"future","description":"RELIANCE 23FEB23 CE 3160","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":3160,"tickSize":0.050000000000000003,"token":102104007,"tradeSymbol":"RELIANCE 23FEB23 CE 3160"},{"Name":"RELIANCE 23FEB23 CE 3180","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":104009,"assetType":"future","description":"RELIANCE 23FEB23 CE 3180","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":3180,"tickSize":0.050000000000000003,"token":102104009,"tradeSymbol":"RELIANCE 23FEB23 CE 3180"},{"Name":"RELIANCE 23FEB23 CE 3200","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":104011,"assetType":"future","description":"RELIANCE 23FEB23 CE 3200","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":3200,"tickSize":0.050000000000000003,"token":102104011,"tradeSymbol":"RELIANCE 23FEB23 CE 3200"},{"Name":"RELIANCE 23FEB23 CE 3220","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":104013,"assetType":"future","description":"RELIANCE 23FEB23 CE 3220","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":3220,"tickSize":0.050000000000000003,"token":102104013,"tradeSymbol":"RELIANCE 23FEB23 CE 3220"},{"Name":"RELIANCE 23FEB23 CE 3240","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":104015,"assetType":"future","description":"RELIANCE 23FEB23 CE 3240","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":3240,"tickSize":0.050000000000000003,"token":102104015,"tradeSymbol":"RELIANCE 23FEB23 CE 3240"},{"Name":"RELIANCE 23FEB23 CE 3260","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":104017,"assetType":"future","description":"RELIANCE 23FEB23 CE 3260","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":3260,"tickSize":0.050000000000000003,"token":102104017,"tradeSymbol":"RELIANCE 23FEB23 CE 3260"},{"Name":"RELIANCE 23FEB23 CE 3280","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":104019,"assetType":"future","description":"RELIANCE 23FEB23 CE 3280","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":3280,"tickSize":0.050000000000000003,"token":102104019,"tradeSymbol":"RELIANCE 23FEB23 CE 3280"},{"Name":"RELIANCE 23FEB23 CE 3300","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":104021,"assetType":"future","description":"RELIANCE 23FEB23 CE 3300","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":3300,"tickSize":0.050000000000000003,"token":102104021,"tradeSymbol":"RELIANCE 23FEB23 CE 3300"},{"Name":"RELIANCE 23FEB23 CE 3320","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":104023,"assetType":"future","description":"RELIANCE 23FEB23 CE 3320","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":3320,"tickSize":0.050000000000000003,"token":102104023,"tradeSymbol":"RELIANCE 23FEB23 CE 3320"},{"Name":"RELIANCE 23FEB23 CE 3340","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":104025,"assetType":"future","description":"RELIANCE 23FEB23 CE 3340","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":3340,"tickSize":0.050000000000000003,"token":102104025,"tradeSymbol":"RELIANCE 23FEB23 CE 3340"},{"Name":"RELIANCE 23FEB23 CE 3360","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":104027,"assetType":"future","description":"RELIANCE 23FEB23 CE 3360","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":3360,"tickSize":0.050000000000000003,"token":102104027,"tradeSymbol":"RELIANCE 23FEB23 CE 3360"},{"Name":"RELIANCE 23FEB23 CE 3380","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":104029,"assetType":"future","description":"RELIANCE 23FEB23 CE 3380","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":3380,"tickSize":0.050000000000000003,"token":102104029,"tradeSymbol":"RELIANCE 23FEB23 CE 3380"},{"Name":"RELIANCE 23FEB23 CE 3400","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":104031,"assetType":"future","description":"RELIANCE 23FEB23 CE 3400","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":3400,"tickSize":0.050000000000000003,"token":102104031,"tradeSymbol":"RELIANCE 23FEB23 CE 3400"},{"Name":"RELIANCE 23FEB23 CE 3420","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":104033,"assetType":"future","description":"RELIANCE 23FEB23 CE 3420","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":3420,"tickSize":0.050000000000000003,"token":102104033,"tradeSymbol":"RELIANCE 23FEB23 CE 3420"},{"Name":"RELIANCE 23FEB23 CE 3440","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":104035,"assetType":"future","description":"RELIANCE 23FEB23 CE 3440","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":3440,"tickSize":0.050000000000000003,"token":102104035,"tradeSymbol":"RELIANCE 23FEB23 CE 3440"},{"Name":"RELIANCE 23FEB23 CE 3460","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":104037,"assetType":"future","description":"RELIANCE 23FEB23 CE 3460","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":3460,"tickSize":0.050000000000000003,"token":102104037,"tradeSymbol":"RELIANCE 23FEB23 CE 3460"},{"Name":"RELIANCE 23FEB23 CE 3480","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":104039,"assetType":"future","description":"RELIANCE 23FEB23 CE 3480","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":3480,"tickSize":0.050000000000000003,"token":102104039,"tradeSymbol":"RELIANCE 23FEB23 CE 3480"},{"Name":"RELIANCE 23FEB23 CE 3500","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":104041,"assetType":"future","description":"RELIANCE 23FEB23 CE 3500","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":3500,"tickSize":0.050000000000000003,"token":102104041,"tradeSymbol":"RELIANCE 23FEB23 CE 3500"},{"Name":"RELIANCE 23FEB23 CE 3520","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":104043,"assetType":"future","description":"RELIANCE 23FEB23 CE 3520","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":3520,"tickSize":0.050000000000000003,"token":102104043,"tradeSymbol":"RELIANCE 23FEB23 CE 3520"},{"Name":"RELIANCE 23FEB23 CE 3540","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":104045,"assetType":"future","description":"RELIANCE 23FEB23 CE 3540","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":3540,"tickSize":0.050000000000000003,"token":102104045,"tradeSymbol":"RELIANCE 23FEB23 CE 3540"},{"Name":"RELIANCE 23FEB23 CE 3560","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":104047,"assetType":"future","description":"RELIANCE 23FEB23 CE 3560","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":3560,"tickSize":0.050000000000000003,"token":102104047,"tradeSymbol":"RELIANCE 23FEB23 CE 3560"},{"Name":"RELIANCE 23FEB23 CE 3580","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":104049,"assetType":"future","description":"RELIANCE 23FEB23 CE 3580","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":3580,"tickSize":0.050000000000000003,"token":102104049,"tradeSymbol":"RELIANCE 23FEB23 CE 3580"},{"Name":"RELIANCE 23FEB23 CE 3600","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":104051,"assetType":"future","description":"RELIANCE 23FEB23 CE 3600","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":3600,"tickSize":0.050000000000000003,"token":102104051,"tradeSymbol":"RELIANCE 23FEB23 CE 3600"},{"Name":"RELIANCE 23FEB23 CE 3620","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":104053,"assetType":"future","description":"RELIANCE 23FEB23 CE 3620","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":3620,"tickSize":0.050000000000000003,"token":102104053,"tradeSymbol":"RELIANCE 23FEB23 CE 3620"},{"Name":"RELIANCE 23FEB23 CE 3640","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":36371,"assetType":"future","description":"RELIANCE 23FEB23 CE 3640","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":3640,"tickSize":0.050000000000000003,"token":102036371,"tradeSymbol":"RELIANCE 23FEB23 CE 3640"},{"Name":"RELIANCE 23FEB23 CE 3660","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":36373,"assetType":"future","description":"RELIANCE 23FEB23 CE 3660","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":3660,"tickSize":0.050000000000000003,"token":102036373,"tradeSymbol":"RELIANCE 23FEB23 CE 3660"},{"Name":"RELIANCE 23FEB23 CE 3680","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":37646,"assetType":"future","description":"RELIANCE 23FEB23 CE 3680","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":3680,"tickSize":0.050000000000000003,"token":102037646,"tradeSymbol":"RELIANCE 23FEB23 CE 3680"},{"Name":"RELIANCE 23FEB23 CE 3700","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":37648,"assetType":"future","description":"RELIANCE 23FEB23 CE 3700","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":3700,"tickSize":0.050000000000000003,"token":102037648,"tradeSymbol":"RELIANCE 23FEB23 CE 3700"},{"Name":"RELIANCE 23FEB23 CE 3720","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":37650,"assetType":"future","description":"RELIANCE 23FEB23 CE 3720","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":3720,"tickSize":0.050000000000000003,"token":102037650,"tradeSymbol":"RELIANCE 23FEB23 CE 3720"},{"Name":"RELIANCE 23FEB23 CE 3740","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":37652,"assetType":"future","description":"RELIANCE 23FEB23 CE 3740","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":3740,"tickSize":0.050000000000000003,"token":102037652,"tradeSymbol":"RELIANCE 23FEB23 CE 3740"},{"Name":"RELIANCE 23FEB23 CE 3760","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":39747,"assetType":"future","description":"RELIANCE 23FEB23 CE 3760","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":3760,"tickSize":0.050000000000000003,"token":102039747,"tradeSymbol":"RELIANCE 23FEB23 CE 3760"},{"Name":"RELIANCE 23FEB23 CE 3780","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":40436,"assetType":"future","description":"RELIANCE 23FEB23 CE 3780","exchange":"nse","expiryDate":1677142800,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":3780,"tickSize":0.050000000000000003,"token":102040436,"tradeSymbol":"RELIANCE 23FEB23 CE 3780"},{"Name":"RELIANCE 29MAR23 CE 1300","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":40007,"assetType":"future","description":"RELIANCE 29MAR23 CE 1300","exchange":"nse","expiryDate":1680080400,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":1300,"tickSize":0.050000000000000003,"token":102040007,"tradeSymbol":"RELIANCE 29MAR23 CE 1300"},{"Name":"RELIANCE 29MAR23 CE 1320","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":40009,"assetType":"future","description":"RELIANCE 29MAR23 CE 1320","exchange":"nse","expiryDate":1680080400,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":1320,"tickSize":0.050000000000000003,"token":102040009,"tradeSymbol":"RELIANCE 29MAR23 CE 1320"},{"Name":"RELIANCE 29MAR23 CE 1340","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":142552,"assetType":"future","description":"RELIANCE 29MAR23 CE 1340","exchange":"nse","expiryDate":1680080400,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":1340,"tickSize":0.050000000000000003,"token":102142552,"tradeSymbol":"RELIANCE 29MAR23 CE 1340"},{"Name":"RELIANCE 29MAR23 CE 1360","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":142554,"assetType":"future","description":"RELIANCE 29MAR23 CE 1360","exchange":"nse","expiryDate":1680080400,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":1360,"tickSize":0.050000000000000003,"token":102142554,"tradeSymbol":"RELIANCE 29MAR23 CE 1360"},{"Name":"RELIANCE 29MAR23 CE 1380","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":52973,"assetType":"future","description":"RELIANCE 29MAR23 CE 1380","exchange":"nse","expiryDate":1680080400,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":1380,"tickSize":0.050000000000000003,"token":102052973,"tradeSymbol":"RELIANCE 29MAR23 CE 1380"},{"Name":"RELIANCE 29MAR23 CE 1400","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":44739,"assetType":"future","description":"RELIANCE 29MAR23 CE 1400","exchange":"nse","expiryDate":1680080400,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":1400,"tickSize":0.050000000000000003,"token":102044739,"tradeSymbol":"RELIANCE 29MAR23 CE 1400"},{"Name":"RELIANCE 29MAR23 CE 1420","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":40724,"assetType":"future","description":"RELIANCE 29MAR23 CE 1420","exchange":"nse","expiryDate":1680080400,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":1420,"tickSize":0.050000000000000003,"token":102040724,"tradeSymbol":"RELIANCE 29MAR23 CE 1420"},{"Name":"RELIANCE 29MAR23 CE 1440","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":44537,"assetType":"future","description":"RELIANCE 29MAR23 CE 1440","exchange":"nse","expiryDate":1680080400,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":1440,"tickSize":0.050000000000000003,"token":102044537,"tradeSymbol":"RELIANCE 29MAR23 CE 1440"},{"Name":"RELIANCE 29MAR23 CE 1460","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":44545,"assetType":"future","description":"RELIANCE 29MAR23 CE 1460","exchange":"nse","expiryDate":1680080400,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":1460,"tickSize":0.050000000000000003,"token":102044545,"tradeSymbol":"RELIANCE 29MAR23 CE 1460"},{"Name":"RELIANCE 29MAR23 CE 1480","OptionType":"CE","ScriptName":"RELIANCE","Series":"OPTSTK","UniqueId":38890,"assetType":"future","description":"RELIANCE 29MAR23 CE 1480","exchange":"nse","expiryDate":1680080400,"instrumentName":"OPTSTK","lotQty":250,"multiplier":1,"strickPrice":1480,"tickSize":0.050000000000000003,"token":102038890,"tradeSymbol":"RELIANCE 29MAR23 CE 1480"},{"Name":"RELIANCE 29MAR23 CE 1500","OptionType":"CE","ScriptName":