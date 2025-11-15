# Stage 1: Build our final image
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    python3 python3-pip python3-venv git \
    build-essential openjdk-11-jre-headless gdal-bin libgdal-dev \
    curl wget iputils-ping unzip \
    && rm -rf /var/lib/apt/lists/*

# Install SNAP 13.0.0 manually
ENV SNAP_VERSION=13.0.0
ENV SNAP_INSTALL_DIR=/opt/snap

COPY esa-snap_all_linux-13.0.0.sh /tmp/esa-snap_all_linux-13.0.0.sh
RUN mkdir -p ${SNAP_INSTALL_DIR} && \
    chmod +x /tmp/esa-snap_all_linux-13.0.0.sh && \
    /tmp/esa-snap_all_linux-13.0.0.sh -q -dir ${SNAP_INSTALL_DIR} && \
    rm /tmp/esa-snap_all_linux-13.0.0.sh

# Set SNAP environment variables
ENV PATH="${SNAP_INSTALL_DIR}/bin:${PATH}"
# Assuming openjdk-11-jre-headless installs here
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64

# Install Python deps
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

# Copy project files
WORKDIR /opt/project
COPY . /opt/project
RUN chmod +x /opt/project/scripts/*.py

CMD ["/bin/bash"]