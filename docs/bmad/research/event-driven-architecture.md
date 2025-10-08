# Event-Driven Architecture for Indian Brokers (Jainam & Zerodha)
## Phase 0: Foundation for US Broker Integration

**Document Version:** 1.0  
**Last Updated:** 2025-10-08  
**Status:** Implementation Plan  
**Timeline:** 2 weeks (10 working days)

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Why Event-Driven Architecture is Critical](#why-event-driven-architecture-is-critical)
3. [Vn.py EventEngine Adaptation Strategy](#vnpy-eventengine-adaptation-strategy)
4. [BrokerAdapter Base Class Refactoring](#brokeradapter-base-class-refactoring)
5. [Jainam_prop Migration Plan](#jainam_prop-migration-plan)
6. [Zerodha Migration Plan](#zerodha-migration-plan)
7. [Week-by-Week Implementation Timeline](#week-by-week-implementation-timeline)
8. [Code Templates](#code-templates)
9. [Performance Benefits Analysis](#performance-benefits-analysis)
10. [Risk Mitigation and Rollback Plan](#risk-mitigation-and-rollback-plan)
11. [Success Metrics](#success-metrics)

---

## Executive Summary

### Purpose

This document outlines the implementation of **event-driven architecture** for OpenAlgo's existing Indian broker integrations (Jainam_prop and Zerodha) as **Phase 0** of the US broker integration roadmap. This foundational work is critical for both Indian and US brokers, providing:

1. **Real-time order updates** (10-100x latency reduction: from 1-2 seconds to <100ms)
2. **Unified architecture** across all brokers (Indian + US)
3. **Production-grade event engine** (adapted from Vn.py's proven implementation)
4. **Scalable foundation** for future broker integrations

### Why Event-Driven for Indian Brokers?

**Critical Finding:** Indian markets are **MORE latency-sensitive** than US markets due to:

- **Higher volatility**: NIFTY can move 100+ points in minutes, BANKNIFTY 500+ points
- **MIS (intraday) leverage**: 5-10x leverage requires real-time position monitoring
- **Auto-squareoff deadlines**: 3:15 PM auto-squareoff requires precise timing
- **Fast-paced options trading**: Weekly options have rapid premium decay

**Current Limitation:** OpenAlgo has sophisticated WebSocket for market data but **NO real-time order updates**. Orders use REST API only, requiring manual refresh.

**Solution:** Implement event-driven architecture with WebSocket/postback for order updates.

### Scope

**Phase 0 (Week 1-2):**
- **Week 1**: Event engine implementation + Jainam_prop migration
- **Week 2**: Zerodha migration (if time permits)

**Deliverables:**
- ✅ Event engine operational (adapted from Vn.py)
- ✅ Jainam_prop using event-driven updates
- ✅ Proven architecture for US broker integration (Phase 1+)

---

## Why Event-Driven Architecture is Critical

### Current Architecture (REST Polling)

```
Current OpenAlgo Architecture (Indian Brokers)

Market Data Flow (WebSocket):
    Zerodha KiteTicker WebSocket
        ↓
    zerodha_websocket.py (1800+ symbols)
        ↓
    Flask-SocketIO
        ↓
    Frontend (real-time charts)

Order Execution Flow (REST):
    Frontend/API
        ↓
    place_order_service.py
        ↓
    broker/zerodha/api/order_api.py (REST)
        ↓
    Zerodha Kite API (REST)
        ↓
    Order placed
        ↓
    ??? (No real-time order updates)
        ↓
    User must manually refresh order book
```

**Problems:**
1. ❌ No real-time order updates
2. ❌ High latency (1-2 seconds for status updates)
3. ❌ Poor user experience (manual refresh required)
4. ❌ Can't implement automated stop-loss adjustments
5. ❌ Missed trading opportunities due to delayed notifications

### Proposed Event-Driven Architecture

```
Event-Driven OpenAlgo Architecture

Market Data Flow (WebSocket):
    [Same as current - already event-driven]

Order Execution Flow (Event-Driven):
    Frontend/API
        ↓
    place_order_service.py
        ↓
    broker/jainam_prop/jainam_adapter.py
        ↓
    Jainam API (REST for placement)
        ↓
    Order placed
        ↓
    Jainam WebSocket/Postback (real-time updates)
        ↓
    jainam_adapter.on_order(order)
        ↓
    Event Engine
        ↓
    Event Handlers (Portfolio Manager, Risk Manager, UI)
        ↓
    Real-time UI updates (<100ms)
```

**Benefits:**
1. ✅ Real-time order updates (<100ms latency)
2. ✅ Automated risk management (stop-loss, position limits)
3. ✅ Excellent user experience (instant notifications)
4. ✅ Unified architecture (same pattern for all brokers)
5. ✅ Scalable (supports 100+ concurrent users)

### Latency Comparison

| Scenario | REST Polling (2 sec interval) | WebSocket/Postback | Improvement |
|----------|------------------------------|-------------------|-------------|
| **Order placed → Status update** | 0-2 seconds (avg 1 sec) | <100ms | **10x faster** |
| **Order filled → Notification** | 0-2 seconds (avg 1 sec) | <100ms | **10x faster** |
| **Order rejected → Alert** | 0-2 seconds (avg 1 sec) | <100ms | **10x faster** |
| **API calls per minute** | 30 calls (60 sec / 2 sec) | 0 calls (event-driven) | **100% reduction** |

### Real-World Impact: NIFTY Intraday Straddle

**Scenario:**
- Place ATM straddle at 9:20 AM
- NIFTY moves 50 points in 30 seconds
- Need to adjust stop loss immediately

**With REST Polling:**
- Order placed at 9:20:00
- Status update at 9:20:02 (2 sec delay)
- By then, NIFTY moved 20 points
- **Loss**: ₹1,000 per lot (50 qty × 20 points)

**With WebSocket:**
- Order placed at 9:20:00
- Status update at 9:20:00.1 (100ms delay)
- Immediate stop loss adjustment
- **Loss**: ₹100 per lot (50 qty × 2 points)

**Savings**: ₹900 per lot = **90% reduction in slippage**

---

## Vn.py EventEngine Adaptation Strategy

### Source Code Reference

**Original Vn.py EventEngine**: `/tmp/vnpy/vnpy/event/engine.py`

**Key Features:**
1. ✅ Thread-safe queue for event handling
2. ✅ Timer events (periodic tasks every 1 second)
3. ✅ Type-specific handlers (register for specific event types)
4. ✅ General handlers (register for all event types)
5. ✅ Clean start/stop lifecycle management

### Adaptation Approach

**What to Adopt:**
1. ✅ Thread-safe Queue pattern
2. ✅ Timer events for periodic tasks
3. ✅ Handler registration system
4. ✅ Event processing loop

**What to Modify:**
1. ⚠️ Use Enum for event types (instead of strings) - Type safety
2. ⚠️ Add OpenAlgo-specific event types
3. ⚠️ Integrate with Flask-SocketIO for UI updates
4. ⚠️ Add error handling for disconnected sessions

### Event Types

```python
# openalgo/core/event_types.py

from enum import Enum

class EventType(Enum):
    """Event types for OpenAlgo event engine"""
    
    # Timer events
    TIMER = "timer"
    
    # Order events
    ORDER_UPDATE = "order_update"
    ORDER_PLACED = "order_placed"
    ORDER_FILLED = "order_filled"
    ORDER_REJECTED = "order_rejected"
    ORDER_CANCELLED = "order_cancelled"
    
    # Trade events
    TRADE_UPDATE = "trade_update"
    
    # Position events
    POSITION_UPDATE = "position_update"
    
    # Account events
    ACCOUNT_UPDATE = "account_update"
    
    # Error events
    ERROR = "error"
    
    # Connection events
    BROKER_CONNECTED = "broker_connected"
    BROKER_DISCONNECTED = "broker_disconnected"
```

### Implementation Effort

| Task | Effort | Description |
|------|--------|-------------|
| **Study Vn.py EventEngine** | 0.5 days | Understand code structure |
| **Create EventEngine class** | 1 day | Adapt Vn.py implementation |
| **Create EventType enum** | 0.5 days | Define OpenAlgo event types |
| **Integration testing** | 1 day | Test event flow end-to-end |
| **Total** | **3 days** | **Week 1: Days 1-3** |

---

## BrokerAdapter Base Class Refactoring

### Current BrokerAdapter (Hypothetical)

```python
# Current approach (REST-only)
class BrokerAdapter(ABC):
    def __init__(self, auth_config):
        self.auth_config = auth_config
        self.connected = False
    
    @abstractmethod
    def connect(self) -> bool:
        pass
    
    @abstractmethod
    def place_order(self, order_data: dict) -> OrderResponse:
        pass
    
    @abstractmethod
    def cancel_order(self, order_id: str) -> bool:
        pass
    
    @abstractmethod
    def get_order_status(self, order_id: str) -> OrderStatus:
        """REST API call - requires polling"""
        pass
```

### Event-Driven BrokerAdapter

```python
# openalgo/broker/base_adapter.py (REFACTORED)

from abc import ABC, abstractmethod
from openalgo.core.event_engine import event_engine, Event, EventType
from openalgo.models import OrderResponse, OrderStatus, Position

class BrokerAdapter(ABC):
    """
    Base broker adapter with event-driven updates
    
    Adapts Vn.py's BaseGateway pattern for OpenAlgo
    """
    
    def __init__(self, auth_config):
        self.auth_config = auth_config
        self.connected = False
        self.gateway_name = auth_config.broker_name
    
    # Event-driven update methods (push model)
    def on_order(self, order: OrderStatus):
        """
        Push order update event
        
        Called by broker adapter when order status changes
        (via WebSocket, postback, or polling)
        """
        event = Event(EventType.ORDER_UPDATE, order)
        event_engine.put(event)
    
    def on_trade(self, trade: dict):
        """Push trade event"""
        event = Event(EventType.TRADE_UPDATE, trade)
        event_engine.put(event)
    
    def on_position(self, position: Position):
        """Push position update event"""
        event = Event(EventType.POSITION_UPDATE, position)
        event_engine.put(event)
    
    def on_account(self, account: dict):
        """Push account update event"""
        event = Event(EventType.ACCOUNT_UPDATE, account)
        event_engine.put(event)
    
    def on_error(self, error: str):
        """Push error event"""
        event = Event(EventType.ERROR, {"broker": self.gateway_name, "error": error})
        event_engine.put(event)
    
    # Abstract methods (must be implemented by broker adapters)
    @abstractmethod
    def connect(self) -> bool:
        """Connect to broker"""
        pass
    
    @abstractmethod
    def place_order(self, order_data: dict) -> OrderResponse:
        """Place order"""
        pass
    
    @abstractmethod
    def cancel_order(self, order_id: str) -> bool:
        """Cancel order"""
        pass
```

### Refactoring Effort

| Task | Effort | Description |
|------|--------|-------------|
| **Add event methods** | 0.5 days | Add on_order(), on_trade(), on_position() |
| **Update existing adapters** | 0.5 days | Update method signatures |
| **Testing** | 1 day | Test event flow with mock broker |
| **Total** | **2 days** | **Week 1: Days 4-5** |

---

## Jainam_prop Migration Plan

### Current Implementation Analysis

**Current Jainam_prop Structure:**

```
broker/jainam_prop/
├── api/
│   ├── order_api.py          # REST API for orders
│   ├── data_api.py            # REST API for market data
│   └── auth_api.py            # Authentication
├── mapping/
│   └── transform_data.py      # Data transformation
└── __init__.py
```

**Current Order Flow (REST-only):**

```python
# Hypothetical current implementation
def place_order(order_data):
    # Place order via REST API
    response = requests.post(
        "https://jainam-api.com/orders",
        json=order_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    # Return order ID
    return response.json()["order_id"]

# No real-time updates - user must poll
def get_order_status(order_id):
    response = requests.get(
        f"https://jainam-api.com/orders/{order_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    return response.json()
```

### WebSocket/Postback Listener Implementation

**Jainam API Capabilities** (to be verified):

**Option 1: WebSocket for Order Updates**
```python
# If Jainam provides WebSocket
import websocket

class JainamWebSocket:
    def __init__(self, token, on_order_update):
        self.token = token
        self.on_order_update = on_order_update
        self.ws = None

    def connect(self):
        ws_url = f"wss://jainam-api.com/ws?token={self.token}"
        self.ws = websocket.WebSocketApp(
            ws_url,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close
        )
        self.ws.run_forever()

    def _on_message(self, ws, message):
        data = json.loads(message)
        if data["type"] == "order_update":
            self.on_order_update(data)
```

**Option 2: HTTP Postback (Webhook)**
```python
# If Jainam uses HTTP postback
from flask import Flask, request

app = Flask(__name__)

@app.route("/jainam/postback", methods=["POST"])
def jainam_postback():
    """
    Receive order updates from Jainam via HTTP POST
    """
    data = request.json

    # Verify signature (if provided)
    if not verify_jainam_signature(data, request.headers):
        return {"error": "Invalid signature"}, 401

    # Parse order update
    order_update = parse_jainam_order_update(data)

    # Push to event engine
    jainam_adapter.on_order(order_update)

    return {"status": "success"}, 200
```

**Option 3: Polling with Event Engine (Fallback)**
```python
# If no WebSocket/postback, use timer events for polling
def on_timer(event):
    """Called every 1 second by event engine"""
    # Poll active orders
    for order_id in active_orders:
        status = get_order_status(order_id)

        # Check if status changed
        if status != cached_status[order_id]:
            # Push event
            jainam_adapter.on_order(status)
            cached_status[order_id] = status
```

### Event-Driven Jainam Adapter

```python
# openalgo/broker/jainam_prop/jainam_adapter.py (NEW)

from openalgo.broker.base_adapter import BrokerAdapter
from openalgo.models import OrderResponse, OrderStatus
import websocket
import json
import threading

class JainamAdapter(BrokerAdapter):
    """
    Jainam_prop adapter with event-driven order updates
    """

    def __init__(self, auth_config):
        super().__init__(auth_config)
        self.ws = None
        self.ws_thread = None

    def connect(self) -> bool:
        """Connect to Jainam API"""
        try:
            # Authenticate
            self.token = self._authenticate()

            # Start WebSocket for order updates
            self._start_websocket()

            self.connected = True
            return True
        except Exception as e:
            logger.error(f"Jainam connection failed: {e}")
            return False

    def _start_websocket(self):
        """Start WebSocket connection for order updates"""
        ws_url = f"wss://jainam-api.com/ws?token={self.token}"

        self.ws = websocket.WebSocketApp(
            ws_url,
            on_message=self._on_ws_message,
            on_error=self._on_ws_error,
            on_close=self._on_ws_close,
            on_open=self._on_ws_open
        )

        # Run WebSocket in separate thread
        self.ws_thread = threading.Thread(target=self.ws.run_forever)
        self.ws_thread.daemon = True
        self.ws_thread.start()

    def _on_ws_message(self, ws, message):
        """Handle WebSocket message"""
        try:
            data = json.loads(message)

            if data["type"] == "order_update":
                # Parse order update
                order = self._parse_order_update(data)

                # Push event
                self.on_order(order)

            elif data["type"] == "trade_update":
                # Parse trade update
                trade = self._parse_trade_update(data)

                # Push event
                self.on_trade(trade)

        except Exception as e:
            logger.error(f"Error processing WebSocket message: {e}")

    def _parse_order_update(self, data: dict) -> OrderStatus:
        """Parse Jainam order update to OpenAlgo format"""
        return OrderStatus(
            order_id=data["order_id"],
            symbol=data["symbol"],
            status=self._map_status(data["status"]),
            filled_quantity=data["filled_qty"],
            remaining_quantity=data["pending_qty"],
            average_price=data["avg_price"],
            order_type=data["order_type"],
            side=data["side"]
        )

    def place_order(self, order_data: dict) -> OrderResponse:
        """Place order via REST API"""
        try:
            # Place order via REST
            response = requests.post(
                "https://jainam-api.com/orders",
                json=self._transform_order(order_data),
                headers={"Authorization": f"Bearer {self.token}"}
            )

            # Order updates will come via WebSocket
            return OrderResponse(
                success=True,
                order_id=response.json()["order_id"]
            )
        except Exception as e:
            return OrderResponse(
                success=False,
                error_message=str(e)
            )
```

### Testing Strategy

**Test Cases:**

1. **Order Placement**
   - Place market order
   - Place limit order
   - Verify order ID returned
   - Verify order event received via WebSocket

2. **Order Status Updates**
   - Order placed → PENDING event
   - Order filled → FILLED event
   - Order rejected → REJECTED event
   - Verify <100ms latency

3. **Order Cancellation**
   - Cancel pending order
   - Verify CANCELLED event received

4. **WebSocket Reconnection**
   - Disconnect WebSocket
   - Verify automatic reconnection
   - Verify order updates resume

5. **Fallback to REST Polling**
   - Disable WebSocket
   - Verify timer-based polling works
   - Verify events still generated

**Testing Environment:**
- Jainam paper trading account
- Mock WebSocket server (for unit tests)
- Integration tests with real Jainam API

### Implementation Effort

| Task | Effort | Description |
|------|--------|-------------|
| **Analyze Jainam API** | 0.5 days | Verify WebSocket/postback support |
| **Implement WebSocket client** | 1 day | Connect, subscribe, handle messages |
| **Implement event handlers** | 0.5 days | Parse updates, push events |
| **Implement fallback polling** | 0.5 days | Timer-based polling if no WebSocket |
| **Testing** | 1.5 days | Unit tests, integration tests |
| **Total** | **4 days** | **Week 1: Days 6-7, Week 2: Days 1-2** |

---

## Zerodha Migration Plan

### Current Implementation Analysis

**Current Zerodha Structure:**

```
broker/zerodha/
├── api/
│   ├── order_api.py          # REST API for orders
│   └── data_api.py            # REST API for market data
├── streaming/
│   ├── zerodha_websocket.py  # WebSocket for MARKET DATA only
│   ├── zerodha_adapter.py    # Adapter for market data
│   └── zerodha_mapping.py    # Symbol mapping
└── mapping/
    └── transform_data.py      # Data transformation
```

**Key Finding:** Zerodha already has WebSocket implementation for **market data** (1800+ symbols), but **NOT for order updates**.

### Zerodha Postback URL Implementation

**Zerodha API:** Uses **HTTP Postback** (webhook) for order updates, NOT WebSocket.

**Postback Configuration:**

```python
# When placing order, specify postback URL
order_params = {
    "tradingsymbol": "NIFTY25AUG25000CE",
    "exchange": "NFO",
    "transaction_type": "BUY",
    "quantity": 50,
    "order_type": "MARKET",
    "product": "MIS",
    "tag": "openalgo",
    # Postback URL (optional)
    # Note: Zerodha sends updates to this URL
}
```

**Postback Payload (from Zerodha):**

```json
{
    "order_id": "240822000000123",
    "status": "COMPLETE",
    "filled_quantity": 50,
    "average_price": 125.50,
    "order_timestamp": "2024-08-22 09:20:15",
    "exchange_timestamp": "2024-08-22 09:20:15",
    "tradingsymbol": "NIFTY25AUG25000CE",
    "exchange": "NFO",
    "transaction_type": "BUY",
    "product": "MIS"
}
```

### Event-Driven Zerodha Adapter

```python
# openalgo/broker/zerodha/zerodha_adapter.py (NEW)

from openalgo.broker.base_adapter import BrokerAdapter
from openalgo.models import OrderResponse, OrderStatus
from flask import Flask, request
import hmac
import hashlib

class ZerodhaAdapter(BrokerAdapter):
    """
    Zerodha adapter with event-driven order updates via postback
    """

    def __init__(self, auth_config):
        super().__init__(auth_config)
        self.postback_url = "https://openalgo.example.com/zerodha/postback"

    def connect(self) -> bool:
        """Connect to Zerodha API"""
        try:
            # Authenticate
            self.kite = KiteConnect(api_key=self.auth_config.api_key)
            self.kite.set_access_token(self.auth_config.api_secret)

            self.connected = True
            return True
        except Exception as e:
            logger.error(f"Zerodha connection failed: {e}")
            return False

    def place_order(self, order_data: dict) -> OrderResponse:
        """Place order with postback URL"""
        try:
            # Transform order data
            zerodha_order = self._transform_order(order_data)

            # Add postback URL (if supported by Zerodha)
            # Note: Zerodha may not support per-order postback
            # In that case, use global postback configuration

            # Place order
            order_id = self.kite.place_order(
                variety=self.kite.VARIETY_REGULAR,
                **zerodha_order
            )

            # Order updates will come via postback
            return OrderResponse(
                success=True,
                order_id=str(order_id)
            )
        except Exception as e:
            return OrderResponse(
                success=False,
                error_message=str(e)
            )

# Flask route for postback
@app.route("/zerodha/postback", methods=["POST"])
def zerodha_postback():
    """
    Receive order updates from Zerodha via HTTP POST
    """
    data = request.json

    # Verify checksum (if provided by Zerodha)
    if not verify_zerodha_checksum(data, request.headers):
        return {"error": "Invalid checksum"}, 401

    # Parse order update
    order = OrderStatus(
        order_id=data["order_id"],
        symbol=data["tradingsymbol"],
        status=map_zerodha_status(data["status"]),
        filled_quantity=data["filled_quantity"],
        remaining_quantity=data["quantity"] - data["filled_quantity"],
        average_price=data["average_price"],
        order_type=data["order_type"],
        side=data["transaction_type"]
    )

    # Push to event engine
    zerodha_adapter.on_order(order)

    return {"status": "success"}, 200
```

### Implementation Effort

| Task | Effort | Description |
|------|--------|-------------|
| **Analyze Zerodha postback** | 0.5 days | Verify postback support, payload format |
| **Implement postback endpoint** | 1 day | Flask route, signature verification |
| **Implement event handlers** | 0.5 days | Parse updates, push events |
| **Testing** | 1 day | Unit tests, integration tests |
| **Total** | **3 days** | **Week 2: Days 3-5** (if time permits) |

---

## Week-by-Week Implementation Timeline

### Week 1: Event Engine + Jainam

**Days 1-3: Event Engine Implementation**

- [ ] **Day 1**: Study Vn.py EventEngine
  - Clone Vn.py repository
  - Study `/tmp/vnpy/vnpy/event/engine.py`
  - Understand thread-safe queue pattern
  - Understand timer events

- [ ] **Day 2**: Create OpenAlgo EventEngine
  - Create `openalgo/core/event_engine.py`
  - Adapt Vn.py's EventEngine class
  - Create EventType enum
  - Add error handling for Flask-SocketIO

- [ ] **Day 3**: Testing
  - Unit tests for event engine
  - Test event registration/unregistration
  - Test timer events
  - Test event flow end-to-end

**Days 4-5: BrokerAdapter Refactoring**

- [ ] **Day 4**: Refactor BrokerAdapter
  - Add `on_order()`, `on_trade()`, `on_position()` methods
  - Update method signatures
  - Create mock broker for testing

- [ ] **Day 5**: Integration Testing
  - Test event flow with mock broker
  - Test Flask-SocketIO integration
  - Test UI updates

**Days 6-7: Jainam Migration (Part 1)**

- [ ] **Day 6**: Analyze Jainam API
  - Verify WebSocket/postback support
  - Document API endpoints
  - Test authentication

- [ ] **Day 7**: Implement WebSocket client
  - Create JainamWebSocket class
  - Implement connection logic
  - Implement message parsing

### Week 2: Jainam Completion + Zerodha (Optional)

**Days 1-2: Jainam Migration (Part 2)**

- [ ] **Day 1**: Implement event handlers
  - Parse order updates
  - Push events to event engine
  - Implement fallback polling

- [ ] **Day 2**: Testing
  - Unit tests
  - Integration tests with Jainam paper account
  - End-to-end testing

**Days 3-5: Zerodha Migration (If Time Permits)**

- [ ] **Day 3**: Analyze Zerodha postback
  - Verify postback support
  - Document payload format
  - Test postback endpoint

- [ ] **Day 4**: Implement postback endpoint
  - Create Flask route
  - Implement signature verification
  - Parse order updates

- [ ] **Day 5**: Testing
  - Unit tests
  - Integration tests with Zerodha
  - End-to-end testing

---

## Code Templates

### 1. Event Engine

```python
# openalgo/core/event_engine.py

from collections import defaultdict
from queue import Empty, Queue
from threading import Thread
from time import sleep
from typing import Any, Callable
from openalgo.core.event_types import EventType
from openalgo.utils.logging import get_logger

logger = get_logger(__name__)


class Event:
    """Event object"""

    def __init__(self, type: EventType, data: Any = None) -> None:
        self.type = type
        self.data = data


HandlerType = Callable[[Event], None]


class EventEngine:
    """
    Event engine for OpenAlgo (adapted from Vn.py)

    Features:
    - Thread-safe event queue
    - Timer events (every 1 second)
    - Type-specific handlers
    - General handlers (all events)
    """

    def __init__(self, interval: int = 1) -> None:
        """
        Initialize event engine

        Args:
            interval: Timer event interval in seconds (default: 1)
        """
        self._interval = interval
        self._queue = Queue()
        self._active = False
        self._thread = Thread(target=self._run, daemon=True)
        self._timer = Thread(target=self._run_timer, daemon=True)
        self._handlers = defaultdict(list)
        self._general_handlers = []

    def _run(self) -> None:
        """Process events from queue"""
        while self._active:
            try:
                event = self._queue.get(block=True, timeout=1)
                self._process(event)
            except Empty:
                pass

    def _process(self, event: Event) -> None:
        """Distribute event to handlers"""
        # Type-specific handlers
        if event.type in self._handlers:
            for handler in self._handlers[event.type]:
                try:
                    handler(event)
                except Exception as e:
                    logger.error(f"Error in event handler: {e}")

        # General handlers
        for handler in self._general_handlers:
            try:
                handler(event)
            except Exception as e:
                logger.error(f"Error in general handler: {e}")

    def _run_timer(self) -> None:
        """Generate timer events"""
        while self._active:
            sleep(self._interval)
            event = Event(EventType.TIMER)
            self.put(event)

    def start(self) -> None:
        """Start event engine"""
        self._active = True
        self._thread.start()
        self._timer.start()
        logger.info("Event engine started")

    def stop(self) -> None:
        """Stop event engine"""
        self._active = False
        self._timer.join()
        self._thread.join()
        logger.info("Event engine stopped")

    def put(self, event: Event) -> None:
        """Put event in queue"""
        self._queue.put(event)

    def register(self, type: EventType, handler: HandlerType) -> None:
        """Register handler for event type"""
        handler_list = self._handlers[type]
        if handler not in handler_list:
            handler_list.append(handler)

    def unregister(self, type: EventType, handler: HandlerType) -> None:
        """Unregister handler"""
        handler_list = self._handlers[type]
        if handler in handler_list:
            handler_list.remove(handler)
        if not handler_list:
            self._handlers.pop(type)

    def register_general(self, handler: HandlerType) -> None:
        """Register general handler (all events)"""
        if handler not in self._general_handlers:
            self._general_handlers.append(handler)

    def unregister_general(self, handler: HandlerType) -> None:
        """Unregister general handler"""
        if handler in self._general_handlers:
            self._general_handlers.remove(handler)


# Global event engine instance
event_engine = EventEngine()
```

### 2. Event-Driven BrokerAdapter

See [BrokerAdapter Base Class Refactoring](#brokeradapter-base-class-refactoring) section above.

### 3. Portfolio Manager Event Handler

```python
# openalgo/services/portfolio_manager.py (MODIFIED)

from openalgo.core.event_engine import event_engine, Event, EventType

class PortfolioManager:
    """Portfolio manager with event-driven updates"""

    def __init__(self):
        # Register for order events
        event_engine.register(EventType.ORDER_UPDATE, self.on_order_update)
        event_engine.register(EventType.POSITION_UPDATE, self.on_position_update)
        event_engine.register(EventType.TIMER, self.on_timer)

    def on_order_update(self, event: Event):
        """Handle order update event"""
        order = event.data

        # Update local order cache
        self.orders[order.order_id] = order

        # Check if order filled
        if order.status == "FILLED":
            # Update positions
            self.update_position(order)

            # Check stop loss / target
            self.check_exit_conditions(order)

        # Emit to UI via Flask-SocketIO
        socketio.emit('order_update', order.to_dict())

    def on_position_update(self, event: Event):
        """Handle position update event"""
        position = event.data

        # Update local position cache
        self.positions[position.symbol] = position

        # Emit to UI
        socketio.emit('position_update', position.to_dict())

    def on_timer(self, event: Event):
        """Handle timer event (every 1 second)"""
        # Check MIS auto-squareoff time
        if self.is_near_squareoff_time():
            self.squareoff_mis_positions()

        # Check margin requirements
        self.check_margin()

        # Reconcile positions
        if self.timer_count % 60 == 0:  # Every 60 seconds
            self.reconcile_positions()

        self.timer_count += 1
```

---

## Performance Benefits Analysis

### Latency Reduction

| Metric | REST Polling | Event-Driven | Improvement |
|--------|-------------|--------------|-------------|
| **Order placed → UI update** | 1-2 seconds | <100ms | **10-20x faster** |
| **Order filled → Notification** | 1-2 seconds | <100ms | **10-20x faster** |
| **Position update → UI** | 2-5 seconds | <100ms | **20-50x faster** |

### API Call Reduction

| Scenario | REST Polling | Event-Driven | Reduction |
|----------|-------------|--------------|-----------|
| **10 active orders** | 300 calls/min | 0 calls/min | **100%** |
| **100 active orders** | 3000 calls/min | 0 calls/min | **100%** |

### User Experience Improvement

| Feature | REST Polling | Event-Driven |
|---------|-------------|--------------|
| **Real-time updates** | ❌ Manual refresh | ✅ Instant (<100ms) |
| **Order notifications** | ❌ Delayed (1-2 sec) | ✅ Instant |
| **Position tracking** | ❌ Delayed (2-5 sec) | ✅ Real-time |
| **Stop-loss automation** | ❌ Not possible | ✅ Fully automated |

---

## Risk Mitigation and Rollback Plan

### Identified Risks

**Risk 1: WebSocket/Postback Reliability**
- **Impact**: High (no order updates if WebSocket fails)
- **Probability**: Medium
- **Mitigation**: Implement fallback to REST polling
- **Detection**: Monitor WebSocket connection status

**Risk 2: Event Engine Performance**
- **Impact**: Medium (delayed events if queue backs up)
- **Probability**: Low
- **Mitigation**: Monitor queue size, add alerts
- **Detection**: Log queue size every 10 seconds

**Risk 3: Migration Breaks Existing Functionality**
- **Impact**: High (existing users affected)
- **Probability**: Low
- **Mitigation**: Feature flags, gradual rollout
- **Detection**: Comprehensive testing before deployment

### Feature Flags

```python
# Feature flag for event-driven updates
USE_EVENT_DRIVEN = os.getenv("USE_EVENT_DRIVEN", "false").lower() == "true"

if USE_EVENT_DRIVEN:
    # Event-driven path
    event_engine.register(EventType.ORDER_UPDATE, on_order_update)
else:
    # REST polling path (fallback)
    poll_order_status()
```

### Rollback Plan

**If Event-Driven Fails:**

1. **Immediate** (< 5 minutes):
   - Set `USE_EVENT_DRIVEN=false` in environment
   - Restart application
   - Revert to REST polling

2. **Short-term** (< 1 hour):
   - Investigate root cause
   - Fix issues
   - Re-enable for subset of users (10%)

3. **Long-term** (< 1 day):
   - Gradual rollout with monitoring
   - 10% → 25% → 50% → 100%

### Monitoring

**Key Metrics:**

1. **Event Engine Health:**
   - Queue size (alert if > 1000)
   - Event processing latency (alert if > 100ms)
   - Handler error rate (alert if > 1%)

2. **WebSocket Health:**
   - Connection status (alert if disconnected > 10 seconds)
   - Message rate (alert if 0 messages for 60 seconds)
   - Reconnection attempts (alert if > 5 attempts)

3. **Order Update Latency:**
   - Time from order placed to event received
   - Target: <100ms
   - Alert if > 500ms

---

## Success Metrics

### Phase 0 Completion Criteria

**Week 1 (Event Engine + Jainam):**

- ✅ Event engine operational
  - [ ] Event queue processing events
  - [ ] Timer events firing every 1 second
  - [ ] Handlers registered and receiving events
  - [ ] No memory leaks (run for 24 hours)

- ✅ Jainam using event-driven updates
  - [ ] WebSocket/postback connected
  - [ ] Order updates received in <100ms
  - [ ] Position updates received in <100ms
  - [ ] Zero REST API calls for order status

**Week 2 (Zerodha - Optional):**

- ✅ Zerodha using event-driven updates
  - [ ] Postback endpoint operational
  - [ ] Order updates received in <100ms
  - [ ] Integration with existing market data WebSocket

### Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Order update latency** | <100ms | Time from broker update to UI |
| **Event processing latency** | <10ms | Time from queue to handler |
| **WebSocket uptime** | >99.9% | Connection uptime over 24 hours |
| **API call reduction** | 100% | Zero REST calls for order status |

### User Acceptance Criteria

- ✅ Real-time order updates in UI (no manual refresh)
- ✅ Instant notifications for order fills/rejections
- ✅ Automated stop-loss adjustments working
- ✅ No degradation in existing functionality
- ✅ Positive user feedback (>90% satisfaction)

---

## Next Steps

**After Phase 0 Completion:**

1. **Phase 1 (Week 3-4)**: IB Integration
   - Adapt Vn.py's IB gateway
   - Use same event engine
   - Leverage event-driven architecture

2. **Phase 2 (Week 5-6)**: Alpaca Integration
   - Build from scratch
   - Use same event engine
   - WebSocket for order updates

3. **Future Phases**: Migrate remaining Indian brokers
   - Angel One, Upstox, Dhan, Fyers, 5Paisa, Shoonya
   - Same event-driven pattern
   - Estimated 1-2 days per broker

---

## References

1. **Vn.py EventEngine**: `/tmp/vnpy/vnpy/event/engine.py`
2. **Vn.py BaseGateway**: `/tmp/vnpy/vnpy/trader/gateway.py`
3. **OpenAlgo WebSocket**: `/Users/maruth/projects/openalgo/docs/websocket.md`
4. **IB Integration Plan**: `ib_vnpy_adaptation_plan.md` (this repository)

---

**Document End**

