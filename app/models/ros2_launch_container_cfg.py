import os

HOST_HOME = os.environ.get("HOST_HOME")
if HOST_HOME is None:
    raise EnvironmentError("HOST_HOME environment variable is not set.")

IMAGE = "ghcr.io/serene4uto/mowbot-legacy-base"

CONTAINERS_CFG = {
    
    # Bringup 
    "bringup": {
        "name": "mowbot_legacy_gui_bringup",
        "image": IMAGE,
        "command": [
            "/bin/bash", 
            "-c", 
            ". /opt/mowbot_legacy/setup.bash \
            && ros2 launch mowbot_legacy_launch gui_wp_bringup.launch.py \
                uros:=true foxglove:=true \
                imu:=true madgwick:=true \
                ntrip:=true gps:=true \
                laser:=true \
                sensormon:=true \
                rl:=false \
            "
        ],
        "network_mode": "host",
        "privileged": True,
        "environment": {
            "DISPLAY": ":0.0",
        },
        "volumes": {
            f"{HOST_HOME}/mowbot_legacy_data": {"bind": "/mowbot_legacy_data", "mode": "rw"},
            "/dev": {"bind": "/dev", "mode": "rw"},
            "/tmp/.X11-unix": {"bind": "/tmp/.X11-unix", "mode": "rw"},
        },
        "detach": True,
        "tty": True,
    },
    
    # Localization
    "localization": {
        "name": "mowbot_legacy_gui_localization",
        "image": IMAGE,
        "command": [
            "/bin/bash", 
            "-c", 
            ". /opt/mowbot_legacy/setup.bash \
            && ros2 launch mowbot_legacy_launch gui_wp_localization.launch.py \
            "
        ],
        "network_mode": "host",
        "privileged": True,
        "environment": {
            "DISPLAY": ":0.0",
        },
        "volumes": {
            f"{HOST_HOME}/mowbot_legacy_data": {"bind": "/mowbot_legacy_data", "mode": "rw"},
            "/dev": {"bind": "/dev", "mode": "rw"},
            "/tmp/.X11-unix": {"bind": "/tmp/.X11-unix", "mode": "rw"},
        },
        "working_dir": "/mowbot_legacy",
        "detach": True,
        "tty": True,
    },
    
    # Navigation with Waypoints following
    "navigation_wp_follow": {
        "name": "mowbot_legacy_gui_nav_wp_follow",
        "image": IMAGE,
        "command": [
            "/bin/bash", 
            "-c", 
            ". /opt/mowbot_legacy/setup.bash \
            && ros2 launch mowbot_legacy_launch gui_wp_follow_nav.launch.py \
            "
        ],
        "network_mode": "host",
        "privileged": True,
        "environment": {
            "DISPLAY": ":0.0",
        },
        "volumes": {
            f"{HOST_HOME}/mowbot_legacy_data": {"bind": "/mowbot_legacy_data", "mode": "rw"},
            "/dev": {"bind": "/dev", "mode": "rw"},
            "/tmp/.X11-unix": {"bind": "/tmp/.X11-unix", "mode": "rw"},
        },
        "working_dir": "/mowbot_legacy",
        "detach": True,
        "tty": True,
    }
    
}