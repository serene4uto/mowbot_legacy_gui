from PyQt5.QtWebEngineWidgets import QWebEngineView

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
)

from PyQt5.QtCore import pyqtSignal, pyqtSlot

import folium
from folium.plugins import Realtime
import io



class MapView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Set up layout for the custom widget
        layout = QHBoxLayout(self)

        # Create a QWebEngineView to display the folium map
        self.webview = QWebEngineView(self)

        # Initialize map attributes
        self.default_location = [36.1141352, 128.4188682]
        self.zoom_start = 18
        self.map = folium.Map(location=self.default_location, zoom_start=self.zoom_start)
        # Store markers in a dictionary with a unique name as key
        self.markers = {}

        # Load the initial map
        self._reload_map()
        layout.addWidget(self.webview)

        map_opt_layout = QVBoxLayout()
        self.update_loc_btn = QPushButton('Update\nLocation')
        # smaller text
        self.update_loc_btn.setStyleSheet("font-size: 12px;")
        self.update_loc_btn.setFixedWidth(70)
        self.update_loc_btn.setFixedHeight(70)
        map_opt_layout.addWidget(self.update_loc_btn)
        map_opt_layout.setSpacing(10)
        map_opt_layout.addStretch(1)
        layout.addLayout(map_opt_layout)

        self.setLayout(layout)


    def _reload_map(self):
        """Helper to reload the map into the QWebEngineView."""
        data = io.BytesIO()
        self.map.save(data, close_file=False)
        self.webview.setHtml(data.getvalue().decode('utf-8'))

    def _regenerate_map(self):
        """Recreate the map and add all current markers with their colors."""
        self.map = folium.Map(location=self.default_location, zoom_start=self.zoom_start)
        for marker in self.markers.values():
            folium.Marker(
                location=marker["location"],
                popup=marker["popup"],
                icon=folium.Icon(color=marker["color"], icon="info-sign")  # Set color and icon
            ).add_to(self.map)
        self._reload_map()

    def create_marker(self, name, latitude=None, longitude=None, popup_text=None, color="blue"):
        """Create a new named marker with a specific color."""
        if name in self.markers:
            print(f"Marker '{name}' already exists.")
            return

        # Default position if none provided
        latitude = latitude or self.default_location[0]
        longitude = longitude or self.default_location[1]
        popup_text = popup_text or f"Marker {name}"

        # Add marker to the dictionary
        self.markers[name] = {
            "location": [latitude, longitude],
            "popup": popup_text,
            "color": color
        }
        self._regenerate_map()

    def delete_marker(self, name):
        """Delete a marker by its name."""
        if name in self.markers:
            del self.markers[name]
            self._regenerate_map()
        else:
            print(f"Marker '{name}' does not exist.")

    def modify_marker(self, name, latitude=None, longitude=None, popup_text=None):
        """Modify the position or popup text of a specific marker."""
        if name in self.markers:
            # Update marker properties
            marker = self.markers[name]
            marker["location"] = [
                latitude if latitude is not None else marker["location"][0],
                longitude if longitude is not None else marker["location"][1]
            ]
            marker["popup"] = popup_text if popup_text is not None else marker["popup"]

            self._regenerate_map()
        else:
            print(f"Marker '{name}' does not exist.")

    
    def update_map_location(self, latitude, longitude, zoom):
        self.default_location = [latitude, longitude]
        self.zoom_start = zoom
        self._regenerate_map()
    
