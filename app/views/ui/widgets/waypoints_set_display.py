from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QListView,
    QGroupBox,
    QComboBox,
)
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from scipy.spatial.transform import Rotation as R
from app.views.ui.widgets.common.map_view_widget import MapViewWidget
from app.views.ui.widgets.common.process_button_widget import ProcessButtonWidget
from app.utils.logger import logger  

class WaypointsSetOptionBar(QWidget):
    def __init__(self, config):
        super().__init__()

        self.start_btn = ProcessButtonWidget(
            start_script=config['script_wp_set_start'],
            stop_script=config['script_wp_set_stop'],
        )
        self.start_btn.setText('Start')
        self.start_btn.setFixedWidth(100)
        self.start_btn.setFixedHeight(80)

        self.list_view = QListView()
        self.list_view.setFixedWidth(200)
        self.list_view.setFixedHeight(80)

        self.log_btn = QPushButton('Log')
        self.log_btn.setFixedWidth(100)
        self.log_btn.setFixedHeight(80)

        self.save_btn = QPushButton('Save')
        self.save_btn.setFixedWidth(100)
        self.save_btn.setFixedHeight(80)
        
        self._init_ui()

        
    def _init_ui(self):
        layout = QHBoxLayout()
        layout.addWidget(self.start_btn)
        layout.setSpacing(10)
        layout.addWidget(self.list_view)
        layout.setSpacing(10)
        layout.addWidget(self.log_btn)
        layout.setSpacing(10)
        layout.addStretch(1)
        layout.addWidget(self.save_btn)
        self.setLayout(layout)
        self.setFixedHeight(100)

class WaypointsSetDisplay(QWidget):
    def __init__(self, config):
        super().__init__()

        self._config = config
        self._last_gps_lat: float = 0.0
        self._last_gps_lon: float = 0.0
        self._last_heading: float = 0.0
        self._logged_count = 0
        
        self.option_bar = WaypointsSetOptionBar(config=self._config)
        self.map_view = MapViewWidget()
        
        self._init_ui()
        
    
    def _init_ui(self):
        layout = QVBoxLayout()
        # add option bar
        layout.addWidget(self.option_bar)
        layout.setSpacing(10)
        # add map view
        layout.addWidget(self.map_view)
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
        
    
    @pyqtSlot(dict)
    def on_heading_quat_signal_received(self, data: dict):
        # Turn quaternion to Euler angles (roll, pitch, yaw) in degrees using the "xyz" order.
        quat = [data['x'], data['y'], data['z'], data['w']]
        euler = R.from_quat(quat).as_euler('xyz', degrees=True)
        # Extract the ENU yaw (heading) from the Euler angles.
        yaw_enu = euler[2]
        # Convert the ENU yaw to NED yaw:
        # In ENU: 0° is East, 90° is North.
        # In NED: 0° is North.
        # Conversion: yaw_ned = (90 - yaw_enu) mod 360.
        yaw_ned = (90 - yaw_enu) % 360
        # logger.info(f"GPS Heading signal received: ENU yaw = {yaw_enu:.2f}°, NED yaw = {yaw_ned:.2f}°")
        self._last_heading = yaw_ned
        self.map_view.update_heading(
            heading=yaw_ned,
        )



        
    

        
        
        