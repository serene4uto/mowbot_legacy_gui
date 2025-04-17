#!/usr/bin/env bash

CURRENT_DIR=$(readlink -f "$(dirname "$0")")
SCRIPT_DIR=$CURRENT_DIR/scripts
RESOURCES_DIR=$CURRENT_DIR/resources
WORKSPACE_ROOT="$SCRIPT_DIR/.."

set -e

# Function to print help message
print_help() {
    echo "Usage: install.sh [OPTIONS]"
    echo "Options:"
    echo "  --help              Display this help message"
    echo "  -h                  Display this help message"
    echo "  --docker-build      Build the Docker image"
    echo "  --desktop-icon      Create a desktop icon for mowbot_legacy_gui"
    echo "  --startup-service   Create a systemd startup service for mowbot_legacy_gui"
    echo ""
}

# Initialize option variables
option_docker_build=false
option_desktop_icon=false
option_startup_service=false

# Parse arguments
parse_arguments() {
    while [ "$1" != "" ]; do
        case "$1" in
        --help | -h)
            print_help
            exit 0
            ;;
        --docker-build)
            option_docker_build=true
            ;;
        --desktop-icon)
            option_desktop_icon=true
            ;;
        --startup-service)
            option_startup_service=true
            ;;
        *)
            echo "Unknown option: $1"
            print_help
            exit 1
            ;;
        esac
        shift
    done
}

print_options() {
    echo "Options:"
    echo "  --docker-build: $option_docker_build"
    echo "  --desktop-icon: $option_desktop_icon"
    echo "  --startup-service: $option_startup_service"
}

build_docker_image() {
    # check if --docker-build is passed
    if [ "$option_docker_build" = true ]; then  # Fixed boolean comparison
        # check if docker is installed
        if ! command -v docker &>/dev/null; then
            echo "Docker is not installed. Please install Docker first."
            exit 1
        fi

        # build the docker image
        bash "$SCRIPT_DIR/build.sh"
    fi
}

setup_app_directory() {
    echo "Setting up application directory..."
    
    # create directory /opt/mowbot_legacy_gui
    if ! sudo mkdir -p /opt/mowbot_legacy_gui; then
        echo "Error: Failed to create directory /opt/mowbot_legacy_gui"
        return 1
    fi

    # copy mowbot_legacy_gui.sh to /opt/mowbot_legacy_gui
    if ! sudo cp "$CURRENT_DIR/mowbot_legacy_gui.sh" /opt/mowbot_legacy_gui/mowbot_legacy_gui.sh; then
        echo "Error: Failed to copy mowbot_legacy_gui.sh"
        return 1
    fi
    
    # make the script executable
    if ! sudo chmod +x /opt/mowbot_legacy_gui/mowbot_legacy_gui.sh; then
        echo "Error: Failed to make script executable"
        return 1
    fi
    
    echo "Application directory setup complete"
}


# setup desktop icon
setup_desktop_icon() {
    # check if --desktop-icon is passed
    if [ "$option_desktop_icon" = true ]; then  # Fixed boolean comparison
        # Get the name of the script file without the extension
        app_name=$(basename "$SCRIPT_DIR/mowbot_legacy_gui.sh" .sh)

        # Set the name of the desktop launcher file
        desktop_file="$app_name.desktop"

        # command to run the script
        command="/bin/bash -c '/opt/mowbot_legacy_gui/mowbot_legacy_gui.sh'"

        # Create the desktop launcher file
        echo "[Desktop Entry]" > "$desktop_file"
        echo "Type=Application" >> "$desktop_file"
        echo "Name=$app_name" >> "$desktop_file"  # Fixed variable name
        echo "Icon=$RESOURCES_DIR/mowbot_app_icon.jpg" >> "$desktop_file"
        echo "Exec=$command" >> "$desktop_file"
        echo "Terminal=false" >> "$desktop_file"

        # Make the desktop launcher file executable
        chmod +x "$desktop_file"

        # Move the desktop launcher file to the actual desktop directory
        mv "$desktop_file" "$HOME/Desktop/"

        echo "Desktop icon setup complete"
    fi
}

# setup systemd service for startup 
setup_startup_service(){
    # check if --startup-service is passed
    if [ "$option_startup_service" = "--startup-service" ]; then
        # Create a systemd service file
        echo ""
    fi
}




# main script entry point
parse_arguments "$@"
print_options
build_docker_image
setup_app_directory
setup_desktop_icon
setup_startup_service
echo "Installation complete"