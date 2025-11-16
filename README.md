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
- [HPC Support Case Study (English)](./mini-insar-pipeline/HPC_SUPPORT_CASE_STUDY_EN.md)

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
*   **Performance**: SNAP processing is CPU and I/O intensive. It benefits from >8GB RAM and multiple cores. A local machine is sufficient for small Areas of Interest (AOIs), but larger-scale processing would require HPC resources. **By default, this pipeline is configured for CPU-based processing. However, it also supports GPU acceleration for compatible NVIDIA GPUs, which can significantly speed up certain processing steps. Enabling GPU support is an advanced, experimental feature. For large datasets, processing without a GPU can be time-consuming.**

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

This pipeline is ready for GPU acceleration with compatible NVIDIA GPUs, which can significantly improve performance. By default, processing is CPU-based. Follow these steps to enable GPU support.

### 1. Host System Setup (for WSL2 Users)

If you are running Docker on Windows with a WSL2 backend, your host system must be configured to pass the GPU to Docker containers.

- **Follow the guide:** A detailed, step-by-step guide for setting up the NVIDIA Container Toolkit on WSL2 is available in this repository. Please follow it carefully:
  - **[WSL2 GPU Setup Guide](./docs/WSL_GPU_SETUP.md)**

This involves installing the NVIDIA Container Toolkit in your WSL2 distribution and configuring the Docker daemon.

### 2. Docker Configuration

The project is already configured to utilize the GPU.

- **`Dockerfile`**: The `Dockerfile` (`mini-insar-pipeline/Dockerfile`) uses an `nvidia/cuda` base image, which includes the necessary CUDA libraries. **No changes are needed.**

- **`docker-compose.yml`**: The `docker-compose.yml` file (`mini-insar-pipeline/docker-compose.yml`) is configured to request GPU access using the `gpus: all` key. This is the modern and recommended way to assign GPUs.

  ```yaml
  services:
    insar:
      build: .
      # ... other settings
      gpus: all
  ```
  **No changes are needed if your file already looks like this.**

### 3. Build and Run

After ensuring your host system and configuration files are set up correctly, build and run the container.

```bash
cd mini-insar-pipeline
docker-compose build
docker-compose run --rm insar /bin/bash
```

### 4. Verify GPU Access

Once inside the container, you can verify that the GPU is accessible by running:

```bash
nvidia-smi
```

If successful, you will see the `nvidia-smi` output, showing your GPU and the CUDA version. If you see an error like `command not found` or `NVIDIA-SMI has failed`, please refer to the **GPU Not Detected** section in the [TROUBLESHOOTING.md](./mini-insar-pipeline/TROUBLESHOOTING.md) guide.