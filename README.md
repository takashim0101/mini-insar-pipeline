# Sentinel InSAR Project — A Guide for Non-Technical Users

## 1. Project Overview

The goal of this project is to use a Python-based framework to run and manage various tools and cloud services. The directory name, `sentinel_insar`, suggests its origins in geospatial analysis using Sentinel satellite data for InSAR (Interferometric Synthetic Aperture Radar).

Currently, the focus is on the **Multi-server MCP framework**, which involves managing containerized applications and integrating with cloud services like AWS and Google AI.

## 2. Preparing the Sandbox Environment

This project operates within a sandbox environment (`MCP_DOCKER`) powered by the Gemini CLI.

**Step 1: Launch the Sandbox**

Launch the sandbox container using the following command.

```bash
docker run -it --name MCP_DOCKER \
    -v /c/Portfolio/sentinel_insar:/workspace \
    -v /var/run/docker.sock:/var/run/docker.sock \
    us-docker.pkg.dev/gemini-code-dev/gemini-cli/sandbox:0.13.0
```

*Note: Automatic updates are disabled in sandbox mode, but the core CLI functionalities are available.*

**Step 2: Google Authentication**

After the container starts, the Gemini CLI will prompt you to authenticate.

1.  Select **"1. Login with Google"**.
2.  Follow the on-screen instructions to authenticate with your Google account in your browser.

Once complete, you can begin using the Gemini CLI.

## 3. Current Setup Status

*   **Sandbox (`MCP_DOCKER`)**: Active and running.
*   **Gemini CLI**: Operating correctly inside Docker.
*   **Google Authentication**: Complete (enabling Q&A, code execution, etc.).
*   **.env File**: Loaded.
    *   `GOOGLE_CLOUD_PROJECT` is currently a placeholder. (In this state, no charges will be incurred from Google Cloud.)
    *   `GOOGLE_CLOUD_LOCATION` is set.
*   **/workspace**: Recognized as the project directory.
*   **GEMINI.md**: Applied to the sandbox configuration.

## 4. About MCP Docker Costs

*   Logging into the sandbox and basic Gemini CLI operations are **free**.
*   Costs **may be incurred** depending on the services you use inside the container.
    *   **Examples**: Paid usage of the Gemini API, Vertex AI, or services beyond the AWS Free Tier.

It is recommended to start with free operations to familiarize yourself with the environment.

## 5. Environment Check (Non-Tech Friendly)

You can use these steps to verify that the environment is working correctly.

**5-1. Activate Python Virtual Environment**
```bash
source venv/bin/activate
```

**5-2. Check Python and Installed Packages**
```bash
python --version
pip list
```

**5-3. Check Environment Variables**
```bash
env | grep GOOGLE
```
*Example Output:*
```
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
```

**5-4. Test with a Simple Python Script**

*   Create a file named `test_env.py` in `/workspace`:
    ```python
    import os

    print("Current directory:", os.getcwd())
    print("GOOGLE_CLOUD_PROJECT:", os.getenv("GOOGLE_CLOUD_PROJECT"))
    print("GOOGLE_CLOUD_LOCATION:", os.getenv("GOOGLE_CLOUD_LOCATION"))
    ```
*   Run the script:
    ```bash
    python test_env.py
    ```
*Example Output:*
```
Current directory: /workspace
GOOGLE_CLOUD_PROJECT: your-project-id
GOOGLE_CLOUD_LOCATION: us-central1
```
This confirms that your Python environment, environment variables, and sandbox are all working correctly.

## 6. Basic Gemini CLI Examples (for Non-Technical Users)

**Check project status:**
```bash
gemini status
```

**List files:**
```bash
ls -la
```

**Ask a simple question:**
```bash
gemini ask "What is the current directory?"
```
*Example Output:*
```
Current directory: /workspace
```

## 7. Summary

By following this guide, even non-technical users can launch the sandbox, verify the environment, and perform basic Gemini CLI operations. We recommend getting comfortable with the free operations first before exploring cloud service integrations and more advanced code execution.

💡 This guide is designed to allow anyone to independently get started, verify the setup, and learn the basics of the Gemini CLI.

## 8. Sub-projects

This repository contains several sub-projects. For detailed instructions and information on the Mini InSAR Pipeline, please refer to its dedicated README:

*   [Mini InSAR Pipeline README](mini-insar-pipeline/README.md)


