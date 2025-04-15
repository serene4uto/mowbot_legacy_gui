import os
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QMessageBox,
    QPushButton,
)
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QProcess
from app.views.ui.widgets import StatusBar, MenuBox, MultiFuncDisplay
from app.views.ui.widgets.common import ProcessButtonWidget
from app.services import FoxgloveWsHandler
from app.services import ROS2LaunchContainerManager
from app.utils.logger import logger

class UIWidget(QWidget):

    bringup_btn_clicked_signal = pyqtSignal()

    def __init__(
        self,
        config=None,
    ):
        super().__init__()
        
        self._config = config
        
        # robot_state
        self._bringup = False
        self._localized = False
        
        self.foxglove_ws_handler = FoxgloveWsHandler(
            config=self._config
        )
        self.launch_container_manager = ROS2LaunchContainerManager(
            config=self._config,
        )
        
        self.mfunc_display = MultiFuncDisplay(
            config=self._config
        )
        self.status_bar = StatusBar()
        self.menu_box = MenuBox()
        
        # Bringup button
        self.bringup_btn = QPushButton()
        self.bringup_btn.setText('Start Bringup')
        self.bringup_btn.setStyleSheet("font-size: 20px; font-weight: bold; color: green")
        self.bringup_btn.setFixedHeight(80)
        self.bringup_btn.setEnabled(True)
        
        # Localize button
        self.localize_btn = QPushButton()
        self.localize_btn.setText('Start Localize')
        self.localize_btn.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: gray")
        self.localize_btn.setFixedHeight(80)
        self.localize_btn.setEnabled(False)

        # initial setup
        self.menu_box.setEnabled(False)
        self.mfunc_display.setEnabled(False)
        
        self._init_ui()
        self._connect_signals()
        
        
    def _init_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(self.status_bar)
        hlayout = QHBoxLayout()
        hleft_layout = QVBoxLayout()
        hleft_layout.addWidget(self.menu_box)
        hleft_layout.addSpacing(10)
        hleft_layout.addWidget(self.localize_btn)
        hleft_layout.addSpacing(10)
        hleft_layout.addWidget(self.bringup_btn)
        
        # Create a container widget for hleft_layout and set a fixed width
        left_container = QWidget()
        left_container.setLayout(hleft_layout)
        left_container.setFixedWidth(250)  # Adjust this value as needed
        
        hlayout.addWidget(left_container)
        hlayout.addWidget(self.mfunc_display)
        
        # Set stretch factors - make the right side expand more
        hlayout.setStretchFactor(left_container, 1)
        hlayout.setStretchFactor(self.mfunc_display, 4)
        
        layout.addLayout(hlayout) 
        self.setLayout(layout)
    
    
    def _connect_signals(self):
        # Connect button
        self.bringup_btn.clicked.connect(self.on_bringup_btn_clicked)
        self.localize_btn.clicked.connect(self.on_localize_btn_clicked)
        
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
        

    def is_bringup(self):
        return self._bringup
    
    
    def is_localized(self):
        return self._localized
        
        
    def on_localize_btn_clicked(self):
        if self._bringup is False:
            QMessageBox.warning(
                self,
                'Warning',
                'Please start Bring-up first.',
                QMessageBox.Ok
            )
            return
        
        self._localized = not self._localized
        if self._localized:
            self.localize_btn.setText('Stop Localize')
            self.localize_btn.setStyleSheet("font-size: 20px; font-weight: bold; color: red")
            self.localize_btn.start_process()
        else:
            self.localize_btn.setText('Start Localize')
            self.localize_btn.setStyleSheet("font-size: 20px; font-weight: bold; color: green")
            self.localize_btn.stop_process()
        

    def on_bringup_btn_clicked(self):
        self._bringup = not self._bringup
        if self._bringup:
            # start bringup
            self.bringup_btn.setText('Stop Bringup')
            self.bringup_btn.setStyleSheet(
                "font-size: 20px; font-weight: bold; color: red")
            # enable
            self.localize_btn.setEnabled(True)
            self.localize_btn.setStyleSheet(
                "font-size: 20px; font-weight: bold; color: green")
            self.menu_box.setEnabled(True)
            self.mfunc_display.setEnabled(True)
            # start all services
            self.bringup_btn.start_process()
            self.foxglove_ws_handler.start()
        else:
            # stop bringup
            self.bringup_btn.setText('Start Bringup')
            self.bringup_btn.setStyleSheet(
                "font-size: 20px; font-weight: bold; color: green")
            # reset everything 
            self.status_bar.reset_status()
            # disable
            self.localize_btn.setEnabled(False)
            self.localize_btn.setStyleSheet( # grayed out
                "font-size: 20px; font-weight: bold; color: gray")
            self.menu_box.setEnabled(False)
            self.mfunc_display.setEnabled(False)
            # stop all services
            self.foxglove_ws_handler.stop()
            self.bringup_btn.stop_process()
            
            
