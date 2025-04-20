import os
from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider,
    QPushButton, QFileDialog, QTabWidget
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5 import QtGui
from typing import List, Tuple, Dict, Any

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
    signal_save_btn_clicked = pyqtSignal(str, dict)  # str: file path, dict: params
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__()
        
        self._config = config
        self.full_params = None
        
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
                ("lookahead_dist", "Lookahead Distance (m)", 0, 2.0, 0.1),
                ("lookahead_time", "Lookahead Time (s)", 0, 3.0, 0.1),
                ("desired_linear_vel", "Desired Linear Velocity (m/s)", 0, 1.0, 0.1),
                ("regulated_linear_scaling_min_radius", "Regulated Linear Scaling Min Radius (m)", 0, 2.0, 0.01),
                ("regulated_linear_scaling_min_speed", "Regulated Linear Scaling Min Speed (m/s)", 0, 1.0, 0.01),
                ("max_angular_accel", "Max Angular Acceleration (rad/s^2)", 0, 3.2, 0.01),
                ("min_approach_linear_velocity", "Min Approach Linear Velocity (m/s)", 0, 2.0, 0.05),
                ("rotate_to_heading_angular_vel", "Rotate to Heading Angular Velocity (rad/s)", 0, 2.0, 0.01),
                ("rotate_to_heading_min_angle", "Rotate to Heading Min Angle (rad)", 0, 3.14, 0.01),
            ]
        )
        
        self.others_tab = SettingsTabWidget(
            param_configs=[
                ("xy_goal_tolerance", "XY Goal Tolerance (m)", 0, 1.0, 0.01),
                ("yaw_goal_tolerance", "Yaw Goal Tolerance (rad)", 0, 3.14, 0.01),
                ("movement_time_allowance", "Movement Time Allowance (s)", 0, 20.0, 0.1),
                ("required_movement_angle", "Required Movement Angle (rad)", 0, 3.14, 0.1),
                ("required_movement_radius", "Required Movement Radius (m)", 0, 2.0, 0.1),
                # ("failure_tolerance", "Failure Tolerance (s)", 0, 1.0, 0.1),
                # ("min_theta_velocity_threshold", "Min Theta Velocity Threshold (rad/s)", 0, 2.0, 0.1),
                # ("min_x_velocity_threshold", "Min X Velocity Threshold (m/s)", 0, 2.0, 0.1),
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
        self.sync_params_file_path = \
            f"{self._config['mowbot_legacy_data_path']}/__params__.yaml"
    
    def _init_buttons(self):
        """Initialize buttons with consistent styling."""
        btn_font = QtGui.QFont()
        btn_font.setPointSize(12)
        btn_font.setBold(True)
        btn_font.setWeight(75)
        
        self.params_sync_btn = QPushButton("Sync")
        self.params_load_btn = QPushButton("Load")
        self.params_save_btn = QPushButton("Save")
        
        
        # Apply consistent styling to buttons
        for btn in [self.params_sync_btn, self.params_load_btn, self.params_save_btn]:
            btn.setFixedSize(UI_CONSTANTS["BUTTON_WIDTH"], UI_CONSTANTS["BUTTON_HEIGHT"])
            btn.setFont(btn_font)
        
    def _init_ui(self):
        """Initialize the user interface layout."""
        layout = QHBoxLayout()
        layout.addWidget(self.settings_tab)
        
        # Buttons layout
        btn_layout = QVBoxLayout()
        btn_layout.addWidget(self.params_sync_btn)
        btn_layout.addSpacing(10)
        btn_layout.addWidget(self.params_load_btn)
        btn_layout.addSpacing(10)
        btn_layout.addWidget(self.params_save_btn)
        btn_layout.addStretch(1)
        
        layout.addStretch(1)
        layout.addLayout(btn_layout)
        self.setLayout(layout)
    
    def prompt_file_dialog_for_load(self):
        """Load parameters from the file."""
        load_file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Parameters File",
            f"{self._config['mowbot_legacy_data_path']}/params",
            "YAML Files (*.yaml);;All Files (*)",
        )
        return load_file_path
        
    def prompt_file_dialog_for_save(self):
        """Save parameters to the file."""
        current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        default_filename = f"params_{current_time}.yaml"
        default_path = f"{self._config['mowbot_legacy_data_path']}/params"
        save_file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Select Parameters File",
            os.path.join(default_path, default_filename),
            "YAML Files (*.yaml);;All Files (*)",
        )
        return save_file_path
    
    def update_load_params(self, yaml_data: dict) -> None:
        """Update the load parameters with the given YAML data."""
        # logger.info(f"Updating load parameters with data: {yaml_data}")
        
        self.full_params = yaml_data
        
        params_widgets = self.regulated_pure_pursuit_tab.params_widgets
        rpp_data = self.full_params['controller_server']['ros__parameters']['FollowPath']
        logger.info(f"Updating load parameters with data: {rpp_data}")
        params_widgets["lookahead_dist"].set_value(rpp_data['lookahead_dist'])
        params_widgets["lookahead_time"].set_value(rpp_data['lookahead_time'])
        params_widgets["desired_linear_vel"].set_value(rpp_data['desired_linear_vel'])
        params_widgets["regulated_linear_scaling_min_radius"].set_value(rpp_data['regulated_linear_scaling_min_radius'])
        params_widgets["regulated_linear_scaling_min_speed"].set_value(rpp_data['regulated_linear_scaling_min_speed'])
        params_widgets["max_angular_accel"].set_value(rpp_data['max_angular_accel'])
        params_widgets["min_approach_linear_velocity"].set_value(rpp_data['min_approach_linear_velocity'])
        params_widgets["rotate_to_heading_angular_vel"].set_value(rpp_data['rotate_to_heading_angular_vel'])
        params_widgets["rotate_to_heading_min_angle"].set_value(rpp_data['rotate_to_heading_min_angle'])
        
        params_widgets = self.others_tab.params_widgets
        others_data = self.full_params['controller_server']['ros__parameters']['general_goal_checker']
        params_widgets["xy_goal_tolerance"].set_value(others_data['xy_goal_tolerance'])
        params_widgets["yaw_goal_tolerance"].set_value(others_data['yaw_goal_tolerance'])
        
        others_data = self.full_params['controller_server']['ros__parameters']['progress_checker']
        params_widgets["movement_time_allowance"].set_value(others_data['movement_time_allowance'])
        params_widgets["required_movement_angle"].set_value(others_data['required_movement_angle'])
        params_widgets["required_movement_radius"].set_value(others_data['required_movement_radius'])
        
        # others_data = self.full_params['controller_server']['ros__parameters']
        # params_widgets["failure_tolerance"].set_value(others_data['failure_tolerance'])
        # params_widgets["min_theta_velocity_threshold"].set_value(others_data['min_theta_velocity_threshold'])
        # params_widgets["min_x_velocity_threshold"].set_value(others_data['min_x_velocity_threshold'])
    
    def get_params(self):
        if self.full_params is None:
            logger.error("No parameters loaded. Cannot get params.")
            return None
        
        params_widgets = self.regulated_pure_pursuit_tab.params_widgets 
        rpp_data = self.full_params['controller_server']['ros__parameters']['FollowPath']
        rpp_data['lookahead_dist'] = params_widgets["lookahead_dist"].get_value()
        rpp_data['lookahead_time'] = params_widgets["lookahead_time"].get_value()
        rpp_data['desired_linear_vel'] = params_widgets["desired_linear_vel"].get_value()
        rpp_data['regulated_linear_scaling_min_radius'] = params_widgets["regulated_linear_scaling_min_radius"].get_value()
        rpp_data['regulated_linear_scaling_min_speed'] = params_widgets["regulated_linear_scaling_min_speed"].get_value()
        rpp_data['max_angular_accel'] = params_widgets["max_angular_accel"].get_value()
        rpp_data['min_approach_linear_velocity'] = params_widgets["min_approach_linear_velocity"].get_value()
        rpp_data['rotate_to_heading_angular_vel'] = params_widgets["rotate_to_heading_angular_vel"].get_value()
        rpp_data['rotate_to_heading_min_angle'] = params_widgets["rotate_to_heading_min_angle"].get_value()
        self.full_params['controller_server']['ros__parameters']['FollowPath'] = rpp_data # reupdate
        params_widgets = self.others_tab.params_widgets
        others_data = self.full_params['controller_server']['ros__parameters']['general_goal_checker']
        others_data['xy_goal_tolerance'] = params_widgets["xy_goal_tolerance"].get_value()
        others_data['yaw_goal_tolerance'] = params_widgets["yaw_goal_tolerance"].get_value() 
        self.full_params['controller_server']['ros__parameters']['general_goal_checker'] = others_data # reupdate
        others_data = self.full_params['controller_server']['ros__parameters']['progress_checker']
        others_data['movement_time_allowance'] = params_widgets["movement_time_allowance"].get_value()
        others_data['required_movement_angle'] = params_widgets["required_movement_angle"].get_value()
        others_data['required_movement_radius'] = params_widgets["required_movement_radius"].get_value()
        self.full_params['controller_server']['ros__parameters']['progress_checker'] = others_data # reupdate
        # others_data = self.full_params['controller_server']['ros__parameters']
        # others_data['failure_tolerance'] = params_widgets["failure_tolerance"].get_value()
        # others_data['min_theta_velocity_threshold'] = params_widgets["min_theta_velocity_threshold"].get_value()
        # others_data['min_x_velocity_threshold'] = params_widgets["min_x_velocity_threshold"].get_value()
        # self.full_params['controller_server']['ros__parameters'] = others_data
        return self.full_params
        
        
        
        
            
            
    