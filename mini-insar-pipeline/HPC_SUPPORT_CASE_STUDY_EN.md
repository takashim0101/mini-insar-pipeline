### Non-Technical Summary

This document describes how I tackled a series of technical challenges to get a specialized satellite data processing system (called InSAR) up and running. InSAR helps scientists measure tiny changes in the Earth's surface, like ground movement after an earthquake or volcano.

The system was built using advanced computing tools (like Docker and a High-Performance Computer setup), but it wasn't working. I acted like a detective, finding and fixing problems ranging from simple typos to complex software settings and even issues with the computer's hard drive running out of space.

My goal was to make this powerful scientific tool reliable and easy for technical professionals to use. By solving these problems, I not only got the system working but also created clear instructions so others wouldn't face the same difficulties. This experience shows my ability to solve tough technical puzzles and help scientists focus on their research, not on computer problems.

### Case Study: Debugging and Stabilizing an InSAR Processing Pipeline

**Objective:**
To bring a non-functional, containerized InSAR scientific computing pipeline to a fully operational state.

**Challenges Encountered and Solutions:**

1.  **Challenge: Disk Space Shortage Leading to I/O Errors**
    *   **Symptom:** `[Errno 5] Input/output error` occurred, causing processing to fail.
    *   **Diagnosis:** Used `WinDirStat` to identify that the host OS (Windows) C: drive was being consumed by an overgrown WSL2 virtual disk (`.vhdx`).
    *   **Solution:** Established and executed a procedure using PowerShell commands (`wsl --shutdown`, `Optimize-VHD`) to safely shrink the virtual disk from over 200GB to tens of GBs without data loss.

2.  **Challenge: SNAP Processing Graph Execution Errors**
    *   **Symptom:** Multiple errors from the SNAP GPT tool, including `No target product set` and `Split product is expected`.
    *   **Diagnosis:** Analyzed `insar_graph.xml` and researched the correct syntax for the SNAP `Back-Geocoding` operator. Discovered that the Sentinel-1 TOPSAR workflow requires splitting both master and slave images.
    *   **Solution:** Systematically revised the XML graph, correcting the `<sources>` tag syntax, adding the necessary `TOPSAR-Split` nodes, and setting appropriate parameters such as `subswath` and `polarization`.

3.  **Challenge: Environmental Configuration Inconsistency**
    *   **Symptom:** `.env` file settings were not being applied, leading to confusion about which configurations were active.
    *   **Diagnosis:** Analyzed `docker-compose.yml` and Python scripts to confirm that the pipeline ignores the `.env` file and uses shell environment variables (`EARTHDATA_USERNAME`, etc.). The `.env` file was found to be configured for a different (Copernicus) workflow.
    *   **Solution:** Clarified the correct configuration method and recommended deleting or renaming unused files to prevent future confusion.

**Skills Demonstrated Through This Experience:**

*   **Problem-Solving Ability:** The capacity to logically break down complex, interdependent technical problems and solve them persistently, one by one.
*   **Scientific Computing:** Practical knowledge of InSAR workflows, container technology (Docker), and data processing pipelines.
*   **HPC-Related Technologies:** Proficiency in Linux environment operations, shell scripting, Python, and virtualisation technology (WSL2) management.
*   **Communication and Documentation:** The proactive attitude to summarise acquired knowledge into documentation like `README.md` and `TROUBLESHOOTING.md` for the benefit of other technical professionals and the community.

**Outcome:**
The pipeline was brought to a fully operational state, with the core SNAP GPT processing taking approximately 26 minutes to execute. The project's documentation was also significantly improved, creating a smoother user experience for future users.