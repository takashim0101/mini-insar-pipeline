# Mini InSAR Pipeline v2 – Professional Edition

## Non-Technical Summary

This project is a ready-to-use toolkit for processing satellite radar data to detect tiny movements of the Earth's surface, like those from earthquakes, volcanoes, or infrastructure changes. Think of it as a high-tech measuring tape that uses satellite images to see how the ground has shifted, down to the millimeter.

While this pipeline is set up for a specific type of analysis called InSAR, its underlying design is a flexible and reusable "template." This means it can be easily adapted for other types of satellite data processing, making it a valuable starting point for a wide range of geospatial and Earth observation projects.

---

A fully reproducible, GPU‑accelerated InSAR processing pipeline built with Docker, SNAP, Python, and modern infrastructure practices. This project demonstrates how a single engineer can design, deploy, and operate a compact but production‑ready InSAR workflow—covering data acquisition, preprocessing, interferogram generation, and displacement visualization.

The goal is to provide a **clean, minimal, operationally realistic reference pipeline** that can be integrated into GeoAI platforms, cloud/HPC environments, or national geospatial systems.

---

# 🚀 Key Capabilities

## **1. End‑to‑End InSAR Workflow (Single‑Engineer Architecture)**

*   Automated search/download of Sentinel‑1 SLC scenes (ASF)
*   SNAP graph processing (coregistration → interferogram → filtering)
*   GeoTIFF/VRT output for analysis and visualization
*   Simple Python‑based displacement visualization + reporting
*   Fully reproducible Docker environment

## **2. GPU‑Ready Infrastructure (Optional, Recommended)**

Supports GPU execution where possible, enabling:

*   Faster matrix operations
*   Faster unwrapping / filtering (future modules)
*   Local experimentation with OLLAMA + GPU inside Docker

## **3. GeoAI‑First Design**

*   SAR automation with Python
*   Clean I/O layer (GeoTIFF, VRT, JSON)
*   Ready for ML extensions (e.g., coherence ML cleaners, PS selection)

## **4. Production‑Ready Engineering Practices**

*   Dockerfile + docker-compose orchestration
*   Isolated and reproducible runtime
*   Clear troubleshooting guides
*   WSL2 memory configuration for stable SNAP processing
*   [HPC Support Case Study (English)](./mini-insar-pipeline/HPC_SUPPORT_CASE_STUDY_EN.md)

### Speeding Up Docker Builds with .dockerignore

To reduce Docker image build times, a `.dockerignore` file has been created in the project's root directory. This file instructs Docker to exclude unnecessary files and directories (e.g., `data/`, `.git/`, `venv/`) from the build context.

By excluding large folders like the `data/` directory, the execution time of the `COPY . /opt/project` step is significantly reduced, leading to faster overall builds.

**Benefits:**
*   Reduces the size of the build context, shortening the time it takes to send to the Docker daemon.
*   Results in smaller image sizes by excluding unnecessary files.
*   Dramatically improves build times, especially by preventing the copying of large amounts of satellite data from the `data/` directory.

This optimization is particularly noticeable when using the `--no-cache` option or when building the image for the first time.

---

# 🎯 Project Status & Next Steps

This section organizes the current project progress and the next steps to take.

## ✔ Current Progress

*   **GPU Test Successful**: GPU testing using `gpu_test.py` was successful, confirming GPU access within the Docker container.
*   **GPT Graph Production Processing Successful**: Master / Slave / Target Product are working correctly, and interferogram generation and Goldstein filtering have been completed.
*   **Docker + SNAP + GPU + ASF Data Integration Successful**: This was the biggest challenge, but the Docker environment, ESA SNAP, GPU passthrough, and ASF data integration are all functioning normally.
*   **Docker Images Built Successfully**: All Docker images (`sentinel_insar-pipeline:latest`) have been successfully built. The `.dockerignore` file is now in place to optimize future build times, especially for the `COPY` operations.

**🔥 In short, we are at the point where approximately 50% of the InSAR pipeline is complete.**
This is the stage where interferogram and Goldstein filtering have finished.

## 📌 Next Tasks (in order of priority)

Based on the current folder structure and progress, the next steps are as follows:

### 🥇 Step 1 — Complete `run_gpt.py` (Most important point to do now)

Currently, the goal is to complete `scripts/run_gpt.py` to fully automate the InSAR pipeline from the CLI. This involves passing Master/Slave paths, Graph Path, and output paths via a Python script.

**Example:**
```bash
python scripts/run_gpt.py \
  --master /opt/data/...SAFE \
  --slave /opt/data/...SAFE \
  --graph graphs/insar_graph.xml \
  --output /opt/data/out
```
This will make the pipeline "fully automated processing."

### 🥈 Step 2 — Phase Unwrapping with SNAPHU

In the current graph, processing stops at Interferogram and Filtering. Phase unwrapping is necessary to calculate displacement.

**Options:**
*   Build and connect SNAPHU within Docker (possible with a few lines added to Dockerfile).
*   Utilize SNAP's SNAPHU-Export function, execute SNAPHU, and then import the results (scriptable).

### 🥉 Step 3 — Convert to LOS Displacement (Phase → Displacement)

From the phase data unwrapped by SNAPHU, calculate the displacement (in millimeters) using the following formula:
`unwrapped_phase × (λ / 4π)`
This can be easily automated with Python (e.g., NumPy).

### 🏅 Step 4 — Generate GeoTIFF (`convert_vrt_to_tif.py` utilization)

`scripts/convert_vrt_to_tif.py` is a post-processing script for DIM → VRT → GeoTIFF. Since GeoTIFF format is desirable as the final output of InSAR, this step will connect to the pipeline.

### 🎖️ Step 5 — Automatic Report Generation with `generate_report.py` (Optional)

This configuration allows for automatic report generation in PDF or Markdown format.
**Ideal report content:**
*   Input pair information
*   Baseline (bperp)
*   Coherence map
*   Displacement map
*   Visualization diagrams

---

# 📦 System Requirements

### **Windows 10/11 + WSL2 + Docker Desktop**

*   WSL2 backend **required**
*   NVIDIA GPU + latest drivers
*   Docker Desktop with **GPU support enabled**

### **Python 3.10+ (host only for utility scripts)**

Used only for optional helper tools.

---

# ⚙️ Local Development Setup (Optional)

If you want to run the Python scripts locally without using Docker, you can set up a virtual environment and install the required dependencies.

1.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    ```

2.  **Activate the virtual environment:**
    *   **On Windows (PowerShell):**
        ```powershell
        .\venv\Scripts\Activate.ps1
        ```
    *   **On macOS/Linux:**
        ```bash
        source venv/bin/activate
        ```

3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.pipeline.txt
    ```

---

# ⚙️ 1. Prepare Earthdata Login (Required)

The pipeline uses **ASF Search API**, which requires NASA Earthdata credentials.

To provide your credentials securely, first copy the example environment file:

```bash
cp env.example .env
```

Then, open the newly created `.env` file and replace the placeholder values with your actual credentials:

```
EARTHDATA_USERNAME="your_earthdata_username"
EARTHDATA_PASSWORD="your_earthdata_password"
```

Docker Compose will automatically pick up these environment variables when you run `docker compose up` or `docker compose build`.

---

# ⚙️ 2. Configure WSL2 Resources (Critical for SNAP)

SNAP requires **high RAM**. Without this, the process will freeze or be killed.

Create or edit:

```
%USERPROFILE%\.wslconfig
```

Add:

```ini
[wsl2]
memory=16GB
processors=6
swap=16GB
localhostForwarding=true
```

Apply changes:

```powershell
wsl --shutdown
```

Restart Docker Desktop.

Verify memory:

```bash
free -h
```

---

# ⚙️ 3. Install OLLAMA + GPU Support (Optional, Recommended)

This pipeline is designed so you can:

*   run OLLAMA on Windows host,
*   expose GPU into Docker,
*   accelerate SAR processing + AI‑based SAR assistants.

**OLLAMA Install (Windows):**
[https://ollama.com/download](https://ollama.com/download)

Verify GPU access:

```powershell
ollama run llama3 "Test GPU"
```

---

# ⚙️ 4. Verify Docker GPU Access

### Test with CUDA Base Image

```powershell
docker run --rm --gpus all nvidia/cuda:12.2.0-base-ubuntu22.04 nvidia-smi
```

### Test PyTorch GPU (for future ML modules)

```powershell
docker run --rm --gpus all -it pytorch/pytorch:2.3.0-cuda12.1-cudnn8-runtime \  
python -c "import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0))"
```

Should output:

```
True NVIDIA GeForce RTX 4060 Laptop GPU
```

If this works, GPU passthrough is ready.

---

## 5. Example Pipeline Execution

> **Note:** The following commands are intended to be run inside the Docker containers, which is the **highly recommended** approach for this project. The Docker environment is pre-configured with all the necessary dependencies, which avoids the complex setup of libraries like GDAL on your local machine.
>
> If you haven't already, start the Docker containers with:
> ```bash
> docker-compose up -d
> ```

### Step 1 — Download Sentinel‑1 SLC (Optional)

If you already have the Sentinel-1 `.SAFE` data in `./data/SAFE/`, you can skip this step.

To run the download script inside the `pipeline` container:
```bash
docker-compose exec pipeline python /opt/project/scripts/download_data.py /opt/project/aoi.geojson 20210511 20210530
```

### Step 2 — Run SNAP InSAR Graph

Execute the InSAR processing graph using the `run_gpt.py` script inside the `snap` container. This script automates the execution of ESA SNAP's Graph Processing Tool (GPT).

```bash
docker-compose exec snap python /opt/project/scripts/run_gpt.py /opt/project/graphs/insar_graph.xml \
  --in1 /opt/data/SAFE/S1A_IW_SLC__1SDV_20210511T173941_20210511T174008_037843_047769_9526.SAFE \
  --in2 /opt/data/SAFE/S1A_IW_SLC__1SDV_20210530T173150_20210530T173217_038120_047FBA_A0C2.SAFE \
  --out /opt/data/out
```

**Important:** The script now automatically logs the execution time.

### Step 3 — Convert VRT → GeoTIFF

To convert the output to GeoTIFF, run the `convert_vrt_to_tif.py` script inside the `pipeline` container:
```bash
docker-compose exec pipeline python /opt/project/scripts/convert_vrt_to_tif.py /opt/data/out
```

### Step 4 — Generate Report

To generate a report with a visualization of the output, run the `generate_report.py` script inside the `pipeline` container:
```bash
docker-compose exec pipeline python /opt/project/scripts/generate_report.py /opt/data/out
```
---

## 6. What is SNAP Graph Execution? (InSAR Processing for Beginners)

The `insar_graph.xml` file used here defines a sequence of automated processing steps for Sentinel-1 radar data, executed by ESA SNAP's Graph Processing Tool (GPT). This process transforms raw satellite data into an interferogram, which can reveal millimeter-scale ground movements.

Here's a simplified breakdown:

1.  **Co-registration:**
    *   **What:** Accurately aligns two satellite images taken at different times over the same area. Imagine precisely stacking two photos of the same landscape taken days apart.
    *   **Why:** Essential for comparing the tiny phase differences between them to detect movement.
2.  **Interferogram Formation:**
    *   **What:** Creates an "interferogram" by measuring the phase difference (a property of radar waves) between the two co-registered images. This phase difference appears as a pattern of fringes (like contour lines).
    *   **Why:** These fringes contain information about ground deformation and topography.
3.  **Topographic Phase Removal:**
    *   **What:** Removes the part of the phase difference caused by the shape of the terrain (mountains, valleys). We only want the phase related to ground movement.
    *   **Why:** Isolates the phase changes directly caused by ground deformation, making them easier to observe.
4.  **Phase Filtering (e.g., Goldstein Filter):**
    *   **What:** Reduces noise in the interferogram, making the fringe patterns clearer and more interpretable.
    *   **Why:** Improves the quality of the deformation signal and helps in unwrapping the phase later.
5.  **Output (e.g., GeoTIFF):**
    *   **What:** Saves the processed interferogram into a standard geospatial format.
    *   **Why:** Allows for further analysis and visualization in GIS software.

**Important Note on GPU Usage:**
While this Docker environment is fully GPU-enabled, SNAP's core InSAR processing (including the `gpt` command with `insar_graph.xml`) is primarily **CPU-bound**. This means the GPU is not actively used during these specific InSAR steps. The GPU setup is crucial for **AI/Deep Learning workloads** (e.g., PyTorch, TensorFlow) and **Large Language Models (LLMs)** via tools like Ollama, which can leverage the GPU within this environment. This project demonstrates a versatile environment capable of both CPU-bound geospatial processing and GPU-accelerated AI tasks.

```
mini-insar-pipeline/
├── .gitignore
├── aoi.geojson
├── docker-compose.yml
├── Dockerfile
├── HPC_SUPPORT_CASE_STUDY_EN.md
├── requirements.txt
├── TROUBLESHOOTING.md
├── graphs/
│   └── (insar_graph.xml is expected here, but the directory is empty)
├── notebooks/
└── scripts/
    ├── convert_vrt_to_tif.py
    ├── download_data.py
    ├── generate_report.py
    └── run_gpt.py
```

---

# Validation & Expected Outputs

After running the pipeline, you should find the following in the `mini-insar-pipeline/data/out/` directory:

*   `insar_filtered.tif`: The filtered interferogram (phase-filtered). This file indicates that the core InSAR processing (co-registration, interferogram formation, topographic phase removal, and filtering) has completed successfully.
*   `insar_filtered.tif.aux.xml`: An auxiliary XML file containing additional metadata for the `insar_filtered.tif`.
*   `insar_filtered.tif.png`: A visualization of the interferogram.
*   `insar_report.txt`: A short textual report with output paths.

You can view the generated interferogram directly here:

[![Filtered Interferogram](docs/insar_filtered.png)](docs/insar_filtered.png)

### Sanity Checks
*   The interferogram should show coherent fringes over non-vegetated areas (coastal/urban).
*   If the interferogram is noisy (low coherence), try picking acquisition dates that are closer together.
*   If outputs are empty or you encounter an error, check the SNAP GPT logs printed to the console. Common issues include incorrect `.SAFE` paths or a missing manifest file.

---

# 🔧 Troubleshooting

For common issues and their resolutions, please refer to the [TROUBLESHOOTING.md](mini-insar-pipeline/TROUBLESHOOTING.md) file.

---

# 🎓 Learning Points & Demonstrated Skills

This project, especially the troubleshooting process, offers valuable insights for those interested in High-Performance Computing (HPC) or geospatial roles, directly aligning with skills sought in roles like a Cloud Infrastructure Engineer. It demonstrates practical experience in:

*   **Modern Scientific Computing Approach (Reproducibility & GeoAI Integration)**:
    *   **Demonstrated Skill**: This project exemplifies a modern approach to scientific computing by containerizing complex geospatial processing workflows (InSAR) within a Linux-based Docker environment. This strategy effectively resolves common path and dependency issues (e.g., with GDAL/PROJ) often encountered on Windows, ensuring cross-platform reproducibility and stability. Furthermore, by integrating GPU passthrough, the environment is not only robust for CPU-bound tasks like ESA SNAP's InSAR processing but also fully equipped for GPU-accelerated AI/ML workloads (e.g., PyTorch, Ollama). This dual capability showcases a best practice in GeoAI, where traditional geospatial analysis is seamlessly combined with cutting-edge AI, optimizing resource utilization and fostering innovation.
    *   **Relevance to Roles**: Essential for roles in scientific computing, GeoAI development, and MLOps, demonstrating the ability to build reproducible, high-performance computing environments that bridge traditional scientific workflows with modern AI/ML capabilities.

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




---

# 📄 Licensing

## Code Licensing

This pipeline's code is provided as-is. If you intend to publish or distribute this code, it is highly recommended to choose and include an appropriate open-source license (e.g., MIT, Apache 2.0) in your repository. This clarifies how others can use, modify, and distribute your code.

## Data Licensing

The Sentinel-1 data downloaded via this pipeline is sourced from the Alaska Satellite Facility (ASF). While ASF data is generally publicly funded and available, specific usage policies, especially concerning commercial applications, can vary by dataset.

**It is crucial for users to consult the End User License Agreements (EULAs) associated with each specific data collection to determine the exact commercial use policy and any other restrictions.**



# 📄 Future Extensions

*   GPU‑accelerated filtering/unwrapping
*   PyTorch‑based coherence cleaning
*   Real‑time deformation dashboards
*   Integration with OLLAMA LLM agents
*   National-scale cloud deployment examples

---

# 📨 Contact / Notes

This pipeline was built to demonstrate how an engineer can deliver **end‑to‑end SAR processing systems** alone—suitable for evaluation by national geospatial institutions.

Feel free to adapt, extend, or integrate this into your own GeoAI stack.
