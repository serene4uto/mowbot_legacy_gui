ARG BASE_IMAGE

FROM $BASE_IMAGE AS base
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Export basic Qt variables
RUN echo 'export DISPLAY=:0' >> ~/.bashrc
RUN echo 'export QT_XCB_GL_INTEGRATION=none' >> ~/.bashrc

# Copy the requirements file into the container
COPY requirements.txt /mowbot_legacy_gui/requirements.txt

# Install dependencies from apt
RUN apt-get update && apt-get install -y \
        python3-pip \
        python3-pyqt5 \
        qtwebengine5-dev \
        qtwebengine5-dev-tools \
        python3-pyqt5.qtwebengine \
        docker.io \
    && apt-get clean

# Upgrade pip (with break-system-packages if needed)
RUN /bin/python3 -m pip install --upgrade pip --break-system-packages

# Install remaining pip packages (PyQt5 excluded from requirements.txt)
RUN /bin/python3 -m pip install \
    --no-cache-dir \
    --verbose \
    --break-system-packages \
    -r /mowbot_legacy_gui/requirements.txt

# Set the working directory
WORKDIR /mowbot_legacy_gui

# Copy the rest of the application code into the container
COPY app /mowbot_legacy_gui/app

# Create entrypoint
COPY docker/etc/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["/bin/bash"]
