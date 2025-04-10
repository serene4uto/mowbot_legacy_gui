#!/usr/bin/env bash

# Get the user ID and group ID of the local user
USER_ID=${LOCAL_UID}
USER_NAME=${LOCAL_USER}
GROUP_ID=${LOCAL_GID}
GROUP_NAME=${LOCAL_GROUP}



# Check if any of the variables are empty
if [[ -z $USER_ID || -z $USER_NAME || -z $GROUP_ID || -z $GROUP_NAME ]]; then
    exec "$@"
    export DISPLAY:=0
    export QT_XCB_GL_INTEGRATION=none
    alias python3='/usr/bin/python3'
else
    echo "Starting with user: $USER_NAME >> UID $USER_ID, GID: $GROUP_ID"

    # Create group and user with GID/UID
    groupadd -g "$GROUP_ID" "$GROUP_NAME"
    useradd -u "$USER_ID" -g "$GROUP_ID" -s /bin/bash -m -d /home/"$USER_NAME" "$USER_NAME"

    # Add sudo privileges to the user
    echo "$USER_NAME ALL=(ALL) NOPASSWD:ALL" >>/etc/sudoers

    # Source ROS2
    # hadolint ignore=SC1090
    export DISPLAY:=0
    export QT_XCB_GL_INTEGRATION=none
    alias python3='/usr/bin/python3'

    # Execute the command as the user
    exec /usr/sbin/gosu "$USER_NAME" "$@"
fi