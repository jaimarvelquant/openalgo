from broker.deltaex.api.order_api import get_order_book, get_trade_book, get_positions, place_order

# This file acts as a bridge for the orderbook_service
def get_orders(auth_token):
    return get_order_book(auth_token)

def get_trades(auth_token):
    return get_trade_book(auth_token)

def get_net_positions(auth_token):
    return get_positions(auth_token)
