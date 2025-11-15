# Mini InSAR Pipeline v2

A reproducible, Dockerized Mini InSAR Pipeline that:
- downloads two Sentinel-1 scenes from the Alaska Satellite Facility (ASF) for an AOI & time window,
- runs an ESA SNAP processing graph (coregistration → interferogram → filtering),
- converts results to GeoTIFFs,
- produces a simple visualization (displacement map) and a short report.

This is a minimum viable InSAR pipeline, intended to demonstrate phase-based displacement output.

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

    *   **Download ESA SNAP Installer**: Before building, you need to manually download the ESA SNAP 13.0.0 "All Toolboxes" **Linux 64-bit** installer (`.sh` file) from [https://step.esa.int/main/download/snap-download/](https://step.esa.int/main/download/snap-download/). Place this `.sh` file directly into the `mini-insar-pipeline` directory (the same directory as the `Dockerfile`). **Do NOT download the Windows installer (.exe) as it will not work within the Linux-based Docker container.**

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
*   **Performance**: SNAP processing is CPU and I/O intensive. It benefits from >8GB RAM and multiple cores. A local machine is sufficient for small Areas of Interest (AOIs), but larger-scale processing would require HPC resources. **Note that this pipeline is configured for CPU-only processing. While SNAP can utilize GPUs for certain operations, this setup does not require or configure GPU acceleration, which would add significant complexity.**

### Learning Points for HPC/Geospatial Roles

This project, especially the troubleshooting process, offers valuable insights for those interested in High-Performance Computing (HPC) or geospatial roles:

*   **Resource Management (Disk I/O, CPU/RAM)**: Understanding how to manage computational resources, especially disk space and RAM, is fundamental. A common real-world problem is encountering I/O errors (`[Errno 5]`) due to full disk space, or processes being `Killed` due to insufficient RAM. This often happens with large virtual disks (WSL2/Docker) or memory-intensive scientific applications. Visual tools like **WinDirStat** are invaluable for diagnosing disk space. Learning to use system commands (e.g., `wsl --shutdown`, `Optimize-VHD` in PowerShell) to safely shrink virtual disks, and configuring Docker Desktop's memory allocation, are critical skills in any data-intensive environment.
*   **Environment & Dependency Management (Docker, `Dockerfile`)**: Ensuring a consistent and reproducible environment across different systems (e.g., local machine vs. cloud cluster) is crucial. Dockerizing the pipeline helps manage complex dependencies like ESA SNAP.
*   **Software Versioning & Compatibility (SNAP Graph XML)**: Software versions can introduce breaking changes (e.g., the `insar_graph.xml` syntax error). Debugging these compatibility issues and adapting configurations is a key skill.
*   **Command-Line Proficiency**: Most HPC and geospatial processing tasks rely heavily on command-line tools (e.g., `docker-compose`, `gpt`, `python` scripts, `df`, `wmic`).
*   **Troubleshooting Mindset**: The iterative process of identifying errors, hypothesizing causes, testing solutions, and documenting findings is central to any technical role.

### Troubleshooting Experience from a Contributor

When I first ran this pipeline, I encountered various errors and found it very challenging. Therefore, I would like to share what I learned: this debugging journey is a very normal, everyday process.

Tackling these problems is exactly what professional researchers and engineers do daily. The errors I faced were the kind of issues they resolve every day.

*   Simple input mistakes in file paths that are easy to overlook.
*   Syntax issues in the graph XML file that required updates to match the software version.
*   Insufficient disk space that needed cleanup.

With each error I resolved, I felt I was steadily moving forward. This trial-and-error process is not a sign of failure. Rather, it is an essential and valuable experience in the field of actual scientific and technical computing. So, if you encounter errors, it is a sign that you are on the right track.