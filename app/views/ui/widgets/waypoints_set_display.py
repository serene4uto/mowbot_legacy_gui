from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QListView,
    QListWidget,
    QTableWidget,
    QTableWidgetItem,
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
        self.start_btn.setFixedWidth(80)
        self.start_btn.setFixedHeight(80)

        self.table_view = QTableWidget(0, 3)
        self.table_view.setHorizontalHeaderLabels(['Lat', 'Lon', 'Hdg'])
        self.table_view.setFixedWidth(200)
        self.table_view.setFixedHeight(80)
        # set smaller text size for table view items
        font = self.table_view.font()
        font.setPointSize(8)
        self.table_view.setFont(font)
        self.table_view.verticalHeader().setDefaultSectionSize(20)
        self.table_view.horizontalHeader().setStretchLastSection(True)
        self.table_view.setColumnWidth(0, 60)  # First column width = 60px
        self.table_view.setColumnWidth(1, 60)  # Second column width = 60px
        self.table_view.setColumnWidth(2, 40)  # Third column width = 40px
        
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
        layout.addWidget(self.start_btn)
        layout.setSpacing(10)
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
        
    
    def add_row_to_table(self, data):
        row_position = self.table_view.rowCount()
        self.table_view.insertRow(row_position)
        self.table_view.setItem(row_position, 0, QTableWidgetItem(data['latitude']))
        self.table_view.setItem(row_position, 1, QTableWidgetItem(data['longitude']))
        self.table_view.setItem(row_position, 2, QTableWidgetItem(data['heading']))

class WaypointsSetDisplay(QWidget):
    def __init__(self, config):
        super().__init__()

        self._config = config
        self._last_gps_lat: float = 0.0
        self._last_gps_lon: float = 0.0
        self._last_heading: float = 0.0
        
        self.option_bar = WaypointsSetOptionBar(config=self._config)
        self.map_view = MapViewWidget()
        
        self._init_ui()
        self._init_signals()
        
    
    def _init_ui(self):
        layout = QVBoxLayout()
        # add option bar
        layout.addWidget(self.option_bar)
        layout.setSpacing(10)
        # add map view
        layout.addWidget(self.map_view)
        self.setLayout(layout)   
        
        
    def _init_signals(self):
        # self.option_bar.start_btn.clicked.connect(self.on_start_button_clicked)
        self.option_bar.log_btn.clicked.connect(self.on_optbar_wp_log_button_clicked)
        # self.option_bar.save_btn.clicked.connect(self.on_save_button_clicked)
        self.option_bar.rm_btn.clicked.connect(self.on_optbar_wp_remove_button_clicked)
        
        
    def on_optbar_wp_log_button_clicked(self):
        self.map_view.add_gps_position_mark(
            latitude=self._last_gps_lat,
            longitude=self._last_gps_lon
        )
        # show in list view
        self.option_bar.add_row_to_table({
            'latitude': str(self._last_gps_lat),
            'longitude': str(self._last_gps_lon),
            'heading': str(self._last_heading),
        })
        
        
    def on_optbar_wp_remove_button_clicked(self):
        if self.option_bar.table_view.rowCount() > 0:
            # Get the current selected row index.
            selected_row = self.option_bar.table_view.currentRow()
            if selected_row >= 0:
                # First, retrieve the data from the selected row.
                lat_item = self.option_bar.table_view.item(selected_row, 0)
                lon_item = self.option_bar.table_view.item(selected_row, 1)
                
                # Check if the items exist to avoid further attribute errors.
                if lat_item is not None and lon_item is not None:
                    rm_lat = lat_item.text()
                    rm_lon = lon_item.text()
    
                    # Remove the corresponding mark from the map using retrieved values.
                    self.map_view.remove_gps_position_mark(
                        latitude=float(rm_lat),
                        longitude=float(rm_lon)
                    )
    
                # Now remove the row from the table.
                self.option_bar.table_view.removeRow(selected_row)
                
        

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



        
    

        
        
        