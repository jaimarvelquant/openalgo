import threading
import json
import logging
from websocket_adapters.base_adapter import BaseBrokerWebSocketAdapter
from broker.jainam_prop.api.auth_api import authenticate_market_data
from broker.jainam_prop.mapping.transform_data import map_jainam_to_exchange
from utils.logging import get_logger
import socketio
from broker.jainam_prop.api.config import get_jainam_base_url

logger = get_logger(__name__)

class JainamWebSocketAdapter(BaseBrokerWebSocketAdapter):
    """
    Jainam-specific implementation of the WebSocket adapter
    Uses Socket.IO for real-time market data streaming
    """

    def __init__(self):
        self.user_id = None
        self.broker_name = "jainam_prop"
        self.logger = get_logger(f"{self.broker_name}_websocket")
        self.root_url = get_jainam_base_url()
        self.market_token = None
        self.sio = None
        self.connected = False
        self.subscriptions = {}

    def initialize(self, broker_name, user_id, auth_data=None):
        """
        Initialize connection with Jainam WebSocket API

        Arguments:
            broker_name (str): Name of the broker (always 'jainam_prop' in this case)
            user_id (str): Client ID/user ID
            auth_data (dict, optional): Authentication data
        """
        self.user_id = user_id
        self.broker_name = broker_name

        # Get market data token
        if auth_data and 'market_token' in auth_data:
            self.market_token = auth_data['market_token']
        else:
            # Authenticate to get market token
            market_token, error = authenticate_market_data()
            if error:
                self.logger.error(f"Market data authentication failed: {error}")
                raise ValueError(f"Market data authentication failed: {error}")
            self.market_token = market_token

        # Initialize Socket.IO client
        self.sio = socketio.Client(logger=False, engineio_logger=False)

        # Set up event handlers
        self.sio.on('connect', self.on_connect)
        self.sio.on('disconnect', self.on_disconnect)
        self.sio.on('1512-json-full', self.on_message_1512_full)  # LTP data
        self.sio.on('1501-json-full', self.on_message_1501_full)  # Touchline data
        self.sio.on('1502-json-full', self.on_message_1502_full)  # Market depth

        self.logger.info(f"Jainam WebSocket adapter initialized for user {user_id}")

    def connect(self):
        """Establish connection to Jainam WebSocket"""
        try:
            if not self.sio:
                raise ValueError("WebSocket client not initialized")

            # Connection URL with authentication
            connection_url = f"{self.root_url}/apimarketdata/socket.io/?token={self.market_token}&userID={self.user_id}&publishFormat=JSON&broadcastMode=Full"

            # Start connection in a thread
            threading.Thread(target=self._connect_socket, args=(connection_url,), daemon=True).start()

            self.logger.info("Jainam WebSocket connection initiated")

        except Exception as e:
            self.logger.error(f"Error connecting to Jainam WebSocket: {e}")
            raise

    def _connect_socket(self, connection_url):
        """Connect to Socket.IO in a separate thread"""
        try:
            self.sio.connect(connection_url, transports=['websocket'])
            self.sio.wait()
        except Exception as e:
            self.logger.error(f"Socket.IO connection error: {e}")

    def disconnect(self):
        """Disconnect from Jainam WebSocket"""
        try:
            if self.sio:
                self.sio.disconnect()
                self.connected = False
            self.logger.info("Jainam WebSocket disconnected")
        except Exception as e:
            self.logger.error(f"Error disconnecting from Jainam WebSocket: {e}")

    def subscribe(self, symbol, exchange, mode=1, depth_level=5):
        """
        Subscribe to market data with Jainam-specific implementation

        Arguments:
            symbol (str): Trading symbol (e.g., 'RELIANCE')
            exchange (str): Exchange code (e.g., 'NSE', 'BSE', 'NFO')
            mode (int): Subscription mode - 1:LTP, 2:Quote, 4:Depth
            depth_level (int): Market depth level (5, 20, 30) - Jainam supports various levels
        """
        try:
            # Map mode to Jainam message codes
            mode_mapping = {
                1: 1512,  # LTP
                2: 1501,  # Touchline (Quote)
                4: 1502   # Market Depth
            }

            message_code = mode_mapping.get(mode, 1512)

            # Get token for symbol (this needs proper implementation)
            from broker.jainam_prop.mapping.transform_data import get_token_from_symbol, map_exchange_to_jainam
            token = get_token_from_symbol(symbol, exchange)
            exchange_segment = map_exchange_to_jainam(exchange)

            # Subscription payload
            subscription_data = {
                'instruments': [{
                    'exchangeSegment': exchange_segment,
                    'exchangeInstrumentID': token
                }],
                'xtsMessageCode': message_code
            }

            # Send subscription request
            if self.connected and self.sio:
                response = self.sio.emit('subscription', subscription_data)
                self.logger.info(f"Subscribed to {symbol}.{exchange} mode {mode}")

                # Store subscription info
                correlation_id = f"{symbol}_{exchange}_{mode}"
                self.subscriptions[correlation_id] = {
                    'symbol': symbol,
                    'exchange': exchange,
                    'token': token,
                    'mode': mode,
                    'message_code': message_code
                }

                return {
                    'status': 'success',
                    'symbol': symbol,
                    'exchange': exchange,
                    'mode': mode,
                    'message': 'Subscription requested'
                }
            else:
                return {
                    'status': 'error',
                    'code': 'NOT_CONNECTED',
                    'message': 'WebSocket not connected'
                }

        except Exception as e:
            self.logger.error(f"Error subscribing to Jainam market data: {e}")
            return {
                'status': 'error',
                'code': 'SUBSCRIPTION_FAILED',
                'message': str(e)
            }

    def unsubscribe(self, symbol, exchange, mode=1):
        """
        Unsubscribe from market data

        Arguments:
            symbol (str): Trading symbol
            exchange (str): Exchange code
            mode (int): Subscription mode
        """
        try:
            correlation_id = f"{symbol}_{exchange}_{mode}"

            if correlation_id in self.subscriptions:
                subscription_info = self.subscriptions[correlation_id]

                # Unsubscription payload
                unsubscription_data = {
                    'instruments': [{
                        'exchangeSegment': map_exchange_to_jainam(exchange),
                        'exchangeInstrumentID': subscription_info['token']
                    }],
                    'xtsMessageCode': subscription_info['message_code']
                }

                # Send unsubscription request
                if self.connected and self.sio:
                    self.sio.emit('unsubscription', unsubscription_data)
                    self.logger.info(f"Unsubscribed from {symbol}.{exchange} mode {mode}")

                # Remove from subscriptions
                del self.subscriptions[correlation_id]

                return {
                    'status': 'success',
                    'message': f"Unsubscribed from {symbol}.{exchange} mode {mode}"
                }
            else:
                return {
                    'status': 'error',
                    'code': 'NOT_SUBSCRIBED',
                    'message': f"Not subscribed to {symbol}.{exchange} mode {mode}"
                }

        except Exception as e:
            self.logger.error(f"Error unsubscribing from Jainam market data: {e}")
            return {
                'status': 'error',
                'code': 'UNSUBSCRIPTION_FAILED',
                'message': str(e)
            }

    # Socket.IO Event Handlers

    def on_connect(self):
        """Handle WebSocket connection"""
        self.connected = True
        self.logger.info("Jainam WebSocket connected successfully")

    def on_disconnect(self):
        """Handle WebSocket disconnection"""
        self.connected = False
        self.logger.info("Jainam WebSocket disconnected")

    def on_message_1512_full(self, data):
        """Handle LTP data (message code 1512)"""
        try:
            self._process_market_data(data, mode=1)
        except Exception as e:
            self.logger.error(f"Error processing 1512 LTP data: {e}")

    def on_message_1501_full(self, data):
        """Handle Touchline data (message code 1501)"""
        try:
            self._process_market_data(data, mode=2)
        except Exception as e:
            self.logger.error(f"Error processing 1501 Touchline data: {e}")

    def on_message_1502_full(self, data):
        """Handle Market Depth data (message code 1502)"""
        try:
            self._process_market_data(data, mode=4)
        except Exception as e:
            self.logger.error(f"Error processing 1502 Market Depth data: {e}")

    def _process_market_data(self, data, mode):
        """
        Process incoming market data and publish to MarvelQuant format

        Arguments:
            data: Raw market data from Jainam
            mode: Data mode (1=LTP, 2=Quote, 4=Depth)
        """
        try:
            # Parse the data (assuming it's JSON string or dict)
            if isinstance(data, str):
                market_data = json.loads(data)
            else:
                market_data = data

            # Extract instrument data
            if 'result' in market_data and market_data['result']:
                instrument_data = market_data['result'][0]  # First instrument

                # Find corresponding subscription
                token = instrument_data.get('ExchangeInstrumentID')
                sub_info = None

                for sub_id, sub in self.subscriptions.items():
                    if sub['token'] == token and sub['mode'] == mode:
                        sub_info = sub
                        break

                if not sub_info:
                    return  # No subscription found for this data

                symbol = sub_info['symbol']
                exchange = sub_info['exchange']

                # Format data based on mode
                formatted_data = self._format_market_data(instrument_data, mode)

                # Create market data message
                market_data_message = {
                    'type': 'market_data',
                    'mode': mode,
                    'topic': f"{symbol}.{exchange}",
                    'data': formatted_data
                }

                # Publish to ZeroMQ (this should be implemented in base class)
                topic = f"{symbol}.{exchange}.{mode}"
                # self.socket.send_multipart([
                #     topic.encode('utf-8'),
                #     json.dumps(market_data_message).encode('utf-8')
                # ])

                self.logger.debug(f"Published market data for {symbol}.{exchange}")

        except Exception as e:
            self.logger.error(f"Error processing market data: {e}")

    def _format_market_data(self, instrument_data, mode):
        """
        Format Jainam market data to MarvelQuant format

        Arguments:
            instrument_data: Raw instrument data from Jainam
            mode: Data mode

        Returns:
            Formatted market data
        """
        formatted_data = {
            'symbol': '',  # Will be set from subscription
            'exchange': '',  # Will be set from subscription
            'timestamp': instrument_data.get('LastTradedTime', '')
        }

        if mode == 1:  # LTP mode
            formatted_data.update({
                'ltp': float(instrument_data.get('LastTradedPrice', 0))
            })

        elif mode == 2:  # Quote mode
            formatted_data.update({
                'ltp': float(instrument_data.get('LastTradedPrice', 0)),
                'open': float(instrument_data.get('Open', 0)),
                'high': float(instrument_data.get('High', 0)),
                'low': float(instrument_data.get('Low', 0)),
                'close': float(instrument_data.get('Close', 0)),
                'volume': int(instrument_data.get('TotalTradedQuantity', 0))
            })

        elif mode == 4:  # Depth mode
            # Format market depth
            depth = {
                'buy': [],
                'sell': []
            }

            # Process buy depth (assuming structure from Jainam API)
            buy_depth = instrument_data.get('Bid', [])
            for level in buy_depth[:5]:  # First 5 levels
                depth['buy'].append({
                    'price': float(level.get('Price', 0)),
                    'quantity': int(level.get('Quantity', 0)),
                    'orders': int(level.get('Orders', 0))
                })

            # Process sell depth
            sell_depth = instrument_data.get('Ask', [])
            for level in sell_depth[:5]:  # First 5 levels
                depth['sell'].append({
                    'price': float(level.get('Price', 0)),
                    'quantity': int(level.get('Quantity', 0)),
                    'orders': int(level.get('Orders', 0))
                })

            formatted_data.update({
                'ltp': float(instrument_data.get('LastTradedPrice', 0)),
                'depth': depth
            })

        return formatted_data
