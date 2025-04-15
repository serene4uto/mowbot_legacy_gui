#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_CONTAINER="gui_wp_bringup"

bash "$SCRIPT_DIR/localize_stop.bash"
bash "$SCRIPT_DIR/wpfl_nav_stop.bash"

# find if the target container is existing
if [ "$(docker ps -aq -f name=$TARGET_CONTAINER)" ]; then
    # if the target container is running, stop it
    if [ "$(docker ps -q -f name=$TARGET_CONTAINER)" ]; then
        echo "Stopping existing container $TARGET_CONTAINER..."
        docker stop $TARGET_CONTAINER
    fi
fi