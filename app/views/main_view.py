from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
)

from .status_bar_view import StatusBarView
from .menu_box_view import MenuBoxView
from .multi_panel_view import MultiPanelView

class MainView(QWidget):
    
    def __init__(
        self,
        config,
    ):
        super().__init__()
        
        self._config = config
        
        self.status_bar = StatusBarView()
        self.menu_box = MenuBoxView()
        self.multi_panel = MultiPanelView(
            config=self._config
        )
        
        self._init_ui()
        
    
    def _init_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(self.status_bar)
        layout.addSpacing(10)
        
        hlayout = QHBoxLayout()
        hlayout.addWidget(self.menu_box)
        hlayout.addSpacing(10)
        hlayout.addWidget(self.multi_panel)
        # hlayout.addSpacing(10)
        # hlayout.addStretch(1)
        
        layout.addLayout(hlayout)
        layout.stretch(1)
        self.setLayout(layout)
        
        
    def get_status_bar(self):
        return self.status_bar
        