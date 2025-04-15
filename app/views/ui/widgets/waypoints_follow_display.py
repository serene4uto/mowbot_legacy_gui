import os
import yaml
import time
from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QFileDialog,
    QMessageBox,
    QGroupBox,
)
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtGui import QFont
import numpy as np
from scipy.spatial.transform import Rotation as R
from app.views.ui.widgets.common import ProcessButtonWidget, MapViewWidget
from app.utils.logger import logger


class WaypointsFollowOptBar(QWidget):
    
    def __init__(
        self,
        config,
        parent,
    ):
        super().__init__()
        
        self._config = config
        self._last_waypoints_file = None
        self._last_params_file = None
        self._wp_fl_started = False
        self._parent = parent
        
        self.start_btn = ProcessButtonWidget(
            start_script=config["script_wpfl_nav_start"],
            stop_script=config["script_wpfl_nav_stop"],
        )
        self.start_btn.setText('Start')
        self.start_btn.setFixedSize(80, 80)
        self.start_btn.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: green")
        
        self.load_wp_btn = QPushButton("Load\r\nWaypoints")
        self.load_wp_btn.setFixedSize(150, 80)
        self.load_wp_btn.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: Black")
        
        self.load_params_btn = QPushButton("Load\r\nParams")
        self.load_params_btn.setFixedSize(100, 80)
        self.load_params_btn.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: Black")
        
        self.wp_info_display = QLabel()
        self.wp_info_display.setText("Waypoints: Empty")
        # self.wp_info_display.setFixedHeight(40)
        
        self.param_info_display = QLabel()
        self.param_info_display.setText("Params: Empty")
        # self.param_info_display.setFixedHeight(40)
        
        self._init_ui()
        self._connect_signals()
        
    
    def _init_ui(self):
        layout = QVBoxLayout()
        bar_layout = QHBoxLayout()
        bar_layout.addWidget(self.start_btn)
        bar_layout.setSpacing(10)
        bar_layout.addWidget(self.load_wp_btn)
        bar_layout.setSpacing(10)
        bar_layout.addWidget(self.load_params_btn)
        bar_layout.setSpacing(10)
        # add info display
        info_grpbox = QGroupBox()
        info_layout = QVBoxLayout()
        info_layout.addWidget(self.wp_info_display)
        info_layout.setSpacing(10)
        info_layout.addWidget(self.param_info_display)
        info_layout.setSpacing(10)
        info_layout.addStretch(1)
        info_grpbox.setLayout(info_layout)
        bar_layout.addWidget(info_grpbox)
        bar_layout.setSpacing(10)
        # bar_layout.addStretch(1)
        layout.addLayout(bar_layout)
        layout.addStretch(1)
        self.setLayout(layout)
        
    
    def _connect_signals(self):
        # Connect button
        self.start_btn.clicked.connect(self._on_start_btn_clicked)
        self.load_wp_btn.clicked.connect(self._on_load_wp_btn_clicked)
        self.load_params_btn.clicked.connect(self._on_load_params_btn_clicked)
    
    
    def _on_load_wp_btn_clicked(self):
        
        wp_dir_path = self._config['mowbot_legacy_data_path'] + '/waypoints'
        target_wp_file_path = self._config['mowbot_legacy_data_path'] + '/__waypoints__.yaml'
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Waypoints File",
            wp_dir_path,
            "YAML Files (*.yaml);;All Files (*)",
        )
        
        if not file_path:
            return  # User canceled
        
        try:
            # Read selected file
            with open(file_path, 'r') as file:
                waypoints_data = yaml.safe_load(file)
                
            # check if __waypoints__.yaml file exists, 
            # if not, create it, change the content of it with selected file
            if not os.path.exists(target_wp_file_path):
                with open(target_wp_file_path, 'w') as file:
                    yaml.dump(waypoints_data, file)
            else:
                with open(target_wp_file_path, 'r+') as file:
                    existing_data = yaml.safe_load(file)
                    if existing_data != waypoints_data:
                        # Update the file with new data
                        file.seek(0)
                        yaml.dump(waypoints_data, file)
                        file.truncate()
            
            self.update_wp_info_display(
                f"Waypoints: {os.path.basename(file_path)}"
            )
            self._parent.map_view.reset()
            for waypoint in waypoints_data['waypoints']:
                self._parent.map_view.add_gps_position_mark(
                    latitude=float(waypoint['latitude']),
                    longitude=float(waypoint['longitude']),
                )
            
        except Exception as e:
            self.update_wp_info_display("Waypoints: Empty")
            logger.error(f"Error loading waypoints file: {e}")
            
    
    def _on_load_params_btn_clicked(self):
        param_dir_path = self._config['mowbot_legacy_data_path'] + '/params'
        target_param_file_path = self._config['mowbot_legacy_data_path'] + '/__params__.yaml'
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Params File",
            param_dir_path,
            "YAML Files (*.yaml);;All Files (*)",
        )
        
        if not file_path:
            return
        try:
            # Read selected file
            with open(file_path, 'r') as file:
                params_data = yaml.safe_load(file)
                
            # check if __params__.yaml file exists, 
            # if not, create it, change the content of it with selected file
            if not os.path.exists(target_param_file_path):
                with open(target_param_file_path, 'w') as file:
                    yaml.dump(params_data, file)
            else:
                with open(target_param_file_path, 'r+') as file:
                    existing_data = yaml.safe_load(file)
                    if existing_data != params_data:
                        # Update the file with new data
                        file.seek(0)
                        yaml.dump(params_data, file)
                        file.truncate()
            
            self.update_param_info_display(
                f"Params: {os.path.basename(file_path)}"
            )
        except Exception as e:
            self.update_param_info_display("Params: Empty")
            logger.error(f"Error loading params file: {e}")
    
    
    def _on_start_btn_clicked(self):
        
        # if self._parent.is_localized() is False or self._parent.is_bringup() is False:
        #     QMessageBox.warning(
        #         self,
        #         "Warning",
        #         "Please localize and bring up the robot before starting.",
        #     )
        #     return
        
        # if self._last_waypoints_file is None or self._last_params_file is None:
        #     QMessageBox.warning(
        #         self,
        #         "Warning",
        #         "Please load waypoints and params files before starting.",
        #     )
        #     return
        
        # Check if the process is already running
        if not self._wp_fl_started:
            self.start_btn.setText('Stop')
            self.start_btn.setStyleSheet(
                "font-size: 20px; font-weight: bold; color: red")
            self._wp_fl_started = True
            self.start_btn.start_process()
            
        else:
            self.start_btn.setText('Start')
            self.start_btn.setStyleSheet(
                "font-size: 20px; font-weight: bold; color: green")
            self._wp_fl_started = False
            self.start_btn.stop_process()
            
    
    def update_wp_info_display(self, text):
        self.wp_info_display.setText(text)
        
        
    def update_param_info_display(self, text):
        self.param_info_display.setText(text)

class WaypointsFollowDisplay(QWidget):
    def __init__(
        self,
        config,
        # parent,
    ):
        super().__init__()

        # self._parent = parent
        
        self._last_gps_lat = 0.0
        self._last_gps_lon = 0.0
        self._last_heading = 0.0
        
        self.opt_bar = WaypointsFollowOptBar(
                        config=config,
                        parent=self
                    )
        self.map_view = MapViewWidget() 

        self.gps_info_display = QLabel()
        self.hdg_info_display = QLabel()
        
        self._init_ui()
        
    
    def _init_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(self.opt_bar)
        layout.addSpacing(10)
        layout.addWidget(self.map_view)
        layout.addSpacing(10)

        # add info display
        info_layout = QHBoxLayout()
        info_layout.addWidget(self.gps_info_display)
        info_layout.setSpacing(10)
        info_layout.addWidget(self.hdg_info_display)
        info_layout.setSpacing(10)
        info_layout.addStretch(1)
        layout.addLayout(info_layout)
        
        layout.addStretch(1)
        self.setLayout(layout)


    @pyqtSlot(dict)
    def on_gps_fix_signal_received(self, data: dict):
        # logger.info(f" GPS Fix signal received: {data}")
        self._last_gps_lat = data['latitude']
        self._last_gps_lon = data['longitude']
        self.map_view.update_gps_position(
            latitude=data['latitude'],
            longitude=data['longitude'],
        )
        
        # Update the info display with the latest GPS position.
        self.gps_info_display.setText(
            f"lat: {data['latitude']:.6f}, lon: {data['longitude']:.6f}"
        )
        
    
    @pyqtSlot(dict)
    def on_heading_quat_signal_received(self, data: dict):
        # Turn quaternion to Euler angles (roll, pitch, yaw) in degrees using the "xyz" order.
        quat = [data['x'], data['y'], data['z'], data['w']]

        # quat_norm = sum(q*q for q in quat)**0.5
        # if quat_norm < 1e-10:  # If norm is effectively zero
        #     logger.warning(f"Received invalid quaternion with near-zero norm: {quat}")
        #     return  # Skip processing this invalid quaternion
        
        euler = R.from_quat(quat).as_euler('xyz', degrees=True)
        # Extract the ENU yaw (heading) from the Euler angles.
        yaw_enu = euler[2]
        # Convert the ENU yaw to NED yaw:
        # In ENU: 0° is East, 90° is North.
        # In NED: 0° is North.
        # Conversion: yaw_ned = (90 - yaw_enu) mod 360.
        yaw_ned = (90 - yaw_enu) % 360
        # logger.info(f"GPS Heading signal received: ENU yaw = {yaw_enu:.2f}°, NED yaw = {yaw_ned:.2f}°")
        self.map_view.update_heading(
            heading=yaw_ned,
        )
        # for _last_heading, using ENU yaw in radians
        self._last_heading = np.deg2rad(yaw_enu)
        
        # Update the info display with the latest heading.
        self.hdg_info_display.setText(
            f"heading: {self._last_heading:.4f} rad"
        )
        
        