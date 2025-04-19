from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider,
    QPushButton, QFileDialog, QTabWidget
)
from PyQt5.QtCore import Qt, pyqtSignal
from typing import List, Tuple, Dict, Any


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
        
        self.label_text = label
        self.min = min
        self.max = max
        self.step = step
        
        # Calculate scale factor once during initialization
        self.scale_factor = int(1 / self.step)
        
        self.label = QLabel(f"{self.label_text}: {min:.2f}")
        self.label.setFixedWidth(fixed_width)
        
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setFixedWidth(250)
        self.slider.setMinimum(int(self.min * self.scale_factor))
        self.slider.setMaximum(int(self.max * self.scale_factor))
        self.slider.setSingleStep(1)  # Use integer steps internally
        self.slider.valueChanged.connect(self.update_label)
        
        # Apply styles
        self._apply_styles()
        self._init_ui()

    def _apply_styles(self):
        """Apply styles to slider - extracted for clarity"""
        self.slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 20px;
                background: #d3d3d3;
                border-radius: 10px;
            }
            QSlider::handle:horizontal {
                width: 20px;
                height: 40px;
                background: #5c5c5c;
                border: 1px solid #3c3c3c;
                border-radius: 10px;
                margin: -10px 0;
            }
        """)

    def _init_ui(self):
        layout = QHBoxLayout()
        layout.addWidget(self.label)
        layout.addSpacing(10)
        layout.addWidget(self.slider)
        layout.addStretch(1)
        layout.setContentsMargins(0, 0, 0, 0)  # Reduce wasted space
        self.setLayout(layout)
    
    def update_label(self, value):
        """Update the label with the current slider value."""
        scaled_value = value / self.scale_factor
        self.label.setText(f"{self.label_text}: {scaled_value:.2f}")
        
    def get_value(self) -> float:
        """Get the current value of the slider."""
        return self.slider.value() / self.scale_factor
    
    def set_value(self, value: float) -> None:
        """Set the slider to a specific value."""
        clamped_value = min(max(value, self.min), self.max)
        self.slider.setValue(int(clamped_value * self.scale_factor))


# Common UI constants - centralized to avoid duplication
UI_CONSTANTS = {
    "SLIDER_LABEL_WIDTH": 300,
    "BUTTON_WIDTH": 200,
    "BUTTON_HEIGHT": 100,
}


class SettingsTabWidget(QWidget):
    def __init__(
        self,
        param_configs: List[Tuple[str, str, float, float, float]],
    ):
        super().__init__()
        
        self.params_widgets: Dict[str, SettingSliderItem] = {}
        
        # Create all sliders based on configuration
        for param_id, label, min_val, max_val, step in param_configs:
            slider = SettingSliderItem(
                label,
                min=min_val,
                max=max_val,
                step=step,
                fixed_width=UI_CONSTANTS["SLIDER_LABEL_WIDTH"]
            )
            self.params_widgets[param_id] = slider
        
        self._init_ui()
        
    def _init_ui(self):
        params_layout = QVBoxLayout()
        
        for widget in self.params_widgets.values():
            params_layout.addSpacing(20)
            params_layout.addWidget(widget)
        
        params_layout.addStretch(1)
        self.setLayout(params_layout)


class SettingsPanelView(QWidget):
    signal_load_btn_clicked = pyqtSignal(str)  # str: file path
    signal_save_btn_clicked = pyqtSignal(str)  # str: file path
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__()
        
        self._config = config
        self.settings_tab = QTabWidget()
        # increase tab height and font size
        self.settings_tab.setStyleSheet(
            """
            QTabBar::tab {
                height: 50px;
                width: 250px;
                font-size: 14px;
                font-weight: bold;
            }
            """
        )
        
        # Create regulated pure pursuit tab
        self.regulated_pure_pursuit_tab = SettingsTabWidget(
            param_configs=[
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
        )
        
        self.others_tab = SettingsTabWidget(
            param_configs=[
                ("xy_goal_tolerance", "XY Goal Tolerance (m)", 0, 1.0, 0.01),
                ("yaw_goal_tolerance", "Yaw Goal Tolerance (rad)", 0, 3.14, 0.01),
                ("movement_time_allowance", "Movement Time Allowance (s)", 0, 20.0, 0.1),
                ("required_movement_angle", "Required Movement Angle (rad)", 0, 3.14, 0.1),
                ("required_movement_radius", "Required Movement Radius (m)", 0, 2.0, 0.1),
                ("failure_tolerance", "Failure Tolerance (s)", 0, 1.0, 0.1),
                ("min_theta_velocity_threshold", "Min Theta Velocity Threshold (rad/s)", 0, 2.0, 0.1),
                ("min_x_velocity_threshold", "Min X Velocity Threshold (m/s)", 0, 2.0, 0.1),
            ]
        )
        
        self.settings_tab.addTab(
            self.regulated_pure_pursuit_tab,
            "Regulated Pure Pursuit"
        )
        self.settings_tab.addTab(
            self.others_tab,
            "Others"
        )
        
        self.settings_tab.setFixedWidth(600)
        self._init_buttons()
        self._init_ui()
        
        # Load default parameters
        default_params_fp = f"{self._config['mowbot_legacy_data_path']}/params/default.yaml"
        self.signal_load_btn_clicked.emit(default_params_fp)
    
    def _init_buttons(self):
        """Initialize buttons with consistent styling."""
        self.params_load_btn = QPushButton("Load")
        self.params_save_btn = QPushButton("Save")
        
        # Apply consistent styling to buttons
        for btn in [self.params_load_btn, self.params_save_btn]:
            btn.setFixedSize(UI_CONSTANTS["BUTTON_WIDTH"], UI_CONSTANTS["BUTTON_HEIGHT"])
        
        # Connect button signals
        self.params_load_btn.clicked.connect(self.on_load_btn_clicked)
        self.params_save_btn.clicked.connect(self.on_save_btn_clicked)
        
    def _init_ui(self):
        """Initialize the user interface layout."""
        layout = QHBoxLayout()
        layout.addWidget(self.settings_tab)
        
        # Buttons layout
        btn_layout = QVBoxLayout()
        btn_layout.addWidget(self.params_load_btn)
        btn_layout.addSpacing(10)
        btn_layout.addWidget(self.params_save_btn)
        btn_layout.addStretch(1)
        
        layout.addStretch(1)
        layout.addLayout(btn_layout)
        self.setLayout(layout)
    
    def on_load_btn_clicked(self):
        """Load parameters from the file."""
        load_file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Parameters File",
            f"{self._config['mowbot_legacy_data_path']}/params",
            "YAML Files (*.yaml);;All Files (*)",
        )
        if load_file_path:
            self.signal_load_btn_clicked.emit(load_file_path)
        
    def on_save_btn_clicked(self):
        """Save parameters to the file."""
        save_file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Select Parameters File",
            f"{self._config['mowbot_legacy_data_path']}/params",
            "YAML Files (*.yaml);;All Files (*)",
        )
        if save_file_path:
            self.signal_save_btn_clicked.emit(save_file_path)
            
    