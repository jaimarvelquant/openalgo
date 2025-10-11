# Pro Dealer API (Regular Dealer Order Functionality)

**Base Endpoint:** `https://smpb.jainam.in:4143/`

**Client ID:** `ZZJ13048`

---

## ?? IMPORTANT NOTES - READ CAREFULLY

### 1. Client ID Distinction
This documentation uses **YOUR ACTUAL PRODUCTION Client ID**, not the example IDs from the original documentation:

| Source | Client ID Used | Purpose |
|--------|---------------|---------|
| **Original Documentation Examples** | `*****` (masked) | Sample/Example IDs only |
| **THIS DOCUMENT (Production)** | `ZZJ13048` | ? YOUR ACTUAL Client ID to use in API calls |

**Action Required:** All API calls in this document show `ZZJ13048` - this is the correct Client ID to use for your Pro Dealer account.

---

### 2. Authentication Credentials Distinction
The original documentation used example/dummy credentials. This document contains **YOUR ACTUAL PRODUCTION CREDENTIALS**:

#### Original Documentation (Examples):
- **secretKey:** `Tgmj182#ui` ? Example only
- **appKey:** `59fcfb78db569a5f014579` ? Example only

#### THIS DOCUMENT (Your Production Credentials):

**Market Data API A:**
- **App Key:** `d4a77bc14c550effbbb423` ? YOUR ACTUAL KEY
- **App Secret:** `Pqoa026@Eg` ? YOUR ACTUAL SECRET

**Interactive Order API A:**
- **App Key:** `753d09b5c21762b4e24239` ? YOUR ACTUAL KEY
- **App Secret:** `Riof561$ws` ? YOUR ACTUAL SECRET

**Action Required:** Use the credentials shown in this document for production authentication. Do NOT use the example credentials from the original documentation.

---

### 3. API Usage Distinction

| API Type | When to Use | Authentication |
|----------|-------------|----------------|
| **Market Data API A** | For fetching market data, quotes, historical data | Use App Key: `d4a77bc14c550effbbb423` |
| **Interactive Order API A** | For placing orders, modifying orders, checking positions, balances | Use App Key: `753d09b5c21762b4e24239` |

---

### 4. Key Differences Summary

| Item | Original Docs | THIS Document |
|------|---------------|---------------|
| **Client ID** | ***** (masked) | ZZJ13048 (production) |
| **Base Endpoint** | Same | `https://smpb.jainam.in:4143/` |
| **Market Data API Key** | Example key | `d4a77bc14c550effbbb423` |
| **Market Data Secret** | Example secret | `Pqoa026@Eg` |
| **Interactive API Key** | Example key | `753d09b5c21762b4e24239` |
| **Interactive API Secret** | Example secret | `Riof561$ws` |

---

### 5. Normal Dealer vs Pro Dealer Distinction

| Feature | Normal Dealer (DLL7182) | Pro Dealer (ZZJ13048 - THIS DOC) |
|---------|------------------------|-----------------------------------|
| **Client ID** | DLL7182 | ZZJ13048 |
| **Account Type** | Normal Dealer | Pro Dealer |
| **Market Data Key** | `511c4265c2869ab1f54180` | `d4a77bc14c550effbbb423` |
| **Market Data Secret** | `Lypl445#sR` | `Pqoa026@Eg` |
| **Interactive Key** | `d229ee8bc6be3d81d35946` | `753d09b5c21762b4e24239` |
| **Interactive Secret** | `Qiet271#eJ` | `Riof561$ws` |
| **API Endpoints** | Same | Same |

**Important:** Make sure you use the correct credentials for each account type. Do not mix Normal Dealer credentials with Pro Dealer operations.

---

### 6. Security Warning
?? **KEEP THESE CREDENTIALS SECURE:**
- Never commit these credentials to public repositories
- Never share these keys with unauthorized persons
- Store them in environment variables or secure vaults in production
- Rotate keys periodically as per security best practices
- Do not mix Normal Dealer and Pro Dealer credentials

---

## Authentication Credentials

### Market Data API A
- **App Key:** `d4a77bc14c550effbbb423`
- **App Secret:** `Pqoa026@Eg`
- **Purpose:** Market data, quotes, historical data

### Interactive Order API A
- **App Key:** `753d09b5c21762b4e24239`
- **App Secret:** `Riof561$ws`
- **Purpose:** Trading operations, orders, positions, balances

---

## A. Authentication

### Login (Market Data API A)
- **Method:** POST
- **Endpoint:** `https://smpb.jainam.in:4143/interactive/user/session`
- **Request Body:**
```json
{
  "secretKey": "Pqoa026@Eg",
  "appKey": "d4a77bc14c550effbbb423",
  "source": "WEBAPI"
}
```

### Login (Interactive Order API A)
- **Method:** POST
- **Endpoint:** `https://smpb.jainam.in:4143/interactive/user/session`
- **Request Body:**
```json
{
  "secretKey": "Riof561$ws",
  "appKey": "753d09b5c21762b4e24239",
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
  "clientID": "ZZJ13048"
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
- `clientID`: String - Client ID ("ZZJ13048")

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
  "clientID": "ZZJ13048"
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
- `clientID`: String - Client ID ("ZZJ13048")

---

### 3. Cancel Order API
- **Method:** DELETE
- **Endpoint:** `https://smpb.jainam.in:4143/interactive/orders?appOrderID={appOrderID}&clientID={clientID}`
- **Note:** Please send clientID for which you want to Cancel Order API.
- **Authentication:** Use Interactive Order API A credentials

**Example URL:**
```
https://smpb.jainam.in:4143/interactive/orders?appOrderID=1100062468&clientID=ZZJ13048
```

**Required Parameters:**
- `appOrderID`: Number - Application order ID to cancel
- `clientID`: String - Client ID ("ZZJ13048")

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
  "clientID": "ZZJ13048"
}
```

**Required Parameters:**
- `exchangeSegment`: String - Exchange segment
- `exchangeInstrumentID`: Number - Exchange instrument ID
- `clientID`: String - Client ID ("ZZJ13048")

---

## C. Account and Portfolio Management

### 1. Dealer Position API
- **Method:** GET
- **Endpoint:** `https://smpb.jainam.in:4143/interactive/portfolio/dealerpositions?dayOrNet={dayOrNet}&clientID={clientID}`
- **Note:** Please send clientID for which you want to check Position.
- **Authentication:** Use Interactive Order API A credentials

**Example URL:**
```
https://smpb.jainam.in:4143/interactive/portfolio/dealerpositions?dayOrNet=NetWise&clientID=ZZJ13048
```

**Required Parameters:**
- `dayOrNet`: String - Position type ("NetWise" or "DayWise")
- `clientID`: String - Client ID ("ZZJ13048")

---

### 2. Dealer TradeBook API
- **Method:** GET
- **Endpoint:** `https://smpb.jainam.in:4143/interactive/orders/dealertradebook?clientID={clientID}`
- **Note:** Please send clientID for which you want to Check TradeBook.
- **Authentication:** Use Interactive Order API A credentials

**Example URL:**
```
https://smpb.jainam.in:4143/interactive/orders/dealertradebook?clientID=ZZJ13048
```

**Required Parameters:**
- `clientID`: String - Client ID ("ZZJ13048")

---

### 3. Dealer OrderBook API
- **Method:** GET
- **Endpoint:** `https://smpb.jainam.in:4143/interactive/orders/dealerorderbook?clientID={clientID}`
- **Note:** Please send clientID for which you want to check OrderBook.
- **Authentication:** Use Interactive Order API A credentials

**Example URL:**
```
https://smpb.jainam.in:4143/interactive/orders/dealerorderbook?clientID=ZZJ13048
```

**Required Parameters:**
- `clientID`: String - Client ID ("ZZJ13048")

---

### 4. Get Balance API
- **Method:** GET
- **Endpoint:** `https://smpb.jainam.in:4143/interactive/user/balance?clientID={clientID}`
- **Note:** Please send clientID for which you want to check balance.
- **Authentication:** Use Interactive Order API A credentials

**Example URL:**
```
https://smpb.jainam.in:4143/interactive/user/balance?clientID=ZZJ13048
```

**Required Parameters:**
- `clientID`: String - Client ID ("ZZJ13048")

---

### 5. Get Holdings API
- **Method:** GET
- **Endpoint:** `https://smpb.jainam.in:4143/interactive/portfolio/holdings?clientID={clientID}`
- **Note:** Please send clientID for which you want to check holdings.
- **Authentication:** Use Interactive Order API A credentials

**Example URL:**
```
https://smpb.jainam.in:4143/interactive/portfolio/holdings?clientID=ZZJ13048
```

**Required Parameters:**
- `clientID`: String - Client ID ("ZZJ13048")

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
  "clientID": "ZZJ13048"
}
```

**Required Parameters:**
- `exchangeSegment`: String - Exchange segment
- `exchangeInstrumentID`: Number - Exchange instrument ID
- `oldProductType`: String - Current product type (e.g., "MIS")
- `newProductType`: String - Target product type (e.g., "NRML")
- `isDayWise`: Boolean - Day wise flag (true/false)
- `targetQty`: String - Quantity to convert
- `clientID`: String - Client ID ("ZZJ13048")

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
  "clientID": "ZZJ13048",
  "positionSquareOffQuantityType": "ExactQty"
}
```

**Required Parameters:**
- `exchangeSegment`: String - Exchange segment
- `exchangeInstrumentID`: Number - Exchange instrument ID
- `productType`: String - Product type (e.g., "NRML")
- `squareoffMode`: String - Square-off mode ("DayWise" or "NetWise")
- `squareOffQtyValue`: Number - Quantity to square off
- `clientID`: String - Client ID ("ZZJ13048")
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
  "clientID": "ZZJ13048"
}
```

**Required Parameters:**
- `squareoffMode`: String - Square-off mode ("NetWise" or "DayWise")
- `clientID`: String - Client ID ("ZZJ13048")

---

## Quick Reference Table

| API Type | Client ID | App Key | App Secret |
|----------|-----------|---------|------------|
| **Pro Dealer (This Doc)** | ZZJ13048 | Market Data: `d4a77bc14c550effbbb423`<br>Interactive: `753d09b5c21762b4e24239` | Market Data: `Pqoa026@Eg`<br>Interactive: `Riof561$ws` |
| **Normal Dealer** | DLL7182 | Market Data: `511c4265c2869ab1f54180`<br>Interactive: `d229ee8bc6be3d81d35946` | Market Data: `Lypl445#sR`<br>Interactive: `Qiet271#eJ` |
| **Original Docs (Examples)** | ***** (masked) | `59fcfb78db569a5f014579` (example) | `Tgmj182#ui` (example) |

---

## Document Version
- **Version:** 1.0 Production
- **Last Updated:** 2025
- **Status:** Production Ready with Actual Credentials
- **Account Type:** Pro Dealer