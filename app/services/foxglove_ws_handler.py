import asyncio
import websockets
import json
import struct
import uuid
import logging
from typing import Callable, Dict, Any, List, Optional

from PyQt5.QtCore import pyqtSignal, QThread, QObject
from app.utils.logger import logger  # Ensure this is a configured logger

from app.utils.cdr_decoder import decode_imu, decode_navsatfix, decode_sensorstatus

class FoxgloveWsHandler(QObject):
    """
    Singleton class to handle WebSocket connections with the Foxglove server.
    Integrates with PyQt5 using signals to communicate events to the UI.
    """

    SUBCRIBE_TOPICS = [
        "/gps/heading",
        "/gps/fix",
        "/sensor_status",
        "/gps/fix_filtered"
    ]


    # Singleton instance
    _instance = None

    # PyQt signals
    heading_quat_signal = pyqtSignal(dict)
    gps_fix_signal = pyqtSignal(dict)
    sensor_status_signal = pyqtSignal(dict)

    @staticmethod
    def get_instance(config: Dict[str, Any]) -> 'FoxgloveWsHandler':
        """
        Returns the singleton instance of FoxgloveWsHandler.
        """
        if FoxgloveWsHandler._instance is None:
            FoxgloveWsHandler._instance = FoxgloveWsHandler(config)
        return FoxgloveWsHandler._instance

    def __init__(self, config: Dict[str, Any]):
        """
        Initializes the FoxgloveWsHandler.

        Args:
            config (Dict[str, Any]): Configuration dictionary containing
                'foxglove_ws_uri' and 'foxglove_ws_subprotocol'.
        """
        if FoxgloveWsHandler._instance is not None:
            raise Exception("This class is a singleton! Use `get_instance` instead.")
        super().__init__()
        self.config = config
        self._running = False
        self.ws: Optional[websockets.WebSocketClientProtocol] = None
        self.max_retries = config.get('max_retries', 5)
        self.backoff_factor = config.get('backoff_factor', 2)
        self.current_retries = 0
        self.should_reconnect = True
        self.loop: Optional[asyncio.AbstractEventLoop] = None  # Reference to the event loop

        self.ws_subs = {}  # Store WebSocket subscriptions

        # Setup QThread for WebSocket handling
        self.thread = QThread()
        self.moveToThread(self.thread)
        self.thread.started.connect(self._run_websocket)

        logger.info("FoxgloveWsHandler instance created. Call start() to begin WebSocket communication.")

    def start(self) -> None:
        """
        Starts the QThread for handling WebSocket communication.
        """
        if not self.thread.isRunning():
            self._running = True
            self.should_reconnect = True
            self.current_retries = 0
            self.ws_subs = {}  # Reset available channels
            self.thread.start()
            logger.info("FoxgloveWsHandler thread started.")
        else:
            logger.warning("FoxgloveWsHandler thread is already running.")

    def stop(self) -> None:
        """
        Stops the WebSocket handler and the associated thread gracefully.
        """
        self._running = False
        self.should_reconnect = False
        if self.ws and self.loop and not self.loop.is_closed():
            # Schedule the disconnect coroutine on the WebSocket thread's event loop
            future = asyncio.run_coroutine_threadsafe(self._ws_disconnect(), self.loop)
            try:
                future.result(timeout=1)  # Wait for the disconnect to complete with a timeout
            except asyncio.TimeoutError:
                logger.warning("Disconnect coroutine timed out.")
            except Exception as e:
                # TODO: Handle exceptions from the disconnect coroutine
                logger.error(f"Error during disconnect: {e}")
        else:
            logger.warning("Event loop is closed or not available.")
        self.thread.quit()
        self.thread.wait()
        logger.info("FoxgloveWsHandler thread stopped.")
        self.loop = None  # Reset the event loop
        self.ws = None  # Reset the WebSocket connection

    def _run_websocket(self) -> None:
        """
        Starts the asyncio event loop for WebSocket communication within the QThread.
        """
        # logger.info("Starting WebSocket connection...")
        loop = asyncio.new_event_loop()
        self.loop = loop
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self._ws_connect())
        except Exception as e:
            logger.error(f"Error in run_websocket: {e}")
        finally:
            loop.close()

    async def _ws_connect(self) -> None:
        """
        Establishes connection to the WebSocket server with reconnection logic.
        """
        while self.should_reconnect and self.current_retries < self.max_retries:
            try:
                # Establish WebSocket connection with the required subprotocol
                self.ws = await websockets.connect(
                    self.config['foxglove_ws_uri'],
                    subprotocols=[self.config['foxglove_ws_subprotocol']],
                )
                logger.info(f"Connected to Foxglove websocket server at {self.config['foxglove_ws_uri']}")

                # Reset retry counter upon successful connection
                self.current_retries = 0

                # Listen for incoming messages
                await self._listen()
            except Exception as e:
                logger.error(f"Error during connection: {e}")
                self.current_retries += 1
                if self.current_retries >= self.max_retries:
                    logger.error("Max retries reached. Could not connect to the server.")
                    break
                wait_time = self.backoff_factor ** self.current_retries
                logger.info(f"Retrying connection in {wait_time} seconds... ({self.current_retries}/{self.max_retries})")
                await asyncio.sleep(wait_time)

    async def _listen(self) -> None:
        """
        Listens for incoming messages from the WebSocket server.
        """
        try:
            async for message in self.ws:
                await self._handle_message(message)
        except websockets.exceptions.ConnectionClosed as e:
            logger.warning(f"Connection closed: {e}")
            if self.should_reconnect:
                await self._ws_connect()
        except Exception as e:
            logger.error(f"Unexpected error in listen: {e}")
            if self.should_reconnect:
                await self._ws_connect()

    async def _handle_message(self, message: Any) -> None:
        """
        Processes incoming messages, handling both JSON and binary data.

        Args:
            message (Any): The incoming message from the WebSocket.
        """
        try:
            if isinstance(message, bytes):
                # Handle binary message
                self._handle_binary_message(message)
            else:
                # Handle JSON message
                parsed_message = json.loads(message)
                logger.info(f"Received JSON message: {parsed_message}")

                # Trigger signals based on the "op" field
                op = parsed_message.get("op")
                if op:
                    await self._trigger_op_event(op, parsed_message)

        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
        except Exception as e:
            logger.error(f"Error processing message: {e}")

    async def _trigger_op_event(self, op: str, message: Dict[str, Any]) -> None:
        """
        Emits signals based on the operation type in the message.

        Args:
            op (str): The operation type.
            message (Dict[str, Any]): The parsed JSON message.
        """
        if op == "advertise":
            await self._handle_advertised_channels(message)
        elif op == "message":
            # Handle other operation types as needed
            pass
        # Add more operations if necessary

    def _handle_binary_message(self, message: bytes) -> None:
        """
        Decodes and processes binary messages.

        Format:
            - opcode (1 byte, unsigned int)
            - subscriptionId (4 bytes, unsigned int)
            - timestamp (8 bytes, unsigned long)
            - payload (remaining bytes)

        Args:
            message (bytes): The binary message received.
        """
        try:
            if len(message) < 13:
                logger.warning("Received binary message is too short.")
                return
            
            # logger.info(f"Received binary message: {message}")

            # Decode opcode, subscriptionId, and timestamp
            opcode = message[0]
            subscription_id = struct.unpack('<I', message[1:5])[0]
            timestamp = struct.unpack('<Q', message[5:13])[0]

            # Extract payload
            payload = message[13:]

            if opcode != 0x01:
                logger.warning(f"Unexpected opcode: {opcode}")
                return

            # logger.info(f"Streaming message received:")
            # logger.info(f"  Subscription ID: {subscription_id}")
            # logger.info(f"  Topic: {self.ws_subs.get(subscription_id, 'Unknown')}")
            # logger.info(f"  Timestamp: {timestamp}")
            # logger.info(f"  Payload (raw): {payload}")

            if self.ws_subs.get(subscription_id, {}).get('topic') == '/gps/heading':
                # logger.info(f" Payload: {payload}")
                imu_data = decode_imu(payload)
                if imu_data is None:
                    return
                heading_quat = imu_data.get('orientation', {})
                self.heading_quat_signal.emit(heading_quat)
                # logger.info(f"  IMU Data: {imu_data}")
                
            if self.ws_subs.get(subscription_id, {}).get('topic') == '/gps/fix':
                # logger.info(f" Payload: {payload}")
                navsatfix_data = decode_navsatfix(payload)
                if navsatfix_data is None:
                    return
                gps_fix = {
                    'latitude': navsatfix_data.get('latitude', 0),
                    'longitude': navsatfix_data.get('longitude', 0),
                    'altitude': navsatfix_data.get('altitude', 0),
                }
                # logger.info(f"  Navsatfix Data: {navsatfix_data}")
            
            if self.ws_subs.get(subscription_id, {}).get('topic') == '/gps/fix_filtered':
                # logger.info(f" Payload: {payload}")
                navsatfix_data = decode_navsatfix(payload)
                if navsatfix_data is None:
                    return
                gps_fix = {
                    'latitude': navsatfix_data.get('latitude', 0),
                    'longitude': navsatfix_data.get('longitude', 0),
                    'altitude': navsatfix_data.get('altitude', 0),
                }
                self.gps_fix_signal.emit(gps_fix)
                logger.info(f"  Navsatfix Data: {navsatfix_data}")
            
            if self.ws_subs.get(subscription_id, {}).get('topic') == '/sensor_status':
                sensorstatus_data = decode_sensorstatus(payload)
                self.sensor_status_signal.emit(sensorstatus_data)
                # logger.info(f"  Sensor Status Data: {sensorstatus_data}")
                
        except struct.error as e:
            logger.error(f"Error decoding binary message: {e}")
        except Exception as e:
            logger.error(f"Unexpected error processing binary message: {e}")

    async def _handle_advertised_channels(self, message: Dict[str, Any]) -> None:
        """
        Handles advertised channels by subscribing to them.

        Args:
            message (Dict[str, Any]): The parsed JSON message containing channel information.
        """
        channels = message.get("channels", [])
        for channel in channels:
            channel_id = channel.get("id")
            topic = channel.get("topic")
            
            if topic in self.SUBCRIBE_TOPICS:
                logger.info(f"Subscribing to channel: {channel_id} with topic: {topic}")
                # Generate a unique subscription ID 
                # subscription_id = int(uuid.uuid4().int & (1<<32)-1)
                subscription_id = channel_id
                self.ws_subs[subscription_id] = channel

                # Subscribe to the channel
                await self._send({
                    "op": "subscribe",
                    "subscriptions": [
                        {"id": subscription_id, "channelId": channel_id}
                    ]
                })

                logger.info(f"Subscribed to channel: {channel_id} with subscription ID: {subscription_id}")

    async def _send(self, message: Dict[str, Any]) -> None:
        """
        Sends a message to the WebSocket server.

        Args:
            message (Dict[str, Any]): The message to send.
        """
        try:
            if self.ws:
                await self.ws.send(json.dumps(message))
                logger.info(f"Sent message: {message}")
            else:
                logger.warning("WebSocket is not open. Cannot send message.")
        except Exception as e:
            logger.error(f"Error sending message: {e}")

    async def _ws_disconnect(self) -> None:
        """
        Closes the WebSocket connection gracefully and stops the event loop.
        """
        try:
            if self.ws:
                await self.ws.close()
                logger.info("Disconnected from Foxglove websocket server")
            if self.loop and self.loop.is_running():
                # Schedule loop.stop() to ensure the event loop can exit
                self.loop.call_soon_threadsafe(self.loop.stop)
            logger.info("WebSocket connection closed.")
        except Exception as e:
            logger.error(f"Error during disconnect: {e}")

    async def send_message(self, message: Dict[str, Any]) -> None:
        """
        Public method to send messages to the WebSocket server.

        Args:
            message (Dict[str, Any]): The message to send.
        """
        await self._send(message)