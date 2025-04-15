
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGroupBox,
    QStackedWidget,
)
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from .waypoints_set_display import WaypointsSetDisplay
from .waypoints_follow_display import WaypointsFollowDisplay
from .settings_display import SettingsDisplay
from app.utils.logger import logger


class MultiFuncDisplay(QWidget):
    def __init__(self, config):
        super().__init__()

        self._config = config
        
        self.staked_widget = QStackedWidget()
        self.wp_set_display = WaypointsSetDisplay(config=self._config)
        self.wp_follow_display = WaypointsFollowDisplay(config=self._config)
        self.settings_display = SettingsDisplay()
        
        self._init_ui()
        
        
    def _init_ui(self):
        layout = QVBoxLayout()
        mfunc_grb = QGroupBox()
        mfunc_layout = QVBoxLayout()
        self.staked_widget.addWidget(self.wp_set_display)
        self.staked_widget.addWidget(self.wp_follow_display)
        self.staked_widget.addWidget(self.settings_display)
        mfunc_layout.addWidget(self.staked_widget)
        mfunc_grb.setLayout(mfunc_layout)
        layout.addWidget(mfunc_grb)
        self.setLayout(layout)
        
    
    @pyqtSlot()
    def on_set_wp_task_btn_clicked(self):
        self.staked_widget.setCurrentIndex(0)
        
        
    @pyqtSlot()
    def on_follow_wp_task_btn_clicked(self):
        self.staked_widget.setCurrentIndex(1)
        
        
    @pyqtSlot()
    def on_settings_btn_clicked(self):
        self.staked_widget.setCurrentIndex(2)
        
        
        
    
        
        