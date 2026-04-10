"""
Constants used throughout the application.
Reference: https://docs.openalgo.in/api-documentation/v1/order-constants
"""

# Exchange Types
EXCHANGE_NSE = "NSE"
EXCHANGE_NFO = "NFO"
EXCHANGE_CDS = "CDS"
EXCHANGE_BSE = "BSE"
EXCHANGE_BFO = "BFO"
EXCHANGE_BCD = "BCD"
EXCHANGE_MCX = "MCX"
EXCHANGE_NCDEX = "NCDEX"
EXCHANGE_NSE_INDEX = "NSE_INDEX"
EXCHANGE_BSE_INDEX = "BSE_INDEX"
EXCHANGE_IBKR = "IBKR"
EXCHANGE_IDEALPRO = "IDEALPRO"
EXCHANGE_NYMEX = "NYMEX"
EXCHANGE_GLOBEX = "GLOBEX"

VALID_EXCHANGES = [
    EXCHANGE_NSE, EXCHANGE_NFO, EXCHANGE_CDS, EXCHANGE_BSE, EXCHANGE_BFO, 
    EXCHANGE_BCD, EXCHANGE_MCX, EXCHANGE_NCDEX, EXCHANGE_NSE_INDEX, 
    EXCHANGE_BSE_INDEX, EXCHANGE_IBKR, EXCHANGE_IDEALPRO, EXCHANGE_NYMEX, EXCHANGE_GLOBEX
]

# Product Types
PRODUCT_CNC = "CNC"
PRODUCT_NRML = "NRML"
PRODUCT_MIS = "MIS"
VALID_PRODUCT_TYPES = [PRODUCT_CNC, PRODUCT_NRML, PRODUCT_MIS]

# Price Types
PRICE_TYPE_MARKET = "MARKET"
PRICE_TYPE_LIMIT = "LIMIT"
PRICE_TYPE_STP = "STP" 
PRICE_TYPE_SL = "SL"
PRICE_TYPE_SLM = "SL-M"
VALID_PRICE_TYPES = [PRICE_TYPE_MARKET, PRICE_TYPE_LIMIT, PRICE_TYPE_STP, PRICE_TYPE_SL, PRICE_TYPE_SLM]

# Order Actions
ACTION_BUY = "BUY"
ACTION_SELL = "SELL"
VALID_ACTIONS = [ACTION_BUY, ACTION_SELL]

# Exchange Badge Colors (for UI)
EXCHANGE_BADGE_COLORS = {
    EXCHANGE_NSE: "badge-accent",
    EXCHANGE_NFO: "badge-secondary",
    EXCHANGE_CDS: "badge-info",
    EXCHANGE_BSE: "badge-neutral",
    EXCHANGE_BFO: "badge-warning",
    EXCHANGE_BCD: "badge-error",
    EXCHANGE_MCX: "badge-primary",
    EXCHANGE_NCDEX: "badge-success",
    EXCHANGE_NSE_INDEX: "badge-accent",
    EXCHANGE_BSE_INDEX: "badge-neutral",
}

# Required Fields for Order Placement
REQUIRED_ORDER_FIELDS = ["apikey", "strategy", "symbol", "exchange", "action", "quantity"]

# Required Fields for Smart Order Placement
REQUIRED_SMART_ORDER_FIELDS = [
    "apikey",
    "strategy",
    "symbol",
    "exchange",
    "action",
    "quantity",
    "position_size",
]

# Required Fields for Cancel Order
REQUIRED_CANCEL_ORDER_FIELDS = ["apikey", "strategy", "orderid"]

# Required Fields for Cancel All Orders
REQUIRED_CANCEL_ALL_ORDER_FIELDS = ["apikey", "strategy"]

# Required Fields for Close Position
REQUIRED_CLOSE_POSITION_FIELDS = ["apikey", "strategy"]

# Required Fields for Modify Order
REQUIRED_MODIFY_ORDER_FIELDS = [
    "apikey",
    "strategy",
    "symbol",
    "action",
    "exchange",
    "orderid",
    "product",
    "pricetype",
    "price",
    "quantity",
    "disclosed_quantity",
    "trigger_price",
]

# Default Values for Optional Fields
DEFAULT_PRODUCT_TYPE = PRODUCT_MIS
DEFAULT_PRICE_TYPE = PRICE_TYPE_MARKET
DEFAULT_PRICE = "0"
DEFAULT_TRIGGER_PRICE = "0"
DEFAULT_DISCLOSED_QUANTITY = "0"
