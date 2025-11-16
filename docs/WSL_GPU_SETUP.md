# WSL2 GPU Setup for NVIDIA Container Toolkit (Ubuntu 24.04)

This document provides detailed steps to configure your WSL2 Ubuntu 24.04 environment to enable GPU acceleration for Docker containers using the NVIDIA Container Toolkit. This is an advanced and experimental configuration for the Mini InSAR Pipeline project.

**Prerequisites:**
*   An NVIDIA GPU on your host machine with appropriate drivers installed (verified by `nvidia-smi`).
*   Docker Desktop installed and running on your Windows host.
*   Ubuntu 24.04 LTS installed as a WSL2 distribution.

## 1. Install NVIDIA Container Toolkit

Follow these steps within your WSL2 Ubuntu 24.04 terminal:

```bash
# Add NVIDIA GPG key
sudo wget -qO /etc/apt/keyrings/nvidia-container-toolkit-keyring.gpg https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit-keyring.gpg

# Add the NVIDIA Container Toolkit repository
distribution=$(. /etc/os-release;echo $ID$VERSION_ID) \
    && sudo wget -qO /etc/apt/sources.list.d/nvidia-container-toolkit.list https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list \
    && sudo sed -i -e 's#deb https://#deb [signed-by=/etc/apt/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' /etc/apt/sources.list.d/nvidia-container-toolkit.list

# Update the apt package list
sudo apt update

# Install the NVIDIA Container Toolkit
sudo apt install -y nvidia-container-toolkit
```

## 2. Configure Docker to use the NVIDIA Container Runtime

This step modifies the Docker daemon configuration to enable GPU access.

```bash
# Configure the Docker daemon
sudo nvidia-ctk runtime configure --runtime=docker

# Restart the Docker service (or restart Docker Desktop on Windows)
# If systemctl is not available in your WSL2, restart Docker Desktop manually.
sudo systemctl restart docker
```

## 3. Verify Installation

Run a CUDA-enabled Docker image to confirm GPU access from within a container.

```bash
docker run --rm --gpus all nvidia/cuda:12.3.0-runtime-ubuntu22.04 nvidia-smi
```
You should see output similar to your host's `nvidia-smi` command, indicating successful GPU passthrough.

## 4. WSL2 Memory Configuration (Optional but Recommended)

For memory-intensive tasks like InSAR processing, it's crucial to allocate sufficient memory to WSL2.

Create or edit a file named `.wslconfig` in your Windows user profile directory (`%USERPROFILE%`, typically `C:\Users\<YourUsername>`).

```ini
[wsl2]
memory=16GB       # Allocate 16GB of RAM to WSL2 (adjust based on your system)
processors=6      # Allocate 6 CPU cores to WSL2 (adjust based on your system)
swap=16GB         # Allocate 16GB of swap space
localhostForwarding=true
```
After saving `.wslconfig`, you must shut down and restart WSL for the changes to take effect. Open PowerShell or Command Prompt (not within WSL) and run: `wsl --shutdown`. Then, restart your Docker Desktop application.
