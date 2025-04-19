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
    
    def update_label(self, value):
        """Update the label with the current slider value."""
        scaled_value = value / self.scale_factor
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
    
    # UI Constants
    SLIDER_LABEL_WIDTH = 300
    BUTTON_WIDTH = 200
    BUTTON_HEIGHT = 100
    
    def __init__(
        self,
        config: dict,
    ):
        super().__init__()
        
        self._config = config
        self._is_params_loaded = False
        self.last_full_rams = {}
        
        self._init_slider_params()
        self._init_buttons()
        self._init_ui()
        
        # Load default parameters
        default_params_fp = \
            self._config['mowbot_legacy_data_path'] + '/params/default.yaml'
        self.signal_load_btn_clicked.emit(default_params_fp)
    
    def _init_slider_params(self):
        """Initialize all parameter sliders with their configurations."""
        # Parameter definitions - easier to maintain and modify
        param_configs = [
            ("lookahead_distance", "Lookahead Distance (m)", 0, 2.0, 0.1),
            ("lookahead_time", "Lookahead Time (s)", 0, 3.0, 0.1),
            ("desired_linear_vel", "Desired Linear Velocity (m/s)", 0, 1.0, 0.1),
            ("regulated_linear_scaling_min_radius", "Regulated Linear Scaling Min Radius (m)", 0, 2.0, 0.1),
            ("regulated_linear_scaling_min_speed", "Regulated Linear Scaling Min Speed (m/s)", 0, 1.0, 0.1),
            ("max_angular_accel", "Max Angular Acceleration (rad/s^2)", 0, 3.2, 0.1),
            ("min_approach_linear_velocity", "Min Approach Linear Velocity (m/s)", 0, 2.0, 0.05),
            ("rotate_to_heading_angular_vel", "Rotate to Heading Angular Velocity (rad/s)", 0, 2.0, 0.1),
            ("rotate_to_heading_min_angle", "Rotate to Heading Min Angle (rad)", 0, 3.14, 0.1),
        ]
        
        self.adjustable_params_widget = {}
        
        for param_id, label, min_val, max_val, step in param_configs:
            slider = SettingSliderItem(
                label,
                min=min_val,
                max=max_val,
                step=step,
                fixed_width=self.SLIDER_LABEL_WIDTH
            )
            setattr(self, f"params_{param_id}", slider)
            self.adjustable_params_widget[param_id] = slider
    
    def _init_buttons(self):
        """Initialize buttons with consistent styling."""
        self.params_load_btn = QPushButton("Load")
        self.params_save_btn = QPushButton("Save")
        
        # Apply consistent styling to buttons
        for btn in [self.params_load_btn, self.params_save_btn]:
            btn.setFixedWidth(self.BUTTON_WIDTH)
            btn.setFixedHeight(self.BUTTON_HEIGHT)
        
        # Connect button signals
        self.params_load_btn.clicked.connect(self.on_load_btn_clicked)
        self.params_save_btn.clicked.connect(self.on_save_btn_clicked)
        
    def _init_ui(self):
        """Initialize the user interface layout."""
        layout = QHBoxLayout()
        
        # Parameters group box
        params_group = QGroupBox("Regulated Pure Pursuit")
        params_layout = QVBoxLayout()
        
        for widget in self.adjustable_params_widget.values():
            params_layout.addWidget(widget)
            params_layout.addSpacing(10)
        
        params_layout.addStretch(1)
        params_group.setLayout(params_layout)
        layout.addWidget(params_group)
        
        # Buttons layout
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
        load_file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Parameters File",
            self._config['mowbot_legacy_data_path'] + '/params',
            "YAML Files (*.yaml);;All Files (*)",
        )
        if load_file_path:
            self.signal_load_btn_clicked.emit(load_file_path)
        
    def on_save_btn_clicked(self):
        """Save parameters to the file."""
        save_file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Select Parameters File",
            self._config['mowbot_legacy_data_path'] + '/params',
            "YAML Files (*.yaml);;All Files (*)",
        )
        if save_file_path:
            self.signal_save_btn_clicked.emit(save_file_path)