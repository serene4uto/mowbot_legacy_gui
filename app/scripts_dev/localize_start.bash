#!/bin/bash

docker run --rm -i \
    --name gui_wp_localization \
    --network host \
    -e DISPLAY=:0.0 \
    -w /mowbot_legacy \
    -v "$HOST_HOME/mowbot_legacy_data:/mowbot_legacy_data" \
    -v "/dev:/dev" \
    -v "/tmp/.X11-unix:/tmp/.X11-unix" \
    ghcr.io/serene4uto/mowbot-legacy-base /bin/bash -c "\
        . /workspaces/mowbot_legacy/install/setup.bash \
        && ros2 launch mowbot_legacy_launch gui_wp_localization.launch.py \
    "