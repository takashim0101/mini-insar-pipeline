# Use a CUDA-enabled base image from NVIDIA for GPU acceleration.
FROM nvidia/cuda:11.8.0-base-ubuntu18.04

# Set environment variables for non-interactive installation and define SNAP_HOME.
ENV DEBIAN_FRONTEND=noninteractive
ENV SNAP_HOME=/opt/snap
# Add SNAP's binary directory to the PATH for easy access to tools like 'gpt'.
ENV PATH=$PATH:$SNAP_HOME/bin

# Install necessary system dependencies:
# - wget: To download the ESA SNAP installer.
# - unzip, tar: For extracting archives.
# - fontconfig: Addresses potential font-related issues in headless environments.
# - openjdk-11-jdk: ESA SNAP is a Java application, so a Java Development Kit is required.
# - git: For cloning jpy source (if needed, but hopefully not with Python 3.6)
# - python3-dev: For Python headers (for snappy-conf)
# - build-essential: For compiling (for snappy-conf)
# - python3-pip: For installing Python packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    wget \
    unzip \
    tar \
    fontconfig \
    openjdk-11-jdk \
    git \
    python3-dev \
    build-essential \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip for Python 3.6 (which should be default python3 on Ubuntu 18.04)
RUN python3 -m pip install --upgrade pip

# Download and install ESA SNAP 9.0.0:
# - WORKDIR /tmp: Change to a temporary directory for downloading.
# - wget ... -O: Download the ESA SNAP 9.0.0 installer for Unix.
# - chmod +x: Make the installer executable.
# - ./esa-snap... -q -dir $SNAP_HOME: Run the installer in quiet (silent) mode (-q)
#   and specify the installation directory (-dir).
# - rm: Clean up the installer file after installation.
WORKDIR /tmp
RUN wget https://download.esa.int/step/snap/9.0/installers/esa-snap_all_unix_9_0_0.sh -O esa-snap_all_unix_9_0_0.sh && \
    chmod +x esa-snap_all_unix_9_0_0.sh && \
    ./esa-snap_all_unix_9_0_0.sh -q -dir $SNAP_HOME && \
    rm esa-snap_all_unix_9_0_0.sh

# Configure Snappy (SNAP's Python API integration):
# Use python3 explicitly for snappy-conf (which should be 3.6 on Ubuntu 18.04)
RUN mkdir -p $SNAP_HOME/snap-python && \
    $SNAP_HOME/bin/snappy-conf /usr/bin/python3 $SNAP_HOME/snap-python && \
    echo "export PYTHONPATH=$PYTHONPATH:$SNAP_HOME/snap-python" >> /etc/bash.bashrc

# Update SNAP modules:
# This step ensures all installed SNAP modules are up-to-date.
# - --nosplash: Prevents the splash screen from appearing.
# - --nogui: Runs SNAP in headless mode without a graphical user interface.
# - --modules --update-all: Commands SNAP to update all available modules.
RUN $SNAP_HOME/bin/snap --nosplash --nogui --modules --update-all

# Set JAVA_HOME (assuming openjdk-11-jdk installs here)
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64

# Install Python deps (using default python3, which is 3.6)
COPY requirements.txt /tmp/requirements.txt
RUN python3 -m pip install --no-cache-dir -r /tmp/requirements.txt

# Copy project files
WORKDIR /opt/project
COPY . /opt/project
RUN chmod +x /opt/project/scripts/*.py

# Set the default command to /bin/bash for easy interaction with the container.
CMD ["/bin/bash"]
