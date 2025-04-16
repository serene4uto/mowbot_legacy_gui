# foxglove_ws_model.py
import asyncio
import websockets
import json
import struct
from typing import Dict, Any, Optional


from PyQt5.QtCore import pyqtSignal, QThread, QObject
from app.utils.logger import logger  # Ensure this is a configured logger
from app.utils.cdr_decoder import decode_imu, decode_navsatfix, decode_sensorstatus

class FoxgloveWsModel(QObject):
    """
    Model class for handling WebSocket communication with the Foxglove server.
    This singleton Model maintains the connection, handles message decoding,
    and emits signals with data updates that can be consumed by the Controller.
    """
    
    # Topics to subscribe to
    SUBCRIBE_TOPICS = [
        "/gps/heading",
        "/gps/fix",
        "/sensor_status",
        "/gps/fix_filtered"
    ]
    
    # Singleton instance
    _instance = None

    # PyQt signals for data updates
    signal_heading_quat = pyqtSignal(dict)
    signal_gps_fix = pyqtSignal(dict)
    signal_health_status = pyqtSignal(dict)
    
    @staticmethod
    def get_instance(config: Dict[str, Any]) -> 'FoxgloveWsModel':
        """
        Returns the singleton instance of FoxgloveWsModel.
        """
        if FoxgloveWsModel._instance is None:
            FoxgloveWsModel._instance = FoxgloveWsModel(config)
        return FoxgloveWsModel._instance

    def __init__(
            self, 
            config: Dict[str, Any]
        ):
        """
        Initializes the FoxgloveWsModel.

        Args:
            config (Dict[str, Any]): Configuration dictionary containing
                'foxglove_ws_uri', 'foxglove_ws_subprotocol', and other optional parameters.
        """
        if FoxgloveWsModel._instance is not None:
            raise Exception("This class is a singleton! Use `get_instance` instead.")
        super().__init__()
        self._config = config
        self._running = False
        self.ws: Optional[websockets.WebSocketClientProtocol] = None
        self.max_retries = config.get('max_retries', 5)
        self.backoff_factor = config.get('backoff_factor', 2)
        self.current_retries = 0
        self.should_reconnect = True
        self.loop: Optional[asyncio.AbstractEventLoop] = None  # Reference to the event loop

        self.ws_subs: Dict[int, Dict[str, Any]] = {}  # Store WebSocket subscription info

        # Setup QThread for asynchronous WebSocket handling.
        self.thread = QThread()
        self.moveToThread(self.thread)
        self.thread.started.connect(self._run_websocket)

        logger.info("FoxgloveWsModel instance created. Call start() to begin WebSocket communication.")

    def start(self) -> None:
        """
        Starts the Model’s QThread for handling WebSocket communication.
        """
        if not self.thread.isRunning():
            self._running = True
            self.should_reconnect = True
            self.current_retries = 0
            self.ws_subs = {}  # Reset subscriptions
            self.thread.start()
            logger.info("FoxgloveWsModel thread started.")
        else:
            logger.warning("FoxgloveWsModel thread is already running.")

    def stop(self) -> None:
        """
        Stops the WebSocket Model and its associated thread gracefully.
        """
        self._running = False
        self.should_reconnect = False
        if self.ws and self.loop and not self.loop.is_closed():
            # Schedule the disconnect coroutine on the event loop.
            future = asyncio.run_coroutine_threadsafe(self._ws_disconnect(), self.loop)
            try:
                future.result(timeout=1)
            except asyncio.TimeoutError:
                logger.warning("Disconnect coroutine timed out.")
            except Exception as e:
                logger.error(f"Error during disconnect: {e}")
        else:
            logger.warning("Event loop is closed or not available.")
        self.thread.quit()
        self.thread.wait()
        logger.info("FoxgloveWsModel thread stopped.")
        self.loop = None
        self.ws = None

    def _run_websocket(self) -> None:
        """
        Initializes and runs the asyncio event loop for WebSocket communication within the QThread.
        """
        loop = asyncio.new_event_loop()
        self.loop = loop
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self._ws_connect())
        except Exception as e:
            logger.error(f"Error in _run_websocket: {e}")
        finally:
            loop.close()

    async def _ws_connect(self) -> None:
        """
        Connects to the WebSocket server with reconnection logic.
        """
        while self.should_reconnect and self.current_retries < self.max_retries:
            try:
                self.ws = await websockets.connect(
                    self._config['foxglove_ws_uri'],
                    subprotocols=[self._config['foxglove_ws_subprotocol']],
                )
                logger.info(f"Connected to Foxglove WebSocket server at {self._config['foxglove_ws_uri']}")
                self.current_retries = 0  # Reset retry counter upon successful connection

                # Begin listening for messages
                await self._listen()
            except Exception as e:
                logger.error(f"Error during WebSocket connection: {e}")
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
            message (Any): The incoming message.
        """
        try:
            if isinstance(message, bytes):
                self._handle_binary_message(message)
            else:
                parsed_message = json.loads(message)
                logger.info(f"Received JSON message: {parsed_message}")

                op = parsed_message.get("op")
                if op:
                    await self._trigger_op_event(op, parsed_message)
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
        except Exception as e:
            logger.error(f"Error processing message: {e}")

    async def _trigger_op_event(self, op: str, message: Dict[str, Any]) -> None:
        """
        Triggers events based on the operation type within the message.

        Args:
            op (str): The operation type.
            message (Dict[str, Any]): The JSON message.
        """
        if op == "advertise":
            await self._handle_advertised_channels(message)
        elif op == "message":
            # Process other operation types as needed
            pass

    def _handle_binary_message(self, message: bytes) -> None:
        """
        Decodes and processes binary messages.

        Args:
            message (bytes): The binary message received.
        """
        try:
            if len(message) < 13:
                logger.warning("Received binary message is too short.")
                return
            
            # Decode opcode, subscriptionId, and timestamp from the binary message.
            opcode = message[0]
            subscription_id = struct.unpack('<I', message[1:5])[0]
            timestamp = struct.unpack('<Q', message[5:13])[0]
            payload = message[13:]

            if opcode != 0x01:
                logger.warning(f"Unexpected opcode: {opcode}")
                return

            # Process message based on subscription topic.
            topic = self.ws_subs.get(subscription_id, {}).get('topic')
            if topic == '/gps/heading':
                imu_data = decode_imu(payload)
                if imu_data is None:
                    return
                heading_quat = imu_data.get('orientation', {})
                self.signal_heading_quat.emit(heading_quat)
            elif topic == '/gps/fix':
                navsatfix_data = decode_navsatfix(payload)
                if navsatfix_data is None:
                    return
                # Optionally process navsatfix_data...
            elif topic == '/gps/fix_filtered':
                navsatfix_data = decode_navsatfix(payload)
                if navsatfix_data is None:
                    return
                gps_fix = {
                    'latitude': navsatfix_data.get('latitude', 0),
                    'longitude': navsatfix_data.get('longitude', 0),
                    'altitude': navsatfix_data.get('altitude', 0),
                }
                self.signal_gps_fix.emit(gps_fix)
                # logger.info(f"Navsatfix Data: {navsatfix_data}")
            elif topic == '/sensor_status':
                sensorstatus_data = decode_sensorstatus(payload)
                self.signal_health_status.emit(sensorstatus_data)
                # logger.info(f"Sensor Status Data: {sensorstatus_data}")
        except struct.error as e:
            logger.error(f"Error decoding binary message: {e}")
        except Exception as e:
            logger.error(f"Unexpected error processing binary message: {e}")

    async def _handle_advertised_channels(self, message: Dict[str, Any]) -> None:
        """
        Processes channel advertisement messages by subscribing to desired channels.

        Args:
            message (Dict[str, Any]): The JSON message advertising channels.
        """
        channels = message.get("channels", [])
        for channel in channels:
            channel_id = channel.get("id")
            topic = channel.get("topic")
            if topic in self.SUBCRIBE_TOPICS:
                logger.info(f"Subscribing to channel: {channel_id} with topic: {topic}")
                subscription_id = channel_id  # Use the channel's id as the subscription id.
                self.ws_subs[subscription_id] = channel
                await self._send({
                    "op": "subscribe",
                    "subscriptions": [
                        {"id": subscription_id, "channelId": channel_id}
                    ]
                })
                logger.info(f"Subscribed to channel: {channel_id} with subscription ID: {subscription_id}")

    async def _send(self, message: Dict[str, Any]) -> None:
        """
        Sends a JSON message to the WebSocket server.

        Args:
            message (Dict[str, Any]): The message to be sent.
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
        Gracefully disconnects from the WebSocket server and stops the event loop.
        """
        try:
            if self.ws:
                await self.ws.close()
                logger.info("Disconnected from Foxglove WebSocket server")
            if self.loop and self.loop.is_running():
                self.loop.call_soon_threadsafe(self.loop.stop)
            logger.info("WebSocket connection closed.")
        except Exception as e:
            logger.error(f"Error during disconnect: {e}")

    async def send_message(self, message: Dict[str, Any]) -> None:
        """
        Public method to send a message to the WebSocket server.

        Args:
            message (Dict[str, Any]): The message dictionary to send.
        """
        await self._send(message)
        
    def is_running(self) -> bool:
        """
        Returns whether the WebSocket Model is currently running.
        
        Returns:
            bool: True if the Model is running, False otherwise.
        """
        return self._running
