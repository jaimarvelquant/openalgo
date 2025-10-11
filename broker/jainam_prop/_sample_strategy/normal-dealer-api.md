# Normal Dealer API (Regular Dealer Order Functionality)

**Base Endpoint:** `https://smpb.jainam.in:4143/`

**Client ID:** `DLL7182`

---

## ?? IMPORTANT NOTES - READ CAREFULLY

### 1. Client ID Distinction
This documentation uses **YOUR ACTUAL PRODUCTION Client ID**, not the example IDs from the original documentation:

| Source | Client ID Used | Purpose |
|--------|---------------|---------|
| **Original Documentation Examples** | `ON190`, `ON100` | Sample/Example IDs only |
| **THIS DOCUMENT (Production)** | `DLL7182` | ? YOUR ACTUAL Client ID to use in API calls |

**Action Required:** All API calls in this document show `DLL7182` - this is the correct Client ID to use for your Normal Dealer account.

---

### 2. Authentication Credentials Distinction
The original documentation used example/dummy credentials. This document contains **YOUR ACTUAL PRODUCTION CREDENTIALS**:

#### Original Documentation (Examples):
- **secretKey:** `Tgmj182#ui` ? Example only
- **appKey:** `59fcfb78db569a5f014579` ? Example only

#### THIS DOCUMENT (Your Production Credentials):

**Market Data API A:**
- **App Key:** `511c4265c2869ab1f54180` ? YOUR ACTUAL KEY
- **App Secret:** `Lypl445#sR` ? YOUR ACTUAL SECRET

**Interactive Order API A:**
- **App Key:** `d229ee8bc6be3d81d35946` ? YOUR ACTUAL KEY
- **App Secret:** `Qiet271#eJ` ? YOUR ACTUAL SECRET

**Action Required:** Use the credentials shown in this document for production authentication. Do NOT use the example credentials from the original documentation.

---

### 3. API Usage Distinction

| API Type | When to Use | Authentication |
|----------|-------------|----------------|
| **Market Data API A** | For fetching market data, quotes, historical data | Use App Key: `511c4265c2869ab1f54180` |
| **Interactive Order API A** | For placing orders, modifying orders, checking positions, balances | Use App Key: `d229ee8bc6be3d81d35946` |

---

### 4. Key Differences Summary

| Item | Original Docs | THIS Document |
|------|---------------|---------------|
| **Client ID** | ON190 / ON100 (examples) | DLL7182 (production) |
| **Base Endpoint** | Same | `https://smpb.jainam.in:4143/` |
| **Market Data API Key** | Example key | `511c4265c2869ab1f54180` |
| **Market Data Secret** | Example secret | `Lypl445#sR` |
| **Interactive API Key** | Example key | `d229ee8bc6be3d81d35946` |
| **Interactive API Secret** | Example secret | `Qiet271#eJ` |

---

### 5. Security Warning
?? **KEEP THESE CREDENTIALS SECURE:**
- Never commit these credentials to public repositories
- Never share these keys with unauthorized persons
- Store them in environment variables or secure vaults in production
- Rotate keys periodically as per security best practices

---

## Authentication Credentials

### Market Data API A
- **App Key:** `511c4265c2869ab1f54180`
- **App Secret:** `Lypl445#sR`
- **Purpose:** Market data, quotes, historical data

### Interactive Order API A
- **App Key:** `d229ee8bc6be3d81d35946`
- **App Secret:** `Qiet271#eJ`
- **Purpose:** Trading operations, orders, positions, balances

---

## A. Authentication

### Login (Market Data API A)
- **Method:** POST
- **Endpoint:** `https://smpb.jainam.in:4143/interactive/user/session`
- **Request Body:**
```json
{
  "secretKey": "Lypl445#sR",
  "appKey": "511c4265c2869ab1f54180",
  "source": "WEBAPI"
}
```

### Login (Interactive Order API A)
- **Method:** POST
- **Endpoint:** `https://smpb.jainam.in:4143/interactive/user/session`
- **Request Body:**
```json
{
  "secretKey": "Qiet271#eJ",
  "appKey": "d229ee8bc6be3d81d35946",
  "source": "WEBAPI"
}
```

---

## B. Trading and Order Management

### 1. Place Order API
- **Method:** POST
- **Endpoint:** `https://smpb.jainam.in:4143/interactive/orders`
- **Note:** Please send clientID for which you want to Place Order.
- **Authentication:** Use Interactive Order API A credentials

**Request Body:**
```json
{
  "exchangeSegment": "NSECM",
  "exchangeInstrumentID": 11536,
  "productType": "NRML",
  "orderType": "MARKET",
  "orderSide": "BUY",
  "timeInForce": "DAY",
  "disclosedQuantity": 0,
  "orderQuantity": "3",
  "limitPrice": 0,
  "orderUniqueIdentifier": "17859599",
  "stopPrice": 0,
  "clientID": "DLL7182"
}
```

**Required Parameters:**
- `exchangeSegment`: String - Exchange segment (e.g., "NSECM")
- `exchangeInstrumentID`: Number - Exchange instrument ID
- `productType`: String - Product type (NRML/MIS/CNC)
- `orderType`: String - Order type (MARKET/LIMIT)
- `orderSide`: String - Order side (BUY/SELL)
- `timeInForce`: String - Time in force (DAY)
- `disclosedQuantity`: Number - Disclosed quantity
- `orderQuantity`: String - Order quantity
- `limitPrice`: Number - Limit price (0 for MARKET orders)
- `orderUniqueIdentifier`: String - Unique order identifier
- `stopPrice`: Number - Stop price (0 if not applicable)
- `clientID`: String - Client ID ("DLL7182")

---

### 2. Modify Order API
- **Method:** PUT
- **Endpoint:** `https://smpb.jainam.in:4143/interactive/orders`
- **Note:** Please send clientID for which you want to modify order.
- **Authentication:** Use Interactive Order API A credentials

**Request Body:**
```json
{
  "appOrderID": 1100036275,
  "modifiedProductType": "NRML",
  "modifiedOrderType": "MARKET",
  "modifiedOrderQuantity": 3,
  "modifiedDisclosedQuantity": 0,
  "modifiedLimitPrice": 0,
  "modifiedStopPrice": 0,
  "modifiedTimeInForce": "DAY",
  "orderUniqueIdentifier": "454845",
  "clientID": "DLL7182"
}
```

**Required Parameters:**
- `appOrderID`: Number - Application order ID to modify
- `modifiedProductType`: String - Modified product type
- `modifiedOrderType`: String - Modified order type
- `modifiedOrderQuantity`: Number - Modified order quantity
- `modifiedDisclosedQuantity`: Number - Modified disclosed quantity
- `modifiedLimitPrice`: Number - Modified limit price
- `modifiedStopPrice`: Number - Modified stop price
- `modifiedTimeInForce`: String - Modified time in force
- `orderUniqueIdentifier`: String - Order unique identifier
- `clientID`: String - Client ID ("DLL7182")

---

### 3. Cancel Order API
- **Method:** DELETE
- **Endpoint:** `https://smpb.jainam.in:4143/interactive/orders?appOrderID={appOrderID}&clientID={clientID}`
- **Note:** Please send clientID for which you want to Cancel Order API.
- **Authentication:** Use Interactive Order API A credentials

**Example URL:**
```
https://smpb.jainam.in:4143/interactive/orders?appOrderID=1100062468&clientID=DLL7182
```

**Required Parameters:**
- `appOrderID`: Number - Application order ID to cancel
- `clientID`: String - Client ID ("DLL7182")

---

### 4. Cancel All API
- **Method:** POST
- **Endpoint:** `https://smpb.jainam.in:4143/interactive/orders/cancelall`
- **Note:** Please send clientID for which you want to Cancel all Order API.
- **Authentication:** Use Interactive Order API A credentials

**Request Body:**
```json
{
  "exchangeSegment": "NSECM",
  "exchangeInstrumentID": 2885,
  "clientID": "DLL7182"
}
```

**Required Parameters:**
- `exchangeSegment`: String - Exchange segment
- `exchangeInstrumentID`: Number - Exchange instrument ID
- `clientID`: String - Client ID ("DLL7182")

---

## C. Account and Portfolio Management

### 1. Dealer Position API
- **Method:** GET
- **Endpoint:** `https://smpb.jainam.in:4143/interactive/portfolio/dealerpositions?dayOrNet={dayOrNet}&clientID={clientID}`
- **Note:** Please send clientID for which you want to check Position.
- **Authentication:** Use Interactive Order API A credentials

**Example URL:**
```
https://smpb.jainam.in:4143/interactive/portfolio/dealerpositions?dayOrNet=NetWise&clientID=DLL7182
```

**Required Parameters:**
- `dayOrNet`: String - Position type ("NetWise" or "DayWise")
- `clientID`: String - Client ID ("DLL7182")

---

### 2. Dealer TradeBook API
- **Method:** GET
- **Endpoint:** `https://smpb.jainam.in:4143/interactive/orders/dealertradebook?clientID={clientID}`
- **Note:** Please send clientID for which you want to Check TradeBook.
- **Authentication:** Use Interactive Order API A credentials

**Example URL:**
```
https://smpb.jainam.in:4143/interactive/orders/dealertradebook?clientID=DLL7182
```

**Required Parameters:**
- `clientID`: String - Client ID ("DLL7182")

---

### 3. Dealer OrderBook API
- **Method:** GET
- **Endpoint:** `https://smpb.jainam.in:4143/interactive/orders/dealerorderbook?clientID={clientID}`
- **Note:** Please send clientID for which you want to check OrderBook.
- **Authentication:** Use Interactive Order API A credentials

**Example URL:**
```
https://smpb.jainam.in:4143/interactive/orders/dealerorderbook?clientID=DLL7182
```

**Required Parameters:**
- `clientID`: String - Client ID ("DLL7182")

---

### 4. Get Balance API
- **Method:** GET
- **Endpoint:** `https://smpb.jainam.in:4143/interactive/user/balance?clientID={clientID}`
- **Note:** Please send clientID for which you want to check balance.
- **Authentication:** Use Interactive Order API A credentials

**Example URL:**
```
https://smpb.jainam.in:4143/interactive/user/balance?clientID=DLL7182
```

**Required Parameters:**
- `clientID`: String - Client ID ("DLL7182")

---

### 5. Get Holdings API
- **Method:** GET
- **Endpoint:** `https://smpb.jainam.in:4143/interactive/portfolio/holdings?clientID={clientID}`
- **Note:** Please send clientID for which you want to check holdings.
- **Authentication:** Use Interactive Order API A credentials

**Example URL:**
```
https://smpb.jainam.in:4143/interactive/portfolio/holdings?clientID=DLL7182
```

**Required Parameters:**
- `clientID`: String - Client ID ("DLL7182")

---

### 6. Position Conversion API
- **Method:** PUT
- **Endpoint:** `https://smpb.jainam.in:4143/interactive/portfolio/positions/convert`
- **Note:** Please send clientID for which you want to Position Conversion.
- **Authentication:** Use Interactive Order API A credentials

**Request Body:**
```json
{
  "exchangeSegment": "NSECM",
  "exchangeInstrumentID": 11536,
  "oldProductType": "MIS",
  "newProductType": "NRML",
  "isDayWise": false,
  "targetQty": "2",
  "clientID": "DLL7182"
}
```

**Required Parameters:**
- `exchangeSegment`: String - Exchange segment
- `exchangeInstrumentID`: Number - Exchange instrument ID
- `oldProductType`: String - Current product type (e.g., "MIS")
- `newProductType`: String - Target product type (e.g., "NRML")
- `isDayWise`: Boolean - Day wise flag (true/false)
- `targetQty`: String - Quantity to convert
- `clientID`: String - Client ID ("DLL7182")

---

### 7. Square-Off API
- **Method:** PUT
- **Endpoint:** `https://smpb.jainam.in:4143/interactive/portfolio/squareoff`
- **Note:** Please send clientID for which you want to square off positions.
- **Authentication:** Use Interactive Order API A credentials

**Request Body:**
```json
{
  "exchangeSegment": "NSECM",
  "exchangeInstrumentID": 2885,
  "productType": "NRML",
  "squareoffMode": "DayWise",
  "squareOffQtyValue": 3,
  "clientID": "DLL7182",
  "positionSquareOffQuantityType": "ExactQty"
}
```

**Required Parameters:**
- `exchangeSegment`: String - Exchange segment
- `exchangeInstrumentID`: Number - Exchange instrument ID
- `productType`: String - Product type (e.g., "NRML")
- `squareoffMode`: String - Square-off mode ("DayWise" or "NetWise")
- `squareOffQtyValue`: Number - Quantity to square off
- `clientID`: String - Client ID ("DLL7182")
- `positionSquareOffQuantityType`: String - Position square off quantity type (e.g., "ExactQty")

---

### 8. Square-Off All API
- **Method:** PUT
- **Endpoint:** `https://smpb.jainam.in:4143/interactive/portfolio/squareoffall`
- **Note:** Please send clientID for which you want to square off all positions.
- **Authentication:** Use Interactive Order API A credentials

**Request Body:**
```json
{
  "squareoffMode": "NetWise",
  "clientID": "DLL7182"
}
```

**Required Parameters:**
- `squareoffMode`: String - Square-off mode ("NetWise" or "DayWise")
- `clientID`: String - Client ID ("DLL7182")

---

## Quick Reference Table

| API Type | Client ID | App Key | App Secret |
|----------|-----------|---------|------------|
| **Normal Dealer (This Doc)** | DLL7182 | Market Data: `511c4265c2869ab1f54180`<br>Interactive: `d229ee8bc6be3d81d35946` | Market Data: `Lypl445#sR`<br>Interactive: `Qiet271#eJ` |
| **Original Docs (Examples)** | ON190/ON100 | `59fcfb78db569a5f014579` (example) | `Tgmj182#ui` (example) |

---

## Document Version
- **Version:** 1.0 Production
- **Last Updated:** 2025
- **Status:** Production Ready with Actual Credentials
- **Account Type:** Normal Dealer