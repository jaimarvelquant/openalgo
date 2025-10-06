"""
Jainam WebSocket client implementation
Uses Socket.IO for real-time market data streaming
"""

import socketio
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class JainamWebSocketClient:
    """
    Jainam WebSocket client using Socket.IO
    """

    def __init__(self, market_token, user_id, root_url="http://ctrade.jainam.in:3000"):
        self.market_token = market_token
        self.user_id = user_id
        self.root_url = root_url
        self.sio = None
        self.connected = False

        # Event handlers
        self.on_connect_callback = None
        self.on_disconnect_callback = None
        self.on_message_callback = None
        self.on_error_callback = None

    def connect(self, on_connect=None, on_message=None, on_disconnect=None, on_error=None):
        """
        Connect to Jainam WebSocket

        Args:
            on_connect: Connection callback
            on_message: Message callback
            on_disconnect: Disconnect callback
            on_error: Error callback
        """
        self.on_connect_callback = on_connect
        self.on_disconnect_callback = on_disconnect
        self.on_message_callback = on_message
        self.on_error_callback = on_error

        # Initialize Socket.IO client
        self.sio = socketio.Client(logger=False, engineio_logger=False)

        # Set up event handlers
        self.sio.on('connect', self._on_connect)
        self.sio.on('disconnect', self._on_disconnect)
        self.sio.on('error', self._on_error)

        # Market data message handlers
        self.sio.on('1512-json-full', self._on_message_1512)  # LTP
        self.sio.on('1501-json-full', self._on_message_1501)  # Touchline
        self.sio.on('1502-json-full', self._on_message_1502)  # Market Depth

        # Connection URL
        connection_url = f"{self.root_url}/apimarketdata/socket.io/?token={self.market_token}&userID={self.user_id}&publishFormat=JSON&broadcastMode=Full"

        try:
            logger.info("Connecting to Jainam WebSocket...")
            self.sio.connect(connection_url, transports=['websocket'])
            self.connected = True
        except Exception as e:
            logger.error(f"Failed to connect to Jainam WebSocket: {e}")
            if self.on_error_callback:
                self.on_error_callback(str(e))

    def disconnect(self):
        """Disconnect from WebSocket"""
        try:
            if self.sio:
                self.sio.disconnect()
                self.connected = False
                logger.info("Jainam WebSocket disconnected")
        except Exception as e:
            logger.error(f"Error disconnecting from Jainam WebSocket: {e}")

    def subscribe(self, instruments, message_code):
        """
        Subscribe to market data

        Args:
            instruments: List of instruments to subscribe
            message_code: Message code (1512=LTP, 1501=Touchline, 1502=Depth)
        """
        if not self.connected:
            logger.error("WebSocket not connected")
            return

        subscription_data = {
            'instruments': instruments,
            'xtsMessageCode': message_code
        }

        try:
            self.sio.emit('subscription', subscription_data)
            logger.info(f"Subscribed to instruments with message code {message_code}")
        except Exception as e:
            logger.error(f"Subscription failed: {e}")

    def unsubscribe(self, instruments, message_code):
        """
        Unsubscribe from market data

        Args:
            instruments: List of instruments to unsubscribe
            message_code: Message code
        """
        if not self.connected:
            logger.error("WebSocket not connected")
            return

        unsubscription_data = {
            'instruments': instruments,
            'xtsMessageCode': message_code
        }

        try:
            self.sio.emit('unsubscription', unsubscription_data)
            logger.info(f"Unsubscribed from instruments with message code {message_code}")
        except Exception as e:
            logger.error(f"Unsubscription failed: {e}")

    def wait(self):
        """Wait for WebSocket connection (blocking)"""
        if self.sio:
            self.sio.wait()

    # Event handler implementations

    def _on_connect(self):
        """Handle connection event"""
        self.connected = True
        logger.info("Jainam WebSocket connected successfully")
        if self.on_connect_callback:
            self.on_connect_callback()

    def _on_disconnect(self):
        """Handle disconnection event"""
        self.connected = False
        logger.info("Jainam WebSocket disconnected")
        if self.on_disconnect_callback:
            self.on_disconnect_callback()

    def _on_error(self, error):
        """Handle error event"""
        logger.error(f"Jainam WebSocket error: {error}")
        if self.on_error_callback:
            self.on_error_callback(error)

    def _on_message_1512(self, data):
        """Handle LTP data (1512)"""
        self._process_message(data, 1512)

    def _on_message_1501(self, data):
        """Handle Touchline data (1501)"""
        self._process_message(data, 1501)

    def _on_message_1502(self, data):
        """Handle Market Depth data (1502)"""
        self._process_message(data, 1502)

    def _process_message(self, data, message_code):
        """
        Process incoming message and call callback

        Args:
            data: Message data
            message_code: Message code identifier
        """
        try:
            # Parse data if it's a string
            if isinstance(data, str):
                parsed_data = json.loads(data)
            else:
                parsed_data = data

            # Add metadata
            enriched_data = {
                'message_code': message_code,
                'timestamp': datetime.now().isoformat(),
                'data': parsed_data
            }

            # Call message callback
            if self.on_message_callback:
                self.on_message_callback(enriched_data)

        except Exception as e:
            logger.error(f"Error processing message {message_code}: {e}")

    # Utility methods

    def is_connected(self):
        """Check if WebSocket is connected"""
        return self.connected

    def get_connection_status(self):
        """Get connection status information"""
        return {
            'connected': self.connected,
            'user_id': self.user_id,
            'root_url': self.root_url
        }
