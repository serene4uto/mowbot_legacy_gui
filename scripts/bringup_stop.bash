#!/bin/bash

# Define Docker container name
CONTAINER_NAME="mowbot_humble"

# Get all PIDs of the ROS2 launch commands inside the Docker container
ROS2_PIDS=$(docker exec "$CONTAINER_NAME" pgrep -f "ros2 launch mowbot_bringup bringup.launch.py")

if [ -z "$ROS2_PIDS" ]; then
    echo "No ROS2 launch process found in container $CONTAINER_NAME."
    exit 1
fi

echo "Found ROS2 launch processes with PIDs: $ROS2_PIDS in container $CONTAINER_NAME."

# Check if pstree is available in the container
if ! docker exec "$CONTAINER_NAME" which pstree > /dev/null 2>&1; then
    echo "The 'pstree' command is not available inside the container $CONTAINER_NAME."
    echo "Please install it (e.g., 'apt-get update && apt-get install -y psmisc') before running this script."
    exit 1
fi

# Iterate over each found PID
for PID in $ROS2_PIDS; do
    echo "Processing ROS2 launch process with PID: $PID"

    # Extract all PIDs in the process tree using pstree and sed
    PIDS_TO_KILL=$(docker exec "$CONTAINER_NAME" bash -c "pstree -p $PID" | sed -n 's/.*(\([0-9]\+\)).*/\1/p')

    if [ -z "$PIDS_TO_KILL" ]; then
        echo "No processes found for PID $PID. Possibly it exited already."
        continue
    fi

    echo "Attempting a graceful shutdown of these processes: $PIDS_TO_KILL"
    # First, try to gracefully terminate with SIGTERM
    docker exec "$CONTAINER_NAME" bash -c "echo '$PIDS_TO_KILL' | xargs -r kill -TERM"

    # Give processes some time to exit cleanly
    sleep 2

    # Check if any of the processes are still running
    RUNNING_PIDS=$(docker exec "$CONTAINER_NAME" bash -c "ps -o pid= -p $(echo $PIDS_TO_KILL | tr ' ' ',') 2>/dev/null")
    if [ -n "$RUNNING_PIDS" ]; then
        echo "Not all processes terminated gracefully. Forcing kill..."
        docker exec "$CONTAINER_NAME" bash -c "echo '$RUNNING_PIDS' | xargs -r kill -9"
    fi

    echo "All processes for PID $PID should now be terminated."
done

echo "All ROS2 launch processes and their descendants have been successfully killed."
