import os

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
)

from PyQt5.QtCore import pyqtSignal, pyqtSlot, QProcess

from app.views.ui.widgets import StatusBar, MenuBox, MultiFuncDisplay, ProcessButton


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
        
        # Create a main vertical layout
        layout = QVBoxLayout()
        
        # Add a status bar at the top
        self.status_bar = StatusBar()
        layout.addWidget(self.status_bar)
        
        # Create a horizontal layout
        self.hlayout = QHBoxLayout()
        
        # Create a left vertical layout that expands fully
        self.hleft_layout = QVBoxLayout()
        
        # Add the menu box to the left layout
        self.menu_box = MenuBox()
        self.hleft_layout.addWidget(self.menu_box)

        operate_layout = QHBoxLayout()
        self.bringup_btn = ProcessButton(
            start_script=self.config['script_bringup_start'],
            stop_script=self.config['script_bringup_stop'],
        )
        self.bringup_btn.setText('Start Bringup')
        self.bringup_btn.setStyleSheet("font-size: 20px; font-weight: bold; color: green")
        self.bringup_btn.setFixedHeight(100)
        self.hleft_layout.addWidget(self.bringup_btn)
        # operate_layout.addWidget(self.bringup_btn)
        # operate_layout.addSpacing(10)
        # self.clean_btn = ProcessButton(
        #     start_script=self.config['cleaning_script'],
        #     stop_script=None,
        # )
        # self.clean_btn.setText('Clean')
        # self.clean_btn.setStyleSheet("font-size: 20px; font-weight: bold; color: blue")
        # self.clean_btn.setFixedHeight(100)
        # operate_layout.addWidget(self.clean_btn)
        # self.hleft_layout.addLayout(operate_layout)
        
        # Ensure the left layout takes all vertical space
        self.hlayout.addLayout(self.hleft_layout)
        
        self.mfunc_display = MultiFuncDisplay(config=self.config)
        self.hlayout.addWidget(self.mfunc_display)
        
        # self.hlayout.addStretch(1) 
        
        # Add the horizontal layout to the main vertical layout
        layout.addLayout(self.hlayout) 
        
        self.setLayout(layout)

        # initial setup
        self.menu_box.setEnabled(False)
        self.mfunc_display.setEnabled(False)

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
        self.foxglove_ws_handler.gps_fix_signal.connect(
            self.mfunc_display.wp_set_display.on_gps_fix_signal_received
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
    
    # def on_clean_btn_clicked(self):
    #     self.clean_btn.start_process()