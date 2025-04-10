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

from PyQt5.QtCore import pyqtSignal, pyqtSlot, QTimer

from .map_view import MapView
from .process_button import ProcessButton

from app.utils.logger import logger  


class WaypointsSetOptionBar(QWidget):
    def __init__(self, config):
        super().__init__()
        
        layout = QHBoxLayout()

        self.start_btn = ProcessButton(
            start_script=config['script_wp_set_start'],
            stop_script=config['script_wp_set_stop'],
        )
        self.start_btn.setText('Start')
        self.start_btn.setFixedWidth(100)
        self.start_btn.setFixedHeight(80)
        layout.addWidget(self.start_btn)
        layout.setSpacing(10)

        self.list_view = QListView()
        self.list_view.setFixedWidth(200)
        self.list_view.setFixedHeight(80)
        layout.addWidget(self.list_view)
        layout.setSpacing(10)
        
        self.log_btn = QPushButton('Log')
        self.log_btn.setFixedWidth(100)
        self.log_btn.setFixedHeight(80)
        layout.addWidget(self.log_btn)
        layout.setSpacing(10)

        # self.genlayout = QVBoxLayout()
        # self.res_lbl = QLabel('Resolution:')
        # self.genlayout.addWidget(self.res_lbl)

        #TODO: auto generate resolution options

        layout.addStretch(1)

        self.save_btn = QPushButton('Save')
        self.save_btn.setFixedWidth(100)
        self.save_btn.setFixedHeight(80)
        layout.addWidget(self.save_btn)
        
        self.setLayout(layout)
        self.setFixedHeight(100)

class WaypointsSetDisplay(QWidget):
    def __init__(self, config):
        super().__init__()

        self.config = config

        self.update_mark_timer = QTimer(self)
        self.update_mark_timer.timeout.connect(self.on_update_mark_timer)
        self.update_mark_timer.start(2000)

        self.last_gps_data: dict = {}

        self.logged_count = 0
        
        layout = QVBoxLayout()
        
        # add option bar
        self.option_bar = WaypointsSetOptionBar(config=self.config)
        layout.addWidget(self.option_bar)
        layout.setSpacing(10)
        
        # add map view
        self.map_view = MapView()
        layout.addWidget(self.map_view)
        
        self.setLayout(layout)

        self.map_view.update_loc_btn.clicked.connect(
            self.update_map_location
        )

        self.map_view.create_marker(
            name='AMR',
            latitude=36.1141352,
            longitude=128.4188682,
            popup_text='AMR',
            color='green',
        )


        self.option_bar.log_btn.clicked.connect(
            self.on_log_btn_clicked
        )

    def on_log_btn_clicked(self):
        if self.last_gps_data:
            self.map_view.create_marker(
                name=f'LOG_{self.logged_count}',
                latitude=self.last_gps_data['latitude'],
                longitude=self.last_gps_data['longitude'],
                popup_text='LOG',
                color='red',
            )
            self.logged_count += 1

    def on_update_mark_timer(self):
        if self.last_gps_data:
            self.map_view.modify_marker(
                name='AMR',
                latitude=self.last_gps_data['latitude'],
                longitude=self.last_gps_data['longitude'],
            )

    def update_map_location(self):
        if self.last_gps_data:
            self.map_view.update_map_location(
                latitude=self.last_gps_data['latitude'],
                longitude=self.last_gps_data['longitude'],
                zoom=18,
            )



    @pyqtSlot(dict)
    def on_gps_fix_signal_received(self, data: dict):
        logger.info(f" GPS Fix signal received: {data}")
        self.last_gps_data = data



        
    

        
        
        