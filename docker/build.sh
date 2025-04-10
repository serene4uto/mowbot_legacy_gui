#!/usr/bin/env bash


set -e


# Function to print help message
print_help() {
    echo "Usage: build.sh [OPTIONS]"
    echo "Options:"
    echo "  --help          Display this help message"
    echo "  -h              Display this help message"
    echo "  --platform      Specify the platform (default: current platform)"
    echo ""
    echo "Note: The --platform option should be one of 'linux/amd64' or 'linux/arm64'."
}


SCRIPT_DIR=$(readlink -f "$(dirname "$0")")
WORKSPACE_ROOT="$SCRIPT_DIR/.."


# Parse arguments
parse_arguments() {
    while [ "$1" != "" ]; do
        case "$1" in
        --help | -h)
            print_help
            exit 1
            ;;
        --platform)
            option_platform="$2"
            shift
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


# Set platform
set_platform() {
    if [ -n "$option_platform" ]; then
        platform="$option_platform"
    else
        platform="linux/amd64"
        if [ "$(uname -m)" = "aarch64" ]; then
            platform="linux/arm64"
        fi
    fi
}


# Set arch lib dir
set_arch_lib_dir() {
    if [ "$platform" = "linux/arm64" ]; then
        lib_dir="aarch64"
    elif [ "$platform" = "linux/amd64" ]; then
        lib_dir="x86_64"
    else
        echo "Unsupported platform: $platform"
        exit 1
    fi
}


# Load env
load_env() {
    source "$WORKSPACE_ROOT/app.env"
}


#install some necessary apt packages
install_apt_packages() {
    sudo apt-get update
    sudo apt-get install -y \
        curl \
        git \
        docker-buildx
}



# Build images
build_images() {
    # https://github.com/docker/buildx/issues/484
    export BUILDKIT_STEP_LOG_MAX_SIZE=10000000

    echo "Building images for platform: $platform"
    echo "Base image: $base_image"
    echo "Lib dir: $lib_dir"
    echo "Target: $target"

    set -x
    docker buildx build \
        --load \
        --progress=plain \
        --platform="$platform" \
        --build-arg BASE_IMAGE="$base_image" \
        --build-arg LIB_DIR="$lib_dir" \
        -f "$SCRIPT_DIR/Dockerfile" \
        -t "ghcr.io/serene4uto/mowbot-legacy-gui:latest" \
        "$WORKSPACE_ROOT"
    set +x
}


# Remove dangling images
remove_dangling_images() {
    docker image prune -f
}


# Main script execution
parse_arguments "$@"
set_platform
set_arch_lib_dir
load_env
install_apt_packages
build_images
remove_dangling_images