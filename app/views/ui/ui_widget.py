import os
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
)
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QProcess
from app.views.ui.widgets import StatusBar, MenuBox, MultiFuncDisplay
from app.views.ui.widgets.common import ProcessButtonWidget
from app.services import FoxgloveWsHandler

class UIWidget(QWidget):

    bringup_btn_clicked_signal = pyqtSignal()

    def __init__(
        self,
        config=None,
    ):
        super().__init__()
        
        self.config = config
        self.bringup = False
        self.foxglove_ws_handler = FoxgloveWsHandler(config=self.config)
        
        self.mfunc_display = MultiFuncDisplay(config=self.config)
        self.status_bar = StatusBar()
        self.menu_box = MenuBox()
        self.bringup_btn = ProcessButtonWidget(
            start_script=self.config['script_bringup_start'],
            stop_script=self.config['script_bringup_stop'],
        )
        self.bringup_btn.setText('Start Bringup')
        self.bringup_btn.setStyleSheet("font-size: 20px; font-weight: bold; color: green")
        self.bringup_btn.setFixedHeight(100)

        # initial setup
        self.menu_box.setEnabled(False)
        self.mfunc_display.setEnabled(False)
        
        self.__init_ui()
        self._connect_signals()
        
        
    def __init_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(self.status_bar)
        hlayout = QHBoxLayout()
        hleft_layout = QVBoxLayout()
        hleft_layout.addWidget(self.menu_box)
        hleft_layout.addWidget(self.bringup_btn)
        hlayout.addLayout(hleft_layout)
        hlayout.addWidget(self.mfunc_display)
        layout.addLayout(hlayout) 
        self.setLayout(layout)
    
    
    def _connect_signals(self):
        # Connect button
        self.bringup_btn.clicked.connect(self.on_bringup_btn_clicked)
        # self.clean_btn.clicked.connect(self.on_clean_btn_clicked)
        # Connect signals
        self.menu_box.settings_btn_clicked_signal.connect(
            self.mfunc_display.on_settings_btn_clicked
        )
        self.menu_box.set_wp_task_btn_clicked_signal.connect(
            self.mfunc_display.on_set_wp_task_btn_clicked
        )
        self.menu_box.follow_wp_task_btn_clicked_signal.connect(
            self.mfunc_display.on_follow_wp_task_btn_clicked
        )
        self.menu_box.util_btn_clicked_signal.connect(
            self.mfunc_display.on_util_btn_clicked
        )
        # Connect service signals
        self.foxglove_ws_handler.sensor_status_signal.connect(
            self.status_bar.on_status_signal_received
        )
        ## wp_set_display
        self.foxglove_ws_handler.gps_fix_signal.connect(
            self.mfunc_display.wp_set_display.on_gps_fix_signal_received
        )
        self.foxglove_ws_handler.heading_quat_signal.connect(
            self.mfunc_display.wp_set_display.on_heading_quat_signal_received
        )
        ## wp_follow_display
        self.foxglove_ws_handler.gps_fix_signal.connect(
            self.mfunc_display.wp_follow_display.on_gps_fix_signal_received
        )
        self.foxglove_ws_handler.heading_quat_signal.connect(
            self.mfunc_display.wp_follow_display.on_heading_quat_signal_received
        )
        


    def on_bringup_btn_clicked(self):
        self.bringup = not self.bringup
        if self.bringup:
            self.bringup_btn.setText('Stop Bringup')
            self.bringup_btn.setStyleSheet("font-size: 20px; font-weight: bold; color: red")
            self.menu_box.setEnabled(True)
            self.mfunc_display.setEnabled(True)
            self.bringup_btn.start_process()
            self.foxglove_ws_handler.start()
        else:
            self.bringup_btn.setText('Start Bringup')
            self.bringup_btn.setStyleSheet("font-size: 20px; font-weight: bold; color: green")
            self.menu_box.setEnabled(False)
            self.mfunc_display.setEnabled(False)
            self.status_bar.reset_status()
            self.foxglove_ws_handler.stop()
            self.bringup_btn.stop_process()
