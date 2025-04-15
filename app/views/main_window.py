from PyQt5.QtWidgets import (
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QStatusBar,
)

from app.app_info import __appname__, __appdescription__
from .main_view import MainView
# from app.views.ui import UIWidget


class MainWindow(QMainWindow):
    """Main window class for the application"""
    
    def __init__(
        self,
        config=None,
    ):
        super().__init__()
        self._config = config

        # Set the window title
        self.setContentsMargins(0, 0, 0, 0)
        self.setWindowTitle(__appname__)
        
        # Set the central widget and the main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # ui_widget = UIWidget(
        #     config=self._config
        # )
        # main_layout.addWidget(ui_widget)
        
        self.main_view = MainView(
            config=self._config,
        )
        main_layout.addWidget(self.main_view)

        # Set the main layout
        widget = QWidget()
        widget.setLayout(main_layout)
        self.setCentralWidget(widget)

        status_bar = QStatusBar()
        status_bar.showMessage(f"{__appname__} - {__appdescription__}")
        self.setStatusBar(status_bar)