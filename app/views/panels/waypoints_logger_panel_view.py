# waypoints_logger_panel_view.py
import os
import yaml
import numpy as np
from datetime import datetime

from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QGroupBox,
    QFileDialog,
)
from PyQt5.QtCore import pyqtSlot
from scipy.spatial.transform import Rotation as R

from .map_view import MapView
from app.utils.logger import logger


class WaypointsLoggerOptionBarView(QWidget):
    """
    A view component for the option bar in the waypoint logging panel.
    It provides the table for displaying logged waypoints and buttons for logging,
    removing, and saving waypoint entries.
    """
    def __init__(self, config):
        super().__init__()
        self._config = config

        # Create the table for displaying waypoint data.
        self.table_view = QTableWidget(0, 3)
        self.table_view.setHorizontalHeaderLabels(['Lat', 'Lon', 'Hdg'])
        self.table_view.setFixedWidth(200)
        self.table_view.setFixedHeight(80)
        font = self.table_view.font()
        font.setPointSize(8)
        self.table_view.setFont(font)
        self.table_view.verticalHeader().setDefaultSectionSize(20)
        self.table_view.horizontalHeader().setStretchLastSection(True)
        self.table_view.setColumnWidth(0, 60)
        self.table_view.setColumnWidth(1, 60)
        self.table_view.setColumnWidth(2, 40)
        
        # Create buttons.
        self.log_btn = QPushButton('Log')
        self.log_btn.setFixedWidth(60)
        self.log_btn.setFixedHeight(40)
        
        self.rm_btn = QPushButton('Remove')
        self.rm_btn.setFixedWidth(60)
        self.rm_btn.setFixedHeight(40)

        self.save_btn = QPushButton('Save')
        self.save_btn.setFixedWidth(100)
        self.save_btn.setFixedHeight(80)
        
        self._init_ui()

    def _init_ui(self):
        layout = QHBoxLayout()
        layout.addWidget(self.table_view)
        layout.setSpacing(10)
        
        log_rm_layout = QVBoxLayout()
        log_rm_layout.addWidget(self.log_btn)
        log_rm_layout.addWidget(self.rm_btn)
        layout.addLayout(log_rm_layout)
        layout.setSpacing(10)
        
        layout.addStretch(1)
        layout.addWidget(self.save_btn)
        self.setLayout(layout)
        self.setFixedHeight(100)
        
    def add_row_to_table(self, data: dict):
        """
        Adds a row to the table using a data dictionary with keys:
        'latitude', 'longitude', and 'heading'.
        """
        row_position = self.table_view.rowCount()
        self.table_view.insertRow(row_position)
        self.table_view.setItem(row_position, 0, QTableWidgetItem(data['latitude']))
        self.table_view.setItem(row_position, 1, QTableWidgetItem(data['longitude']))
        self.table_view.setItem(row_position, 2, QTableWidgetItem(data['heading']))
        
    def clear_table(self):
        self.table_view.setRowCount(0)
        self.table_view.clearContents()
        self.table_view.setHorizontalHeaderLabels(['Lat', 'Lon', 'Hdg'])


class WaypointsLoggerPanelView(QWidget):
    """
    A view that composes the waypoint logging option bar and a map view.
    It also displays current GPS and heading information.
    """
    def __init__(
        self, 
        config
    ):
        super().__init__()
        self._config = config
        self._last_gps_lat: float = 0.0
        self._last_gps_lon: float = 0.0
        self._last_heading: float = 0.0
        
        # Flag for whether logging is active (if needed by a controller)
        self._wp_log_started = False
        
        # Create subcomponents.
        self.option_bar = WaypointsLoggerOptionBarView(config=self._config)
        self.map_view = MapView(
            config=self._config
        )
        self.gps_info_display = QLabel()
        self.hdg_info_display = QLabel()
        
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(self.option_bar)
        layout.setSpacing(10)
        layout.addWidget(self.map_view)
        layout.setSpacing(10)
          
        # Create an information display area.
        info_layout = QHBoxLayout()
        info_layout.addWidget(self.gps_info_display)
        info_layout.setSpacing(10)
        info_layout.addWidget(self.hdg_info_display)
        info_layout.setSpacing(10)
        info_layout.addStretch(1)
        layout.addLayout(info_layout)
        
        self.setLayout(layout) 
        
        
    # -- UI Update API Methods --
    def update_table_with_logged_waypoint(self, latitude: float, longitude: float, heading: float):
        """
        Updates the map view with a new marker and adds the corresponding data to the table.
        """
        self.map_view.add_gps_position_mark(latitude=latitude, longitude=longitude)
        self.option_bar.add_row_to_table({
            'latitude': str(latitude),
            'longitude': str(longitude),
            'heading': str(heading),
        })
    
    def clear_logged_waypoints(self):
        self.option_bar.clear_table()

    def update_gps_info(self, latitude: float, longitude: float):
        """
        Updates the map view's GPS marker and refreshes the GPS information display.
        """
        self._last_gps_lat = latitude
        self._last_gps_lon = longitude
        self.map_view.update_gps_position(latitude=latitude, longitude=longitude)
        self.gps_info_display.setText(
            f"lat: {latitude:.6f}, lon: {longitude:.6f}"
        )
        
    def update_heading_info(self, data: dict):
        """
        Converts quaternion heading data to a readable value, updates the map view's heading,
        and refreshes the heading information display.
        """
        quat = [data['x'], data['y'], data['z'], data['w']]
        euler = R.from_quat(quat).as_euler('xyz', degrees=True)
        yaw_enu = euler[2]
        yaw_ned = (90 - yaw_enu) % 360
        self.map_view.update_heading(heading=yaw_ned)
        self._last_heading = np.deg2rad(yaw_enu)
        self.hdg_info_display.setText(
            f"heading: {self._last_heading:.4f} rad"
        )

    def prompt_for_save_file(self) -> str:
        """
        Opens a file dialog to prompt the user for a file location to save waypoints.
        Returns the selected file path or an empty string if canceled.
        """
        current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        default_filename = f"waypoints_{current_time}.yaml"
        default_path = os.path.join(self._config['mowbot_legacy_data_path'], 'waypoints')
        if not os.path.exists(default_path):
            os.makedirs(default_path)
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Waypoints",
            os.path.join(default_path, default_filename),
            "YAML Files (*.yaml);;All Files (*)",
        )
        return file_path

    def show_save_success(self, file_path: str):
        """
        Provides a UI indication (or logs a message) that the waypoints were saved successfully.
        """
        logger.info(f"Waypoints saved to {file_path}")
