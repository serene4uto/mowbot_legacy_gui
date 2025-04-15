# map_view.py
import os
import json
import pathlib
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from app.utils.logger import logger

class JsPyBridge(QObject):
    """
    Bridge for Python–JavaScript communication.
    Provides signals for GPS update, heading update, marker addition, and marker removal.
    """
    signal_tracker_gps_updated = pyqtSignal(str)
    signal_tracker_heading_updated = pyqtSignal(str)
    signal_marks_gps_added = pyqtSignal(str)
    signal_marks_gps_removed = pyqtSignal(str)
    
    @pyqtSlot(str)
    def receive_from_js(self, message):
        logger.debug(f"Received from JS: {message}")

class MapView(QWidget):
    """
    MapView loads an external HTML template to display a Leaflet map.
    The template includes a placeholder '{bingApiKey}' which is replaced at runtime.
    It exposes API methods to update the GPS position, heading, and manage markers.
    """
    def __init__(self, config):
        """
        :param config: A dictionary containing configuration, including "bing_api_key".
        """
        super().__init__()
        self._config = config
        self._init_ui()
        
        # Setup Python-JavaScript bridge and channel.
        self.jspy_bridge = JsPyBridge()
        self.channel = QWebChannel()
        self.channel.registerObject("jspy_bridge", self.jspy_bridge)
        self.web_view.page().setWebChannel(self.channel)
        
        self._load_map()
        
    def _init_ui(self):
        layout = QVBoxLayout()
        self.web_view = QWebEngineView()
        layout.addWidget(self.web_view)
        self.setLayout(layout)
        
    def _load_map(self):
        """
        Loads the external HTML template, replaces the Bing API key placeholder, and sets the HTML.
        """
        # Compute the path to the HTML template file.
        template_path = os.path.join(pathlib.Path(__file__).parent.parent.parent.resolve(), 
                    "resources", "templates", "map_template.html")
        try:
            with open(template_path, "r", encoding="utf-8") as file:
                html = file.read()
        except Exception as e:
            logger.error("Failed to load map template: " + str(e))
            html = ""
        
        # Replace the placeholder with the actual Bing API key.
        bing_api_key = self._config["bing_api_key"]
        html = html.replace("{bingApiKey}", bing_api_key)
        
        self.web_view.setHtml(html)
        
    # --- View API Methods ---
    
    def update_gps_position(self, latitude, longitude):
        """Update the GPS position on the map."""
        payload = json.dumps({
            'latitude': latitude,
            'longitude': longitude,
        })
        self.jspy_bridge.signal_tracker_gps_updated.emit(payload)
        
    def update_heading(self, heading):
        """Update the heading on the map."""
        payload = json.dumps({'heading': heading})
        self.jspy_bridge.signal_tracker_heading_updated.emit(payload)
        
    def add_gps_position_mark(self, latitude, longitude):
        """Add a marker on the map at the given GPS position."""
        payload = json.dumps({
            'latitude': latitude,
            'longitude': longitude,
        })
        self.jspy_bridge.signal_marks_gps_added.emit(payload)
        logger.debug("Sent request to add GPS position mark")
        
    def remove_gps_position_mark(self, latitude, longitude):
        """Remove the marker on the map that matches the given GPS position."""
        payload = json.dumps({
            'latitude': latitude,
            'longitude': longitude,
        })
        self.jspy_bridge.signal_marks_gps_removed.emit(payload)
        logger.debug("Sent request to remove GPS position mark")
        
    def reset(self):
        """Reset the map by clearing all markers."""
        self.web_view.page().runJavaScript("clearMarkers();")
        logger.debug("Map view reset")
