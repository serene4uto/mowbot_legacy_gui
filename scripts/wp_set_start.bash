#!/bin/bash

docker run --rm -i \
    --name mowbot_legacy_wp_set \
    --network host \
    -e DISPLAY=:0.0 \
    -w /mowbot_legacy \
    -v "$HOST_HOME/mowbot_legacy_data:/mowbot_legacy_data" \
    -v "/dev:/dev" \
    -v "/tmp/.X11-unix:/tmp/.X11-unix" \
    ghcr.io/serene4uto/mowbot-legacy-base /bin/bash -c "\
        . /opt/mowbot_legacy/setup.bash \
        && ros2 launch mowbot_legacy_launch rl_dual_ekf_navsat.launch.py \
    "