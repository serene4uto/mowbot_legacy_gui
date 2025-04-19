
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QGroupBox,
    QSlider,
    QPushButton,
    QFileDialog,
)
from PyQt5.QtCore import Qt, pyqtSignal
from app.utils.logger import logger


class SettingSliderItem(QWidget):
    def __init__(
        self,
        label: str,
        min: float = 0,
        max: float = 100,
        step: float = 1,
        fixed_width: int = 200,
    ): 
        super().__init__()
        
        self.label = label
        self.min = min
        self.max = max
        self.step = step
        
        # Dynamically calculate scale factor based on step
        self.scale_factor = int(1 / self.step)
        
        self.lb = QLabel(f"{self.label}: {min}")  # Display initial value
        self.lb.setFixedWidth(fixed_width)
        self.lb.font().setPointSize(12)
        
        self.slider = QSlider(
            orientation=Qt.Horizontal,
            minimum=int(self.min * self.scale_factor),
            maximum=int(self.max * self.scale_factor),
            singleStep=int(self.step * self.scale_factor),
        )
        self.slider.setFixedWidth(250) # Set fixed width for the slider
        # self.slider.setFixedHeight(100) # Set fixed height for the slider
        self.slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 20px;  /* Adjust the height of the groove */
                background: #d3d3d3; /* Groove color */
                border-radius: 10px; /* Optional rounded corners */
            }
            QSlider::handle:horizontal {
                width: 20px;  /* Adjust the width of the handle */
                height: 40px; /* Adjust the height of the handle */
                background: #5c5c5c; /* Handle color */
                border: 1px solid #3c3c3c; /* Optional border */
                border-radius: 10px; /* Make the handle circular */
                margin: -10px 0; /* Center the handle in the groove */
            }
        """)
        
        self.slider.valueChanged.connect(self.update_label)  # Connect signal
        self._init_ui()

    def _init_ui(self):
        layout = QHBoxLayout()
        layout.addWidget(self.lb)
        layout.addSpacing(10)
        layout.addWidget(self.slider)
        layout.addStretch(1)
        self.setLayout(layout)
        # self.setFixedWidth(500)
    
    def update_label(self, value):
        """Update the label with the current slider value."""
        scaled_value = value / self.scale_factor
        # Format to remove unnecessary trailing zeros
        # formatted_value = f"{scaled_value:.2f}".rstrip('0').rstrip('.')
        formatted_value = f"{scaled_value:.2f}"
        self.lb.setText(f"{self.label}: {formatted_value}")
        
    def get_value(self):
        """Get the current value of the slider."""
        return self.slider.value() / self.scale_factor
    
    def set_value(self, value):
        """Set the slider to a specific value."""
        set_value = min(max(value, self.min), self.max)  # Ensure value is within bounds
        self.update_label(set_value * self.scale_factor)
        self.slider.setValue(int(set_value * self.scale_factor))

class SettingsPanelView(QWidget):
    
    signal_load_btn_clicked = pyqtSignal(str) # str: file path
    signal_save_btn_clicked = pyqtSignal(str) # str: file path
    
    def __init__(
        self,
        config: dict,
    ):
        super().__init__()
        
        self._config = config
        
        # self.setWindowTitle("Settings Panel")
        self._is_params_loaded = False
        
        self.last_params = {}
        
        self.params_desired_linear_vel = SettingSliderItem(
            "Desired Linear Velocity (m/s)",
            min=0,max=1.0,step=0.1,
            fixed_width=300,
        )
        self.params_lookahead_distance = SettingSliderItem(
            "Lookahead Distance (m)",
            min=0, max=5.0, step=0.1,
            fixed_width=300,
        )
        self.params_min_approach_velocity = SettingSliderItem(
            "Min Approach Velocity (m/s)",
            min=0, max=2.0, step=0.05,
            fixed_width=300,
        )
        self.params_rotate_to_heading_angular_vel = SettingSliderItem(
            "Rotate to Heading Angular Velocity (rad/s)",
            min=0, max=2.0, step=0.1,
            fixed_width=300,
        )
        self.params_rotate_to_heading_min_angle = SettingSliderItem(
            "Rotate to Heading Min Angle (rad)",
            min=0, max=3.14, step=0.1,
            fixed_width=300,
        )
        
        self.params_load_btn = QPushButton("Load")
        self.params_load_btn.setFixedWidth(200)
        self.params_load_btn.setFixedHeight(100)
        
        self.params_save_btn = QPushButton("Save")
        self.params_save_btn.setFixedWidth(200)
        self.params_save_btn.setFixedHeight(100)
        
        self._init_ui()
        
        default_params_fp = \
            self._config['mowbot_legacy_data_path'] + '/params/default.yaml'
        self.signal_load_btn_clicked.emit(default_params_fp)
        
    def _init_ui(self):
        layout = QHBoxLayout()
        
        flp_grbox = QGroupBox("Regulated Pure Pursuit")
        flp_layout = QVBoxLayout()
        
        flp_layout.addWidget(self.params_desired_linear_vel)
        flp_layout.addSpacing(10)
        flp_layout.addWidget(self.params_lookahead_distance)
        flp_layout.addSpacing(10)
        flp_layout.addWidget(self.params_min_approach_velocity)
        flp_layout.addSpacing(10)
        flp_layout.addWidget(self.params_rotate_to_heading_angular_vel)
        flp_layout.addSpacing(10)
        flp_layout.addWidget(self.params_rotate_to_heading_min_angle)
        flp_layout.addStretch(1)
        flp_grbox.setLayout(flp_layout)
        layout.addWidget(flp_grbox)
        
        layout.addStretch(1)
        btn_layout = QVBoxLayout()
        btn_layout.addWidget(self.params_load_btn)
        btn_layout.addSpacing(10)
        btn_layout.addWidget(self.params_save_btn)
        btn_layout.addStretch(1)
        layout.addLayout(btn_layout)
        
        
        self.setLayout(layout)


    
    def on_load_btn_clicked(self):
        """Load parameters from the file."""
        
        # open file dialog to select the parameter file
        load_file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Parameters File",
            self._config['mowbot_legacy_data_path'] + '/params',
            "YAML Files (*.yaml);;All Files (*)",
        )
        if not load_file_path:
            return
        self.signal_load_btn_clicked.emit(load_file_path)
        
    def on_save_btn_clicked(self):
        """Save parameters to the file."""
        
        # open file dialog to select the parameter file
        save_file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Select Parameters File",
            self._config['mowbot_legacy_data_path'] + '/params',
            "YAML Files (*.yaml);;All Files (*)",
        )
        if not save_file_path:
            return
        self.signal_save_btn_clicked.emit(save_file_path)
        
    
        