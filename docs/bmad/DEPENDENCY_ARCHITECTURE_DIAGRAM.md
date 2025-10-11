# MarvelQuant & OpenAlgo SDK Architecture

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         MARVELQUANT SERVER                          │
│                    (Our Rebranded Application)                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │
│  │   REST API   │  │  WebSocket   │  │   Database   │            │
│  │ (Port 5000)  │  │ (Port 8765)  │  │   (SQLite)   │            │
│  └──────┬───────┘  └──────┬───────┘  └──────────────┘            │
│         │                  │                                        │
│         │                  │                                        │
└─────────┼──────────────────┼────────────────────────────────────────┘
          │                  │
          │ HTTP/REST        │ WebSocket
          │                  │
          ▼                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    OPENALGO PYTHON SDK                              │
│              (External Client Library - PyPI)                       │
│                   pip install openalgo                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  from openalgo import api                                          │
│                                                                     │
│  client = api(                                                     │
│      api_key="...",                                                │
│      host="http://127.0.0.1:5000",  ← Points to MarvelQuant       │
│      ws_url="ws://127.0.0.1:8765"   ← Points to MarvelQuant       │
│  )                                                                 │
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │
│  │ REST Client  │  │   WebSocket  │  │   Strategy   │            │
│  │   Methods    │  │    Client    │  │   Manager    │            │
│  └──────────────┘  └──────────────┘  └──────────────┘            │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
          │
          │ Used by
          │
          ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    OUR CLIENT CODE                                  │
│              (Strategies, Tests, Services)                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────────┐  ┌──────────────────┐  ┌─────────────────┐ │
│  │   Strategies     │  │      Tests       │  │   MCP Server    │ │
│  │  (8 files)       │  │    (4 files)     │  │   (2 files)     │ │
│  │                  │  │                  │  │                 │ │
│  │ • ltp_example.py │  │ • test_broker.py │  │ • mcpserver.py  │ │
│  │ • ema_cross.py   │  │ • test_history   │  │ • test_mcp.py   │ │
│  │ • supertrend.py  │  │ • ltp_test       │  │                 │ │
│  └──────────────────┘  └──────────────────┘  └─────────────────┘ │
│                                                                     │
│  ┌──────────────────┐  ┌──────────────────┐                       │
│  │  Download Scripts│  │  Telegram Bot    │                       │
│  │    (2 files)     │  │    (3 files)     │                       │
│  │                  │  │                  │                       │
│  │ • ieod.py        │  │ • telegram_bot   │                       │
│  │ • sqlite_dl.py   │  │   _service.py    │                       │
│  └──────────────────┘  └──────────────────┘                       │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Key Relationships

### 1. **MarvelQuant Server** (Our Application)
- **What it is:** Flask-based trading platform server
- **What it does:** Provides REST API and WebSocket feeds
- **Ports:** 5000 (HTTP), 8765 (WebSocket)
- **Rebranding:** OpenAlgo → MarvelQuant ✅

### 2. **OpenAlgo SDK** (External Library)
- **What it is:** Python client library (like `requests`)
- **What it does:** Connects TO MarvelQuant server
- **Source:** PyPI (`pip install openalgo`)
- **Maintained by:** Community (marketcalls)
- **Rebranding:** Stays as "openalgo" ✅

### 3. **Our Client Code** (Strategies/Tests/Services)
- **What it is:** Example code and services
- **What it does:** Uses OpenAlgo SDK to connect to MarvelQuant
- **Rebranding:** Update comments/docs to reference MarvelQuant ✅

---

## Data Flow Example

```
┌─────────────────────────────────────────────────────────────────┐
│ STEP 1: User runs strategy                                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ python strategies/ltp_example.py                                │
│                                                                 │
│ from openalgo import api                                        │
│ client = api(host="http://127.0.0.1:5000")                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 2: OpenAlgo SDK makes HTTP request                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ POST http://127.0.0.1:5000/api/v1/placeorder                   │
│ Headers: { "X-API-KEY": "..." }                                │
│ Body: { "symbol": "RELIANCE", "action": "BUY", ... }           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 3: MarvelQuant Server processes request                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Flask route: /api/v1/placeorder                                │
│ - Validates API key                                            │
│ - Calls broker API (Zerodha, Angel, etc.)                      │
│ - Returns response                                             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 4: Response flows back                                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ OpenAlgo SDK receives response                                 │
│ Returns to strategy code                                       │
└─────────────────────────────────────────────────────────────────┘
```

---

## Namespace Isolation

### Python Import Resolution

```python
# When you write:
from openalgo import api

# Python looks in this order:
# 1. Current directory (./openalgo.py) ❌ Not found
# 2. PYTHONPATH directories ❌ Not found
# 3. Site-packages (/path/to/site-packages/openalgo/) ✅ FOUND!
#
# Result: Imports the external PyPI package
```

### No Collision Because:

```
Our Project Structure:
/Users/maruth/projects/openalgo/
├── app.py                    ← MarvelQuant server
├── blueprints/               ← Server routes
├── broker/                   ← Broker integrations
├── strategies/               ← Client code using SDK
│   └── ltp_example.py        ← Uses: from openalgo import api
└── requirements.txt          ← Lists: openalgo==1.0.32

External Library (in site-packages):
/path/to/site-packages/openalgo/
├── __init__.py
├── api.py                    ← The 'api' class we import
└── ...

NO OVERLAP! Different locations, different purposes.
```

---

## Analogy: Web Server vs HTTP Client

```
┌─────────────────────────────────────────────────────────────────┐
│                         APACHE SERVER                           │
│                    (Like MarvelQuant)                           │
│                                                                 │
│  Serves HTTP requests on port 80                               │
│  Renamed from "Apache" to "MyWebServer"                        │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │ HTTP Requests
                              │
┌─────────────────────────────────────────────────────────────────┐
│                         CURL LIBRARY                            │
│                    (Like openalgo SDK)                          │
│                                                                 │
│  Makes HTTP requests to servers                                │
│  Still called "curl" even if server renamed                    │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │ Used by
                              │
┌─────────────────────────────────────────────────────────────────┐
│                      YOUR BASH SCRIPTS                          │
│                  (Like our strategies)                          │
│                                                                 │
│  curl http://localhost/api/data                                │
└─────────────────────────────────────────────────────────────────┘
```

**Key Point:** Renaming Apache to "MyWebServer" doesn't affect `curl` command!

---

## Rebranding Impact Matrix

| Component | Old Name | New Name | Impact |
|-----------|----------|----------|--------|
| **Server** | OpenAlgo | MarvelQuant | ✅ Rename |
| **Client SDK** | openalgo | openalgo | ✅ Keep as-is |
| **PyPI Package** | openalgo | openalgo | ✅ No change |
| **Import Statement** | `from openalgo import api` | `from openalgo import api` | ✅ No change |
| **Server URL** | `http://127.0.0.1:5000` | `http://127.0.0.1:5000` | ✅ No change |
| **API Endpoints** | `/api/v1/placeorder` | `/api/v1/placeorder` | ✅ No change |

**Conclusion:** Server rebranding doesn't affect client SDK!

---

## Testing Strategy

### Before Rebranding
```bash
# Test that SDK connects to server
python strategies/ltp_example.py
# ✅ Should work
```

### After Rebranding
```bash
# Test that SDK still connects to server
python strategies/ltp_example.py
# ✅ Should still work (same HTTP endpoints)
```

### Why It Works
- SDK connects via HTTP/WebSocket
- HTTP endpoints don't change
- Server name is just branding
- API contract remains the same

---

## Summary

```
┌─────────────────────────────────────────────────────────────────┐
│                    SIMPLE EXPLANATION                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  MarvelQuant = The SERVER (our application)                    │
│  openalgo    = The CLIENT SDK (external library)               │
│                                                                 │
│  Just like:                                                    │
│  - Gmail = Server, Thunderbird = Client                        │
│  - Apache = Server, curl = Client                              │
│  - MySQL = Server, mysql-connector = Client                    │
│                                                                 │
│  Renaming the server doesn't affect the client!                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

**See Also:**
- Full Analysis: `docs/bmad/DEPENDENCY_CONFLICT_ANALYSIS.md`
- Quick Reference: `docs/bmad/DEPENDENCY_QUICK_REFERENCE.md`

