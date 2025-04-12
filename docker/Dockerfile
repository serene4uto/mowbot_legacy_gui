ARG BASE_IMAGE

FROM $BASE_IMAGE AS base
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# add to ~/.bashrc
# RUN echo 'alias python3='/usr/bin/python3'' >> ~/.bashrc
# RUN echo 'alias pip3='/usr/bin/pip3'' >> ~/.bashrc
RUN echo 'export DISPLAY=:0' >> ~/.bashrc
RUN echo 'export QT_XCB_GL_INTEGRATION=none' >> ~/.bashrc

# Copy the requirements file into the container
COPY requirements.txt /mowbot_legacy_gui/

# Install the required packages
RUN apt-get update && apt-get install -y \
        python3-pip \
        # python3-pyqt5 \
        qtwebengine5-dev \
        qtwebengine5-dev-tools \
        # python3-pyqt5.qtwebengine \
        docker.io 


# Set PyQt license acceptance for noninteractive builds
ENV PYQT_GPL_ACCEPT=yes

# update pip
RUN pip install --upgrade pip

RUN pip install \
    pyqt5 --config-settings --confirm-license= --verbose

RUN pip install \
    --no-cache-dir \
    --verbose \
    -r mowbot_legacy_gui/requirements.txt

# Set the working directory
WORKDIR /mowbot_legacy_gui

# Copy the rest of the application code into the container
COPY app /mowbot_legacy_gui/app


# Create entrypoint
COPY docker/etc/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh


ENTRYPOINT ["/entrypoint.sh"]
CMD ["/bin/bash"]





        
         