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
    *   Alternatively, place a `.env` file in the `mini-insar-pipeline` directory with `EARTHDATA_USERNAME=your_username` and `EARTHDATA_PASSWORD=your_password`.
4.  **`.env` File Parsing:**
    *   **Do NOT use double quotes** around the values in the `.env` file (e.g., `EARTHDATA_USERNAME=your_username`, not `EARTHDATA_USERNAME="your_username"`), as `docker-compose` may fail to parse them.
5.  **Password Special Characters:**
    *   If your Earthdata password contains special characters (e.g., `!`), it might cause issues with `asf-search` or the underlying environment. While ASF requires a special character, consider temporarily changing your password to use a less problematic one (e.g., `@` or `#` instead of `!`) if the issue persists.
6.  **Network Connectivity (from within Docker):**
    *   Verify that the Docker container has internet access and can reach Earthdata's URS and ASF's API endpoints.
    *   Inside the container, run: `curl -v https://urs.earthdata.nasa.gov/` and `curl -v https://api.daac.asf.alaska.edu/`. Both should return `HTTP/1.1 200 OK`.
7.  **`asf-search` Debugging:**
    *   If the error persists, run `asf-search` authentication directly in a Python interpreter inside the container with debug logging enabled to get more detailed error messages.

## 2. `KeyError: 'features'` when parsing `aoi.geojson`

**Problem:** The `download_data.py` script fails with `KeyError: 'features'` when trying to read the `aoi.geojson` file.

**Cause:** The `aoi.geojson` file is formatted as a direct GeoJSON `Polygon` geometry object, but the script was initially expecting a GeoJSON `FeatureCollection` (which contains a top-level `'features'` key).

**Resolution:** The `download_data.py` script was modified to correctly parse both `FeatureCollection` and direct `Geometry` (like `Polygon`) GeoJSON formats.

## 3. `geo_search() got an unexpected keyword argument 'session'`

**Problem:** The `download_data.py` script fails with `ERROR: ASF search failed. Details: geo_search() got an unexpected keyword argument 'session'`.

**Cause:** The `asf_search.geo_search()` function does not accept a `session` argument for authentication; it handles authentication implicitly after `asf.ASFSession().auth_with_creds()` has been called.

**Resolution:** The `session=session` argument was removed from the `asf.geo_search()` call in `download_data.py`.


## 5. SNAP GPT Fails with "Specified 'file' [...] does not exist." (Missing .SAFE directory)

**Problem:** The `run_gpt.py` script fails with an error message like `Error: [NodeId: Read-Slave] Specified 'file' [/opt/data/SAFE/S1A_...SAFE] does not exist.`

**Cause:** The `download_data.py` script downloads Sentinel-1 data as `.zip` archives. However, the SNAP `Read` operator in the processing graph expects the unzipped `.SAFE` directories as input, not the `.zip` files. The error occurs because the `.SAFE` directory corresponding to the downloaded `.zip` file is not present.

**Resolution:** The `download_data.py` script needs to be modified to automatically unzip the downloaded `.zip` files after successful download.

1.  **Update `Dockerfile`:** Ensure the `unzip` utility is installed in the Docker image. Add `unzip` to the `apt-get install` command in the `Dockerfile`.
2.  **Update `download_data.py`:** Modify the `download_data.py` script to include logic for unzipping each downloaded `.zip` file into its corresponding `.SAFE` directory and then removing the `.zip` file.
3.  **Rebuild Docker Image:** After modifying `Dockerfile` and `download_data.py`, you must rebuild the Docker image using `docker-compose build`.
4.  **Re-run Pipeline:** Then, re-run the pipeline starting from the `download_data.py` step.

## 4. SNAP GPT Command Fails with `UnknownFieldException`

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

## 7. `[Errno 5] Input/output error` during unzipping

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

*   **Project-Specific Data:**
    *   Clear the contents of the `data/SAFE` and `data/out` directories.

*   **General Windows Cleanup:**
    *   **Disk Cleanup Tool:** Run the built-in Windows "Disk Cleanup" utility and select "Clean up system files" to remove old Windows Update files.
    *   **Uninstall Unused Apps:** Go to "Settings" > "Apps" > "Installed apps" and uninstall any software you no longer need.
    *   **Disk Analysis Tools:** Use free tools like **WinDirStat** or **TreeSize Free** to visualize what is consuming your disk space. This is often the most effective way to find large, forgotten files.

*   **Docker Cleanup:**
    *   The `docker system prune -a` command is an effective but aggressive way to reclaim disk space by removing all stopped containers, unused networks, and dangling images.
        *   **Real-World Example:** One user resolved an `[Errno 5]` error by running `docker system prune -a`, which successfully reclaimed over 10GB of disk space.
    *   For a less aggressive approach, you can use more targeted commands:
        *   `docker builder prune`: Safely removes only the build cache.
        *   `docker image prune`: Safely removes "dangling" images (images not tagged or used by any container).

For Windows users, you can also free up significant space on your C: drive by running the following command in an **administrator PowerShell or Command Prompt**:
```
Dism.exe /online /Cleanup-Image /StartComponentCleanup
```
This command cleans up the Windows Component Store, removing older versions of system components. For an even more aggressive cleanup that removes all superseded versions of every component (making it impossible to uninstall previous updates), you can use:
```
Dism.exe /online /Cleanup-Image /StartComponentCleanup /ResetBase
```

Other advanced methods to free up space on Windows (use with caution):
*   **Disable Hibernation:** If you don't use hibernation, disabling it can free up significant space (equal to your RAM size). Run in **administrator PowerShell or Command Prompt**:
    ```
powercfg.exe /hibernate off
```
*   **Manage System Restore Points:** Reduce the disk space allocated for system restore points or delete older ones. Search for "Create a restore point" in Windows, then configure settings.

## 6. `IndentationError` in `download_data.py`

**Problem:** The `download_data.py` script fails with an `IndentationError: unexpected indent`.

**Cause:** This is a Python syntax error caused by incorrect indentation in the script. It likely occurred during a copy-paste operation when adding new code, such as the unzipping logic.

**Resolution:** The script must be corrected to have valid Python indentation. This involves:
1.  Ensuring that `import` statements are at the top of the file with no leading whitespace.
2.  Ensuring that all code blocks (e.g., inside `try...except` blocks, `for` loops, and functions) are indented consistently (e.g., with 4 spaces per level).
3.  The script was corrected to fix the indentation of the download and unzip logic.

## 8. Killed message during processing (Out of Memory)

**Problem:** The processing script (e.g., `generate_report.py` or `run_gpt.py`) terminates abruptly with a "Killed" message, without a clear error traceback.

**Cause:** The "Killed" message typically indicates that the process ran out of available memory (RAM) and was terminated by the operating system (or Docker's resource limits). Scientific computing tasks, especially InSAR processing, are highly memory-intensive.

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
5.  **Re-run the pipeline**: After saving the modified `insar_graph.xml`, re-run the `run_gpt.py` script inside the Docker container.        ```
        After saving `.wslconfig`, you must shut down and restart WSL for the changes to take effect. Open PowerShell or Command Prompt (not within WSL) and run: `wsl --shutdown`. Then, restart your Docker Desktop application. You can verify the allocated memory by running `free -h` inside your WSL terminal or `docker info | grep "Total Memory"` after Docker Desktop has restarted.
    *   After changing settings, apply and restart Docker Desktop.

3.  **Reduce Memory Footprint (if possible):**
    *   If the issue persists, review the script's memory usage. For plotting large images, sometimes downsampling or processing in chunks can help, though this might require code modifications.
    *   Ensure no other memory-intensive applications are running on your host machine simultaneously.

4.  **Re-run:** After adjusting memory settings, re-run the pipeline steps.