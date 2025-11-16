# Mini InSAR Pipeline - Troubleshooting Guide

This document outlines common issues encountered during the setup and execution of the Mini InSAR Pipeline, along with their resolutions.

## 1. Authentication Failed (Earthdata Login / ASF)

**Problem:** The `download_data.py` script fails with an "Authentication failed. Please check your Earthdata Login credentials. Details: Username or password is incorrect" error.

**Initial Cause:** The original pipeline used the deprecated Copernicus Open Access Hub API.

**Resolution Steps:**

1.  **Migrated Data Source:** The pipeline was updated to use the Alaska Satellite Facility (ASF) for Sentinel-1 data acquisition, leveraging the `asf-search` Python library.
2.  **Earthdata Login Credentials:**
    *   Ensure you have a valid NASA Earthdata Login account.
    *   Verify your username and password by logging into the [Earthdata Login website](https://urs.earthdata.nasa.gov/) directly.
    *   Ensure the "Alaska Satellite Facility Data Access" application is authorized in your [Earthdata Login profile](https://urs.earthdata.nasa.gov/profile) under "Approved Applications".
3.  **Environment Variable Setup:**
    *   Ensure `EARTHDATA_USERNAME` and `EARTHDATA_PASSWORD` are correctly set as environment variables in your host shell *before* running `docker-compose`.
4.  **Password Special Characters:**
    *   If your Earthdata password contains special characters (e.g., `!`), it might cause issues with `asf-search` or the underlying environment. While ASF requires a special character, consider temporarily changing your password to use a less problematic one (e.g., `@` or `#` instead of `!`) if the issue persists.
5.  **Network Connectivity (from within Docker):**
    *   Verify that the Docker container has internet access and can reach Earthdata's URS and ASF's API endpoints.
    *   Inside the container, run: `curl -v https://urs.earthdata.nasa.gov/` and `curl -v https://api.daac.asf.alaska.edu/`. Both should return `HTTP/1.1 200 OK`.
6.  **`asf-search` Debugging:**
    *   If the error persists, run `asf-search` authentication directly in a Python interpreter inside the container with debug logging enabled to get more detailed error messages.

## 2. `KeyError: 'features'` when parsing `aoi.geojson`

**Problem:** The `download_data.py` script fails with `KeyError: 'features'` when trying to read the `aoi.geojson` file.

**Cause:** The `aoi.geojson` file is formatted as a direct GeoJSON `Polygon` geometry object, but the script was initially expecting a GeoJSON `FeatureCollection` (which contains a top-level `'features'` key).

**Resolution:** The `download_data.py` script was modified to correctly parse both `FeatureCollection` and direct `Geometry` (like `Polygon`) GeoJSON formats.

## 3. `geo_search() got an unexpected keyword argument 'session'`

**Problem:** The `download_data.py` script fails with `ERROR: ASF search failed. Details: geo_search() got an unexpected keyword argument 'session'`.

**Cause:** The `asf_search.geo_search()` function does not accept a `session` argument for authentication; it handles authentication implicitly after `asf.ASFSession().auth_with_creds()` has been called.

**Resolution:** The `session=session` argument was removed from the `asf.geo_search()` call in `download_data.py`.

## 4. SNAP GPT Fails with "Specified 'file' [...] does not exist." (Missing .SAFE directory)

**Problem:** The `run_gpt.py` script fails with an error message like `Error: [NodeId: Read-Slave] Specified 'file' [/opt/data/SAFE/S1A_...SAFE] does not exist.`

**Cause:** The `download_data.py` script downloads Sentinel-1 data as `.zip` archives. However, the SNAP `Read` operator in the processing graph expects the unzipped `.SAFE` directories as input, not the `.zip` files. The error occurs because the `.SAFE` directory corresponding to the downloaded `.zip` file is not present.

**Resolution:** The `download_data.py` script needs to be modified to automatically unzip the downloaded `.zip` files after successful download.

1.  **Update `Dockerfile`:** Ensure the `unzip` utility is installed in the Docker image. Add `unzip` to the `apt-get install` command in the `Dockerfile`.
2.  **Update `download_data.py`:** Modify the `download_data.py` script to include logic for unzipping each downloaded `.zip` file into its corresponding `.SAFE` directory and then removing the `.zip` file.
3.  **Rebuild Docker Image:** After modifying `Dockerfile` and `download_data.py`, you must rebuild the Docker image using `docker-compose build`.
4.  **Re-run Pipeline:** Then, re-run the pipeline starting from the `download_data.py` step.

## 5. SNAP GPT Command Fails with `UnknownFieldException`

**Problem:** The `run_gpt.py` script fails with an error similar to `com.thoughtworks.xstream.converters.reflection.AbstractReflectionConverter$UnknownFieldException: No such field org.esa.snap.core.gpf.graph.Graph.connection`.

**Cause:** This error indicates a version mismatch between the SNAP Graph XML file (`insar_graph.xml`) and the version of SNAP being used (e.g., SNAP 13.0.0). The XML syntax for defining processing graphs changed in newer versions of SNAP. Specifically, the `<connection>` tag used to link nodes is no longer valid.

**Resolution:** The `insar_graph.xml` file must be updated to use the modern graph syntax.

1.  **Remove `<connection>` Tags:** All `<connection from="..." to="..."/>` tags must be removed from the graph file.
2.  **Use `<sources>` Tags:** Each node that receives input from a previous node must have a `<sources>` block. Inside this block, you specify the source node using a `<sourceProduct>` tag with a `refid` attribute pointing to the ID of the source node.

    *   **Example (Old Syntax):**
        ```xml
        <node id="NodeA">...</node>
        <node id="NodeB">...</node>
        <connection from="NodeA" to="NodeB"/>
        ```

    *   **Example (New Syntax):**
        ```xml
        <node id="NodeA">...</node>
        <node id="NodeB">
          <operator>...</operator>
          <sources>
            <sourceProduct refid="NodeA"/>
          </sources>
          ...
        </node>
        ```

3.  **Update the Graph:** The `insar_graph.xml` was updated to reflect this new syntax, resolving the incompatibility.

## 6. `[Errno 5] Input/output error` during unzipping

**Problem:** The `download_data.py` script fails during the unzip step with `ERROR: Download or unzipping failed. Details: [Errno 5] Input/output error`.

**Cause:** This is a low-level OS error indicating a problem with file reading or writing. The most common cause in this context is a **lack of disk space**. The Docker volume mount maps the container's `/opt/data` directory to a directory on your host machine (e.g., your C: drive). If the host machine's drive is full, the container cannot write the large, unzipped `.SAFE` directories, resulting in an I/O error.

**Resolution:**

1.  **Diagnose:**
    *   Run `df -h` inside the container. Check the `Use%` and `Avail` columns for the filesystem mounted on `/opt/data`. If `Use%` is at or near 100% and `Avail` is near zero, you have a disk space issue.
    *   On your **Windows host machine**, you can check the free space of your drives using the command prompt or PowerShell:
        ```
        wmic logicaldisk get caption,freespace,size
        ```
        This will show the `FreeSpace` (in bytes) and `Size` (in bytes) for each logical disk.

    *   **For Linux/HPC environments (inside Docker or on a cluster):**
        *   `df -h`: Check overall disk space usage.
        *   `du -sh <directory>`: Check disk usage of a specific directory (e.g., `du -sh /opt/data/SAFE`).
        *   `rm <file/directory>`: Remove files or directories (use with caution!).
        *   `lfs quota -u <username> /path/to/filesystem`: (Specific to Lustre filesystems) Check user's quota.
2.  **Free Up Space:** Free up a significant amount of disk space on the corresponding drive on your host machine. For InSAR processing, having at least 10-20 GB of free space is recommended.
3.  **Re-run:** After freeing up space, exit the container and re-run the pipeline starting with `docker-compose run --rm insar /bin/bash`.

**Tip for Freeing Up Space:**
A comprehensive list of methods to free up disk space on your host machine:

### Project-Specific Data

*   Clear the contents of the `data/SAFE` and `data/out` directories.

### General Windows Cleanup

*   **Disk Cleanup Tool:** Run the built-in Windows "Disk Cleanup" utility and select "Clean up system files" to remove old Windows Update files.
*   **Uninstall Unused Apps:** Go to "Settings" > "Apps" > "Installed apps" and uninstall any software you no longer need.
*   **Disk Analysis Tools:** Use free tools like **WinDirStat** or **TreeSize Free** to visualize what is consuming your disk space. This is often the most effective way to find large, forgotten files.

### Docker Cleanup

*   The `docker system prune -a` command is an effective but aggressive way to reclaim disk space by removing all stopped containers, unused networks, and dangling images/build cache.
    *   **Real-World Example:** A recent experience demonstrated that running `docker system prune -a` successfully reclaimed over 18GB of disk space after multiple build attempts, resolving `[Errno 5]` errors caused by insufficient disk space. This command is crucial for maintaining a clean Docker environment, especially during iterative development and debugging of containerized applications.
*   For a less aggressive approach, you can use more targeted commands:
    *   `docker builder prune`: Safely removes only the build cache.
    *   `docker image prune`: Safely removes "dangling" images (images not tagged or used by any container).
    *   `docker container prune`: Removes all stopped containers.

### Advanced Windows Cleanup (Use with Caution)

For Windows users, you can also free up significant space on your C: drive by running the following command in an **administrator PowerShell or Command Prompt**:
```
Dism.exe /online /Cleanup-Image /StartComponentCleanup
```
This command cleans up the Windows Component Store, removing older versions of system components. For an even more aggressive cleanup that removes all superseded versions of every component (making it impossible to uninstall previous updates), you can use:
```
Dism.exe /online /Cleanup-Image /StartComponentCleanup /ResetBase
```

Other advanced methods to free up space on Windows:
*   **Disable Hibernation:** If you don't use hibernation, disabling it can free up significant space (equal to your RAM size). Run in **administrator PowerShell or Command Prompt**:
    ```powercfg.exe /hibernate off
```
*   **Manage System Restore Points:** Reduce the disk space allocated for system restore points or delete older ones. Search for "Create a restore point" in Windows, then configure settings.

## 7. IndentationError in download_data.py

**Problem:** The `download_data.py` script fails with an `IndentationError: unexpected indent`.

**Cause:** This is a Python syntax error caused by incorrect indentation in the script. It likely occurred during a copy-paste operation when adding new code, such as the unzipping logic.

**Resolution:** The script must be corrected to have valid Python indentation. This involves:
1.  Ensuring that `import` statements are at the top of the file with no leading whitespace.
2.  Ensuring that all code blocks (e.g., inside `try...except` blocks, `for` loops, and functions) are indented consistently (e.g., with 4 spaces per level).
3.  The script was corrected to fix the indentation of the download and unzip logic.

## 8. Killed message during processing (Out of Memory)

**Problem:** The processing script (e.g., `generate_report.py` or `run_gpt.py`) terminates abruptly with a "Killed" message, without a clear error traceback.

**Cause:** The "Killed" message typically indicates that the process ran out of available memory (RAM) and was terminated by the operating system (or Docker's resource limits). Scientific computing tasks, especially InSAR processing, are highly memory-intensive.

> **Note:** InSAR processing can take a significant amount of time (15 minutes to over an hour for a pair of full Sentinel-1 SLC scenes). A long-running process is not necessarily an error. Only investigate if the process truly hangs without any output for an extended period, or if it explicitly terminates with a "Killed" message.

**Resolution:**

1.  **Diagnose Memory Usage:**
    *   **Check Docker Container Memory:** In your host PowerShell/terminal, run `docker stats`. Observe the `MEM USAGE / LIMIT` column for your `mini_insar` container. If `MEM USAGE` is close to `LIMIT`, the container has reached its allocated memory limit.
    *   **Check Host System Memory:** Monitor your host machine's overall RAM usage using Task Manager (Windows) or Activity Monitor (macOS/Linux). High overall usage can impact Docker's available memory.

2.  **Increase Docker Desktop Memory Allocation:**
    *   If you are using Docker Desktop (Windows/macOS), you can increase the amount of RAM allocated to the Docker Engine. Go to Docker Desktop **Settings -> Resources -> Advanced**, and increase the "Memory" slider. InSAR processing can benefit from 8GB or more, with 16GB or more recommended for this pipeline.
    *   **For Windows/WSL2 Users:** If you are running Docker Desktop on Windows with the WSL2 backend, you can configure WSL2's memory allocation by creating or editing a `.wslconfig` file in your Windows user profile directory (`%USERPROFILE%`, typically `C:\Users\<YourUsername>\`). Add the following content (adjust `memory` and `processors` based on your system's resources):
        ```ini
        [wsl2]
        memory=16GB       # Allocate 16GB of RAM to WSL2
        processors=6      # Allocate 6 CPU cores to WSL2
        swap=16GB         # Allocate 16GB of swap space
        localhostForwarding=true
        ```
        After saving `.wslconfig`, you must shut down and restart WSL for the changes to take effect. Open PowerShell or Command Prompt (not within WSL) and run: `wsl --shutdown`. Then, restart your Docker Desktop application. You can verify the allocated memory by running `free -h` inside your WSL terminal or `docker info | grep "Total Memory"` after Docker Desktop has restarted.
    *   After changing settings, apply and restart Docker Desktop.

3.  **Reduce Memory Footprint (if possible):**
    *   If the issue persists, review the script's memory usage. For plotting large images, sometimes downsampling or processing in chunks can help, though this might require code modifications.
    *   Ensure no other memory-intensive applications are running on your host machine simultaneously.

4.  **Re-run:** After adjusting memory settings, re-run the pipeline steps.

## 9. SNAP GPT Fails with "Unknown element 'writeGeoCoding'"

**Problem:** The `run_gpt.py` script fails with an error message like `Error: [NodeId: WriteGTiff] Operator 'WriteOp': Unknown element 'writeGeoCoding'` or `Caused by: com.bc.ceres.binding.ConversionException: Unknown element 'writeGeoCoding'`.

**Cause:** This error indicates a version mismatch between the SNAP Graph XML file (`insar_graph.xml`) and the version of SNAP being used. Specifically, the `writeGeoCoding` element within the `Write` operator's parameters is no longer recognized or is handled differently in the current SNAP version.

**Resolution:** Remove the `writeGeoCoding` element from the `WriteGTiff` node in the `insar_graph.xml` file.

1.  **Locate `insar_graph.xml`**: The file is located at `mini-insar-pipeline/graphs/insar_graph.xml`.
2.  **Edit the file**: Open `insar_graph.xml` and find the `<node id="WriteGTiff" ...>` section.
3.  **Remove the line**: Delete the line `<writeGeoCoding>true</writeGeoCoding>` from within the `<parameters>` block of the `WriteGTiff` node.

    *   **Before:**
        ```xml
          <node id="WriteGTiff" name="Write">
            <operator>Write</operator>
            <sources>
              <sourceProduct refid="Goldstein"/>
            </sources>
            <parameters>
              <file>${output.path}/insar_filtered.tif</file>
              <formatName>GeoTIFF-BigTIFF</formatName>
              <writeGeoCoding>true</writeGeoCoding>
            </parameters>
          </node>
        ```

    *   **After:**
        ```xml
          <node id="WriteGTiff" name="Write">
            <operator>Write</operator>
            <sources>
              <sourceProduct refid="Goldstein"/>
            </sources>
            <parameters>
              <file>${output.path}/insar_filtered.tif</file>
              <formatName>GeoTIFF-BigTIFF</formatName>
            </parameters>
          </node>
        ```
4.  **Re-run the pipeline**: After saving the modified `insar_graph.xml`, re-run the `run_gpt.py` script inside the Docker container.

## 10. SNAP GPT Fails with "Source product should first be deburst"

**Problem:** The `run_gpt.py` script fails with an error message like `Error: [NodeId: Terrain-Correction] Source product should first be deburst.` or `Caused by: org.esa.snap.core.gpf.OperatorException: Source product should first be deburst.`.

**Cause:** This error occurs when a SNAP operator (like `Terrain-Correction`) that expects a debursted product receives a TOPSAR product that has not yet undergone the `TOPSAR-Deburst` operation. Sentinel-1 TOPSAR SLC products consist of multiple bursts, and many subsequent processing steps require these bursts to be merged (debursted) into a single image.

**Resolution:** Insert a `TOPSAR-Deburst` operator into the processing graph (`insar_graph.xml`) at an appropriate stage, typically after the `Interferogram` step and before any operators that require a debursted product (such as `GoldsteinPhaseFiltering` or `Terrain-Correction`).

1.  **Locate `insar_graph.xml`**: The file is located at `mini-insar-pipeline/graphs/insar_graph.xml`.
2.  **Edit the file**: Open `insar_graph.xml`.
3.  **Insert `TOPSAR-Deburst` node**: Add the `TOPSAR-Deburst` node after the `Interferogram` node.
4.  **Update subsequent node's source**: Modify the `sources` of the node immediately following the new `TOPSAR-Deburst` node (e.g., `GoldsteinPhaseFiltering`) to reference the `TOPSAR-Deburst` node.

    *   **Before (relevant part):**
        ```xml
          <node id="Interf" name="Interferogram">
            <operator>Interferogram</operator>
            <sources>
              <sourceProduct refid="CoReg"/>
            </sources>
            <parameters/>
          </node>

          <node id="Goldstein" name="GoldsteinPhaseFiltering">
            <operator>GoldsteinPhaseFiltering</operator>
            <sources>
              <sourceProduct refid="Interf"/>
            </sources>
            <parameters/>
          </node>
        ```

    *   **After (relevant part):**
        ```xml
          <node id="Interf" name="Interferogram">
            <operator>Interferogram</operator>
            <sources>
              <sourceProduct refid="CoReg"/>
            </sources>
            <parameters/>
          </node>

          <node id="Deburst" name="TOPSAR-Deburst">
            <operator>TOPSAR-Deburst</operator>
            <sources>
              <sourceProduct refid="Interf"/>
            </sources>
            <parameters>
              <selectedPolarisations>VV</selectedPolarisations>
            </parameters>
          </node>

          <node id="Goldstein" name="GoldsteinPhaseFiltering">
            <operator>GoldsteinPhaseFiltering</operator>
            <sources>
              <sourceProduct refid="Deburst"/>
            </sources>
            <parameters/>
          </node>
        ```
5.  **Re-run the pipeline**: After saving the modified `insar_graph.xml`, re-run the `run_gpt.py` script inside the Docker container.

## 11. SNAP Installer Download Fails with "404 Not Found"

**Problem:** During the Docker image build, the `wget` command for the ESA SNAP installer fails with an "ERROR 404: Not Found" message.

**Cause:** The direct download URL for ESA SNAP installers, especially for newer versions like 13.0.0, can change or become unavailable. The `Dockerfile` was initially configured to download SNAP 13.0.0, but its direct download link was found to be unreliable.

**Resolution:** The `Dockerfile` has been updated to use ESA SNAP version 9.0.0, which has a stable direct download link.

1.  **Verify `Dockerfile`:** Ensure your `Dockerfile` (located in `mini-insar-pipeline/Dockerfile`) contains the updated `wget` command for SNAP 9.0.0:
    ```dockerfile
    RUN wget https://download.esa.int/step/snap/9.0/installers/esa-snap_all_unix_9_0_0.sh -O esa-snap_all_unix_9_0_0.sh && \
        chmod +x esa-snap_all_unix_9_0_0.sh && \
        ./esa-snap_all_unix_9_0_0.sh -q -dir $SNAP_HOME && \
        rm esa-snap_all_unix_9_0_0.sh
    ```
2.  **Rebuild Docker Image:** After confirming the `Dockerfile` is updated, rebuild your Docker image:
    ```bash
    cd mini-insar-pipeline
    docker-compose build
    ```

## 12. Snappy Configuration Fails (Python interpreter compatibility or jpy build error)

**Problem:** When running `snappy-conf` inside the Docker container, you encounter errors such as:
*   `Python interpreter executable not found: python3` (even if `which python3` returns a path)
*   `Python configuration failed. Command [...] failed with return code 10.`
*   The `snappyutil.log` shows: `ERROR: The module 'jpy' is required to run snappy, but no binary 'jpy' wheel matching the pattern 'jpy-{version}-cp310-{abi_tag}-linux_x86_64.whl' could be found.`
*   Attempting to build `jpy` from source (e.g., `python3 setup.py bdist_wheel`) results in compilation errors like `error: lvalue required as left operand of assignment` related to `Py_REFCNT`.

**Cause:**
*   SNAP 9.0.0's `snappy` module has known compatibility issues with newer Python versions (e.g., Python 3.10, which is default on Ubuntu 22.04). The `jpy` bridge, which `snappy` relies on, uses deprecated Python C API calls that cause compilation failures with Python 3.10.
*   The `deadsnakes` PPA, while useful for installing multiple Python versions, does not provide Python 3.6 for Ubuntu 22.04 (Jammy) due to `libssl` dependencies.

**Resolution:**

The most robust solution is to use a Docker base image that natively supports a Python version compatible with SNAP 9.0.0's `snappy` module, such as Python 3.6.

1.  **Modify `Dockerfile` to use an Ubuntu 18.04 base image:**
    *   Change the `FROM` line in your `Dockerfile` from `nvidia/cuda:11.8.0-base-ubuntu22.04` to `nvidia/cuda:11.8.0-base-ubuntu18.04`. Ubuntu 18.04 (Bionic) typically includes Python 3.6 as its default `python3`.
    *   Remove any steps related to adding the `deadsnakes` PPA or explicitly installing `python3.6` via `apt-get install`.
    *   Ensure `python3-dev` and `build-essential` are installed for the new base image.

2.  **Clean Docker System:**
    *   After modifying the `Dockerfile`, it's crucial to clean up old Docker images and build cache to ensure a fresh build.
        ```bash
        docker system prune -a
        ```

3.  **Rebuild Docker Image:**
    *   Rebuild the Docker image with the updated `Dockerfile`.
        ```bash
        docker-compose build
        ```

4.  **Run Container Interactively:**
    *   Run the container interactively to attempt `snappy-conf` again.
        ```bash
        docker-compose run --rm insar /bin/bash
        ```

5.  **Re-run `snappy-conf`:**
    *   Inside the container, execute `snappy-conf` using the default `python3` (which should now be Python 3.6).
        ```bash
        /opt/snap/bin/snappy-conf python3 /opt/snap/snap-python
        ```

6.  **Check `snappyutil.log` for Success:**
    *   After running `snappy-conf`, check the log file. If successful, it should indicate a successful configuration.
        ```bash
        cat /opt/snap/snap-python/snappy/snappyutil.log
        ```

## 13. GPU Not Detected or Used in Docker

**Problem:** You have an NVIDIA GPU and have configured the project for GPU acceleration, but the container does not seem to use it. Running `nvidia-smi` inside the container shows `command not found` or `NVIDIA-SMI has failed because it couldn't communicate with the NVIDIA driver.`

**Cause:** This issue typically has two main causes:
1.  The Docker Compose configuration is not correctly requesting the GPU.
2.  The host machine (especially a WSL2 environment) is not correctly configured to pass the GPU through to Docker containers.

> **Note on GPU Utilization:**
> Even if your GPU is correctly detected within the Docker container (as verified by `nvidia-smi`), the current version of ESA SNAP (and specifically the InSAR processing operators used in this pipeline) does NOT support GPU acceleration. Therefore, you will likely observe 0% GPU utilization and 0MiB GPU memory usage in `nvidia-smi` while the InSAR pipeline is running. This is expected behavior and does not indicate a problem with your GPU setup or Docker configuration. The processing will be performed on the CPU.

**Resolution:**

1.  **Check `docker-compose.yml`:**
    *   Open `mini-insar-pipeline/docker-compose.yml`.
    *   Verify that the `insar` service has the `gpus: all` key. This is the correct, modern way to request GPU access.
        ```yaml
        services:
          insar:
            build: .
            # ... other settings
            gpus: all
        ```
    *   If this key is missing or commented out, add it and rebuild the container (`docker-compose build`).

2.  **Verify Host Setup (Especially for WSL2):**
    *   For GPU support to work with Docker Desktop on Windows, your WSL2 environment needs the **NVIDIA Container Toolkit**.
    *   A detailed guide is provided in this repository. Please ensure you have followed all the steps, especially running `nvidia-ctk runtime configure` and restarting Docker.
    *   **See the guide:** [WSL2 GPU Setup Guide](../docs/WSL_GPU_SETUP.md)

3.  **Final Verification:**
    *   After confirming both configurations above, run the container:
        ```bash
        cd mini-insar-pipeline
        docker-compose run --rm insar /bin/bash
        ```
    *   Inside the container, test again with `nvidia-smi`.
    *   A successful connection will display a table with your GPU's details (name, driver version, etc.). An unsuccessful connection will result in an error like `command not found` or `NVIDIA-SMI has failed`.

---
## 14. PyTorch Fails to Detect GPU or Throws CUDA Error

**Problem:** You have installed PyTorch, but your script reports that `torch.cuda.is_available()` is `False`, or you encounter CUDA-related errors at runtime.

**Cause:** This is almost always caused by a mismatch between the CUDA version PyTorch was compiled for and the CUDA version available in the Docker container. For example, you may have installed a PyTorch version for CUDA 12.1 (`cu121`) while the container provides CUDA 11.8.

**Resolution:**

1.  **Uninstall Incorrect PyTorch:**
    ```bash
    pip3 uninstall torch torchvision torchaudio
    ```
2.  **Install Correct PyTorch for CUDA 11.8:**
    Re-install PyTorch using the correct index URL for CUDA 11.8:
    ```bash
    pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
    ```

---

## Understanding Successful Log Output and Next Steps

When the pipeline runs successfully, you might see log messages similar to these, indicating a normal and expected progression:

### Log Interpretation:

**1. SRTM DEM のダウンロード完了**
```
xdata/dem/SRTMGL1/S45E172.SRTMGL1.hgt.zip
....10%....20%....90% done.
```
→ この地区 (S45E172) のDEMが正しく落ちてきています。

**2. SNAP（GAMMA バックエンド含む）が jBLAS をロードしてクリーンアップ**
```
org.jblas INFO Deleting /tmp/jblas...
```
→ SNAP の InSAR オペレーションでは内部で Java + jBLAS（線形代数）を使うため、
テンポラリにライブラリを展開し、処理後に削除します。
これは **完全に正常** です。(異常の場合はここでエラーが出ます)

**3. プロンプトが帰ってきた**
```
root@4bde7702323:/opt/project#
```
→ つまり **前のコマンドはすべて成功した** ということです。

### Next Steps:

あなたが次に行うべきは **パイプラインの次のステップのコマンドを実行** することです。

もし Mini InSAR Pipeline v2 を使っているなら：

▶️ **Full example run（続き）**

1.  **データダウンロード（もう完了）**

2.  **コレジストレーション & インターフェログラム生成**
    ```bash
    python /opt/scripts/run_gpt.py /opt/graphs/insar_graph.xml \
        --in1 /opt/data/SAFE/S1A_XXXX.SAFE \
        --in2 /opt/data/SAFE/S1A_YYYY.SAFE \
        --out /opt/data/out
    ```

3.  **VRT → GeoTIFF 変換**
    ```bash
    python /opt/scripts/convert_vrt_to_tif.py /opt/data/out
    ```

4.  **レポート生成（干渉縞のプレビュー付き）**
    ```bash
    python /opt/scripts/generate_report.py /opt/data/out
    ```

### Judging Pipeline Completion:

✅ **このログが意味していること**

あなたが貼った部分は：

*   SRTM DEM ダウンロード
*   SNAP/jBLAS の内部処理
*   一時ファイル削除
*   エラーなしでプロンプトが返った

という **途中ステップが成功した** という内容です。

これは “完了” ではなく “次のステップに進める状態” という意味のログです。

🔥 **パイプライン全体が完了したかを判断する方法**

InSAR Pipeline v2 の全処理が完了した場合は：

`/opt/data/out/` 内に以下が出ているはずです：

*   `coherence.tif`
*   `interferogram.tif`
*   `wrapped_phase.tif`
*   `unwrapped_phase.tif`（ある場合）
*   `amplitude.tif`
*   中間 VRT ファイル
*   `report.html`（レポート生成スクリプトを使った場合）

もし 上記が出ていなければ、まだ途中 です。

📌 **今あなたのログは “どのステップ？”**

あなたが貼ったログは DEMダウンロード → SNAP 起動処理の一部 → 正常終了
これは主に：

*   `download_data.py` か
*   `run_gpt.py` の前半部分

に該当します。

🧭 **次に確認したいこと（これで全体完了かすぐ判定できます）**
👉 コマンドをコンテナ内で実行してください：
```bash
ls -R /opt/data/out
```

すると：

*   沢山の GeoTIFF や VRT がある → 全体ほぼ完了
*   空 or フォルダ自体がない → まだ全体は終わっていない

---

### Current Pipeline Status (Based on `insar_filtered.tif`):

✅ **結論から言うと：**

まだ InSAR パイプラインは “完全には終了していません”。

現在出ているのは `insar_filtered.tif` 1つだけ なので、
全工程のうち「後半の一部まで進んだ」状態 です。

📌 **本来、フル実行が成功したときに `/opt/data/out` に出るべき代表ファイル**

あなたの InSAR Pipeline（Mini InSAR v2）なら通常は：

*   `coherence.tif`
*   `interferogram.tif`
*   `wrapped_phase.tif`
*   `unwrapped_phase.tif`（ある場合）
*   `amplitude_master.tif`
*   `amplitude_slave.tif`
*   `diff_phase.tif`
*   `insar_filtered.tif` ← 今これだけ出てる
*   `report.html`（`generate_report.py` まで実行したら）
*   中間の `.vrt` ファイル多数

などが揃います。

今あるのは 最終的な出力のほんの１つだけ。

🔥 **現状はどのステップまで進んでいるか？**

`insar_filtered.tif` は通常、

▶ フィルタリング・地形補正以降の後処理の一部が成功した段階

つまり：

*   マスター/スレーブ SLC 読込
*   オルビット補正
*   コアレジストレーション
*   インターフェログラム生成
*   コヒーレンス生成
*   位相フィルタリング

などの途中までは動いている可能性が高い。

しかし：

*   コヒーレンス
*   インターフェログラム（wrapped phase）

などが出ていないため、まだ半分〜7割程度で止まっている。


    This ensures that the installed PyTorch version is compatible with the container's environment.

---

# Troubleshooting Experience from a Contributor

When I first ran this pipeline, I encountered various errors and found it very challenging. Therefore, I would like to share what I learned: this debugging journey is a very normal, everyday process.

Tackling these problems is exactly what professional researchers and engineers do daily. The errors I faced were the kind of issues they resolve every day.

*   Simple input mistakes in file paths that are easy to overlook.
*   Syntax issues in the graph XML file that required updates to match the software version.
*   Insufficient disk space that needed cleanup.

With each error I resolved, I felt I was steadily moving forward. This trial-and-error process is not a sign of failure. Rather, it is an essential and valuable experience in the field of actual scientific and technical computing. So, if you encounter errors, it is a sign that you are on the right track.