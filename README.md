# Mini InSAR Pipeline v2

A reproducible, Dockerized Mini InSAR Pipeline that:
- downloads two Sentinel-1 scenes from the Alaska Satellite Facility (ASF) for an AOI & time window,
- runs an ESA SNAP processing graph (coregistration → interferogram → filtering),
- converts results to GeoTIFFs,
- produces a simple visualization (displacement map) and a short report.

This is a minimum viable InSAR pipeline, intended to demonstrate phase-based displacement output.

This project demonstrates how advanced SAR workflows can be implemented by a single engineer, making satellite-based deformation monitoring reproducible, automated, and ready for integration into national-scale geospatial systems.

Although this pipeline was built end-to-end by one person for demonstration purposes, the architecture is intentionally modular, maintainable, and suited for team-based development and operational environments.

# What this project demonstrates

## 🟦 Full Pipeline Engineering (Single-person architecture)
- End-to-end design of an operational InSAR pipeline
- Automated data ingest → preprocessing → interferogram → phase → displacement output
- Fully reproducible Dockerised environment

## 🟦 GeoAI & SAR Processing
- Sentinel-1 SAR handling, InSAR concepts, geospatial formats (GeoTIFF, VRT, GeoJSON)
- Python-based workflow automation (SNAP, Snappy, custom tooling)
- HPC-aware processing (I/O optimization, system resource tuning)

## 🟦 Infrastructure & Systems Engineering
- Containerization (Dockerfile, docker-compose)
- Multi-language stack debugging (Python, Java, C-extensions, Linux)
- Infrastructure as Code principles for scientific workflows

## 🟦 Documentation & Knowledge Transfer
- Clear troubleshooting guides, reproducible instructions, technical notes

## How to Run

1.  **Set Earthdata Login Credentials**:
    Data download is handled by `asf-search`, which requires a NASA Earthdata Login account.

    *   **Create an Account**: If you don't have one, [register for a free NASA Earthdata account](https://urs.earthdata.nasa.gov/users/new).
    *   **Set Environment Variables**: Set your credentials as environment variables in your **host shell** *before* running `docker-compose`.

    *   **For Bash/Zsh (Linux/macOS):**
        ```bash
        export EARTHDATA_USERNAME=your_earthdata_username
        export EARTHDATA_PASSWORD=your_earthdata_password
        ```
    *   **For PowerShell (Windows):**
        ```powershell
        $env:EARTHDATA_USERNAME="your_earthdata_username"
        $env:EARTHDATA_PASSWORD="your_earthdata_password"
        ```
    *   *Replace `your_earthdata_username` and `your_earthdata_password` with your actual credentials.*

2.  **Windows/WSL2 Users: Configure Docker Memory (Crucial for InSAR Processing)**

    InSAR processing is memory-intensive. If you are running Docker Desktop on Windows with the WSL2 backend, it is crucial to allocate sufficient memory to WSL2 to prevent out-of-memory errors during SNAP processing.

    1.  **Create or Edit `.wslconfig`**:
        Create or edit a file named `.wslconfig` in your Windows user profile directory (`%USERPROFILE%`, typically `C:\Users\<YourUsername>\`).

    2.  **Add Configuration**:
        Add the following content to the `.wslconfig` file. Adjust `memory` and `processors` based on your system's resources, but ensure `memory` is at least 16GB for this pipeline.

        ```ini
        [wsl2]
        memory=16GB       # Allocate 16GB of RAM to WSL2
        processors=6      # Allocate 6 CPU cores to WSL2
        swap=16GB         # Allocate 16GB of swap space
        localhostForwarding=true
        ```

    3.  **Restart WSL**:
        After saving `.wslconfig`, you must shut down and restart WSL for the changes to take effect. Open PowerShell or Command Prompt (not within WSL) and run:

        ```powershell
        wsl --shutdown
        ```
        Then, restart your Docker Desktop application. You can verify the allocated memory by running `free -h` inside your WSL terminal or `docker info | grep "Total Memory"` after Docker Desktop has restarted.

3.  **Build and Run the Container**:
    **Important:** All `docker-compose` commands must be run from within the `mini-insar-pipeline` directory.

    *   **ESA SNAP Installer**: Due to issues with direct download of ESA SNAP 13.0.0, the `Dockerfile` is now configured to automatically download ESA SNAP 9.0.0 "All Toolboxes" **Linux 64-bit** installer (`.sh` file) from the official STEP website during the Docker image build process. Manual download and placement of the installer are no longer required.

    First, navigate to the correct directory:
    ```bash
    cd mini-insar-pipeline
    ```

    Then, build the image (to install the new Python dependencies) and run the container:
    ```bash
    docker-compose build
    docker-compose run --rm insar /bin/bash
    ```

4.  **Inside the Container: Run the Pipeline**:
    Once you are inside the Docker container's bash shell (indicated by a prompt like `root@...:/opt/project#`), you can run the pipeline steps.

    *   **Download Data**:
        You will need an `aoi.geojson` file defining your Area of Interest. An example `aoi.geojson` for Ashburton, NZ, has been provided in the project root. The `download_data.py` script will select two scenes closest to the specified start and end dates, which is ideal for pre/post-event InSAR comparison.

        *Context: The Ashburton flood in 2021 occurred between May 29th and May 31st [1].*

        ```bash
        # Usage: python3 /path/to/script.py aoi.geojson YYYYMMDD YYYYMMDD /output/dir
        # Example for Ashburton pre/post-flood comparison (May 11, 2021 and June 4, 2021)
        python3 /opt/scripts/download_data.py /opt/project/aoi.geojson 20210511 20210604 /opt/data/SAFE
        ```

---
[1] Ashburton District Council. (2021). *Canterbury floods 2021*. Retrieved from https://www.ashburtondc.govt.nz/our-district/emergency-management/canterbury-floods-2021

    *   **Run SNAP GPT Pipeline**:
        Adjust the `--in1` and `--in2` paths to match the actual `.SAFE` folder names downloaded in the previous step. You can find these names in the `/opt/data/SAFE` directory inside the container.

        ```bash
        # Usage: python3 /path/to/script.py /path/to/graph.xml --in1 /path/to/master.SAFE --in2 /path/to/slave.SAFE --out /output/dir
        python3 /opt/scripts/run_gpt.py /opt/graphs/insar_graph.xml --in1 /opt/data/SAFE/S1A_... --in2 /opt/data/SAFE/S1B_... --out /opt/data/out
        ```

    *   **Convert, Visualize, and Report**:
        ```bash
        python3 /opt/scripts/convert_vrt_to_tif.py /opt/data/out
        python3 /opt/scripts/generate_report.py /opt/data/out
        ```

## Validation & Expected Outputs

After running the pipeline, you should find the following in the `mini-insar-pipeline/data/out/` directory:

*   `insar_filtered.tif`: The filtered interferogram (phase-filtered).
*   `insar_filtered.tif.png`: A visualization of the interferogram.
*   `insar_report.txt`: A short textual report with output paths.

### Sanity Checks
*   The interferogram should show coherent fringes over non-vegetated areas (coastal/urban).
*   If the interferogram is noisy (low coherence), try picking acquisition dates that are closer together.
*   If outputs are empty or you encounter an error, check the SNAP GPT logs printed to the console. Common issues include incorrect `.SAFE` paths or a missing manifest file.

## Troubleshooting

For common issues and their resolutions, please refer to the [TROUBLESHOOTING.md](mini-insar-pipeline/TROUBLESHOOTING.md) file.

## Code Licensing

This pipeline's code is provided as-is. If you intend to publish or distribute this code, it is highly recommended to choose and include an appropriate open-source license (e.g., MIT, Apache 2.0) in your repository. This clarifies how others can use, modify, and distribute your code.

## Data Licensing

The Sentinel-1 data downloaded via this pipeline is sourced from the Alaska Satellite Facility (ASF). While ASF data is generally publicly funded and available, specific usage policies, especially concerning commercial applications, can vary by dataset.

**It is crucial for users to consult the End User License Agreements (EULAs) associated with each specific data collection to determine the exact commercial use policy and any other restrictions.**

## Notes, Limitations, and Next Steps

*   **SNAP / SNAPHU**: For full phase unwrapping, you would typically use `snaphu` (usually a separate installation) or SNAP’s Unwrapping operator. This may require extra packages and configuration.
*   **SBAS / PS-InSAR**: This mini-pipeline handles a single interferogram (DInSAR). Time-series analysis (SBAS/PS) requires additional tooling (e.g., MintPy, StaMPS) and significantly more computation.
*   **HPC Scaling**: For production use, the `gpt` call can be wrapped inside job arrays (e.g., SLURM) or scaled using services like AWS Batch / Fargate.
*   **Performance**: SNAP processing is CPU and I/O intensive. It benefits from >8GB RAM and multiple cores. A local machine is sufficient for small Areas of Interest (AOIs), but larger-scale processing would require HPC resources. **Note that this pipeline is configured for CPU-only processing. While SNAP can utilize GPUs for certain operations, this setup does not require or configure GPU acceleration, which would add significant complexity. For large datasets, processing without a GPU can be significantly time-consuming.**

### Learning Points for HPC/Geospatial Roles

This project, especially the troubleshooting process, offers valuable insights for those interested in High-Performance Computing (HPC) or geospatial roles, directly aligning with skills sought in roles like a Cloud Infrastructure Engineer. It demonstrates practical experience in:

*   **Cloud Infrastructure & DevOps (AWS, Docker, IaC, GitHub Actions, Serverless, Kubernetes)**:
    *   **Demonstrated Skill**: Experience in defining and managing infrastructure (Docker containers, dependencies, resource allocation) through code (`Dockerfile`, `docker-compose.yml`). This ensures consistent and reproducible environments across different systems, a core principle of IaC. The iterative process of building, testing, and refining the Docker image reflects DevOps practices. Familiarity with containerization (Docker) and orchestration concepts (Kubernetes, AWS EKS) is also highlighted.
    *   **Relevance to Roles**: This skill is highly relevant to roles requiring expertise in cloud infrastructure, DevOps practices, and managing deployments in environments like AWS. It demonstrates experience with Infrastructure as Code (IaC) using tools like Docker and an understanding of cloud-based service architectures, including serverless and container orchestration (e.g., Kubernetes, AWS EKS).

*   **Programming & Development (Python Scripting, Automation, Data Processing)**:
    *   **Demonstrated Skill**: Automating complex scientific workflows (InSAR processing) using Python scripting and containerization. This involves software development practices that support data processing, scripting, and automation.
    *   **Relevance to Roles**: This skill is crucial for roles involving software development, particularly in data processing, scripting, and automation, often utilizing languages like Python.

*   **Geospatial Technology (Data Formats, Processing Workflows, GDAL, STAC)**:
    *   **Demonstrated Skill**: Practical knowledge of InSAR workflows, ESA SNAP, and processing pipelines within a containerized environment. This involves handling specialized geospatial data and tools, including the use of GDAL for data conversion and understanding of metadata standards like STAC.
    *   **Relevance to Roles**: This skill is essential for roles focused on geospatial data, including processing workflows, spatial analysis, and the delivery of essential geospatial products, often involving tools like GDAL and standards like STAC.

*   **Resource Management & Optimization (Disk I/O, CPU/RAM, Docker Cleanup)**:
    *   **Demonstrated Skill**: Understanding how to manage computational resources, especially disk space and RAM, is fundamental. Encountering and resolving `[Errno 5]` (I/O errors) due to full disk space, or processes being `Killed` due to insufficient RAM, highlights practical experience. This includes using tools like `wsl --shutdown`, `Optimize-VHD`, and crucially, `docker system prune -a` for reclaiming significant disk space (e.g., over 18GB after multiple build attempts).
    *   **Relevance to Roles**: This skill is vital for roles involving cloud architecture, system administration, and performance optimization, where efficient resource management and problem-solving for performance issues are critical.

*   **Problem-Solving & Troubleshooting Mindset**:
    *   **Demonstrated Skill**: The iterative process of identifying errors (e.g., `404 Not Found` for SNAP installer, `gdal-config not found`, `Python configuration failed`), hypothesizing causes, testing solutions, and documenting findings is central to any technical role. This project involved debugging version mismatches, environmental inconsistencies, and dependency issues.
    *   **Relevance to Roles**: This skill is fundamental for any technical role, emphasizing a practical, outcome-driven approach to identifying, diagnosing, and resolving complex technical challenges.

*   **Communication and Documentation**:
    *   **Demonstrated Skill**: The proactive attitude to summarize acquired knowledge into clear documentation (`README.md`, `TROUBLESHOOTING.md`) for the benefit of other technical professionals and the community. This includes translating technical concepts for both general and technical audiences.
    *   **Relevance to Roles**: This skill is crucial for effectively conveying technical information to diverse audiences, contributing to knowledge sharing, user training, and overall project clarity.

### Troubleshooting Experience from a Contributor

When I first ran this pipeline, I encountered various errors and found it very challenging. Therefore, I would like to share what I learned: this debugging journey is a very normal, everyday process.

Tackling these problems is exactly what professional researchers and engineers do daily. The errors I faced were the kind of issues they resolve every day.

*   Simple input mistakes in file paths that are easy to overlook.
*   Syntax issues in the graph XML file that required updates to match the software version.
*   Insufficient disk space that needed cleanup.

With each error I resolved, I felt I was steadily moving forward. This trial-and-error process is not a sign of failure. Rather, it is an essential and valuable experience in the field of actual scientific and technical computing. So, if you encounter errors, it is a sign that you are on the right track.

## Advanced Configuration: GPU Acceleration (Experimental)

This pipeline is configured for CPU-only processing by default. While ESA SNAP can utilize GPUs for certain operations, enabling GPU acceleration adds significant complexity and is considered an advanced, experimental configuration for this project.

If you wish to attempt GPU acceleration with your NVIDIA GPU, follow these general steps:

1.  **Verify Host System Prerequisites:**
    *   Ensure your NVIDIA GPU drivers are correctly installed on your host system (e.g., confirmed by `nvidia-smi` output).
    *   Ensure Docker Desktop (or Docker Engine) is installed and running.

2.  **Install NVIDIA Container Toolkit (inside WSL2 Ubuntu):**
    Before installing the toolkit, it's good practice to upgrade your system's packages to their latest versions to ensure compatibility and stability.
    ```bash
    sudo apt update
    sudo apt upgrade -y
    ```
    This toolkit allows Docker to access your host's NVIDIA GPUs. Run these commands inside your WSL2 Ubuntu terminal:
    ```bash
    sudo apt install -y curl gnupg software-properties-common
    curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor | sudo tee /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg > /dev/null
    # Add the NVIDIA Container Toolkit repository
    curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
    sudo apt update
    sudo apt install -y nvidia-container-toolkit
    ```
    Then, configure Docker to use the NVIDIA runtime by editing `/etc/docker/daemon.json`:
    ```bash
    sudo nano /etc/docker/daemon.json
    ```
    Add/modify the content:
    ```json
    {
        "default-runtime": "nvidia",
        "runtimes": {
            "nvidia": {
                "path": "/usr/bin/nvidia-container-runtime",
                "runtimeArgs": []
            }
        }
    }
    ```
    Restart Docker (e.g., `sudo systemctl restart docker` or restart Docker Desktop).

3.  **Modify `docker-compose.yml`:**
    Add a `deploy` section to your `insar` service to specify GPU resources. Locate the `insar` service and add the following:
    ```yaml
        deploy:
          resources:
            reservations:
              devices:
                - driver: nvidia
                  count: all # or 1
                  capabilities: [gpu]
    ```

4.  **Modify `Dockerfile` (Advanced & SNAP-Specific):**
    This step involves updating the `Dockerfile` to include CUDA support and a more robust SNAP installation process. The previous `Dockerfile` was based on `ubuntu:22.04` and manually copied the SNAP installer. The updated `Dockerfile` uses an `nvidia/cuda` base image and downloads SNAP directly.

    Here is the updated `Dockerfile` content:

    ```dockerfile
    # Use a CUDA-enabled base image from NVIDIA for GPU acceleration.
    FROM nvidia/cuda:11.8.0-base-ubuntu22.04

    # Set environment variables for non-interactive installation and define SNAP_HOME.
    ENV DEBIAN_FRONTEND=noninteractive
    ENV SNAP_HOME=/opt/snap
    # Add SNAP's binary directory to the PATH for easy access to tools like 'gpt'.
    ENV PATH=$PATH:$SNAP_HOME/bin

    # Install necessary system dependencies:
    # - wget: To download the ESA SNAP installer.
    # - unzip, tar: For extracting archives.
    # - fontconfig: Addresses potential font-related issues in headless environments.
    # - python3, python3-pip: For Snappy (SNAP's Python API) integration.
    # - openjdk-11-jdk: ESA SNAP is a Java application, so a Java Development Kit is required.
    RUN apt-get update && \
        apt-get install -y --no-install-recommends \
        wget \
        unzip \
        tar \
        fontconfig \
        python3 \
        python3-pip \
        openjdk-11-jdk \
        && rm -rf /var/lib/apt/lists/*

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
    # - mkdir -p: Create a directory for the Snappy module.
    # - $SNAP_HOME/bin/snappy-conf: Run the Snappy configuration tool.
    #   It links the specified Python interpreter (python3) with SNAP and generates
    #   the 'snappy' module in the target directory.
    # - echo ... >> /etc/bash.bashrc: Add the Snappy module's path to PYTHONPATH
    #   so Python can find it. This makes it available for all users.
    RUN mkdir -p $SNAP_HOME/snap-python && \
        $SNAP_HOME/bin/snappy-conf python3 $SNAP_HOME/snap-python && \
        echo "export PYTHONPATH=$PYTHONPATH:$SNAP_HOME/snap-python" >> /etc/bash.bashrc

    # Update SNAP modules:
    # This step ensures all installed SNAP modules are up-to-date.
    # - --nosplash: Prevents the splash screen from appearing.
    # - --nogui: Runs SNAP in headless mode without a graphical user interface.
    # - --modules --update-all: Commands SNAP to update all available modules.
    RUN $SNAP_HOME/bin/snap --nosplash --nogui --modules --update-all

    # Set JAVA_HOME (assuming openjdk-11-jdk installs here)
    ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64

    # Install Python deps
    COPY requirements.txt /tmp/requirements.txt
    RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

    # Copy project files
    WORKDIR /opt/project
    COPY . /opt/project
    RUN chmod +x /opt/project/scripts/*.py

    # Set the default command to /bin/bash for easy interaction with the container.
    CMD ["/bin/bash"]
    ```

    **Note:** This `Dockerfile` now uses ESA SNAP 9.0.0 due to direct download issues with version 13.0.0. The installer is automatically downloaded during the Docker image build process.

5.  **Rebuild and Run:**
    After all modifications, rebuild your Docker image and run the container:
    ```bash
    cd mini-insar-pipeline
    docker-compose build
    docker-compose run --rm insar /bin/bash
    ```
    Verify GPU access inside the container by running `nvidia-smi`.