import subprocess
import sys
import os
import argparse

def main():
    parser = argparse.ArgumentParser(
        description="Run ESA SNAP's Graph Processing Tool (gpt) for InSAR processing."
    )
    parser.add_argument("graph_xml", help="Path to the SNAP graph XML file.")
    parser.add_argument("--in1", required=True, help="Path to the master Sentinel-1 SAFE file (ZIP or unzipped directory).")
    parser.add_argument("--in2", required=True, help="Path to the slave Sentinel-1 SAFE file (ZIP or unzipped directory).")
    parser.add_argument("--out", default="/opt/data/out", help="Output directory for processed products.")
    args = parser.parse_args()

    # Ensure output directory exists
    os.makedirs(args.out, exist_ok=True)

    # Construct the gpt command
    gpt_command = [
        '/opt/snap/bin/gpt',
        args.graph_xml,
        f'-Pmaster={args.in1}',
        f'-Pslave={args.in2}',
        f'-Poutput.path={args.out}'
    ]

    print(f"DEBUG: Running GPT command: {' '.join(gpt_command)}")

    try:
        # Execute the gpt command and capture stdout/stderr
        # text=True decodes stdout/stderr as text
        # check=True will raise CalledProcessError if the command returns a non-zero exit code
        result = subprocess.run(gpt_command, capture_output=True, text=True, check=True)
        print("GPT command executed successfully.")
        if result.stdout:
            print("GPT STDOUT:")
            print(result.stdout)
        if result.stderr:
            print("GPT STDERR:")
            print(result.stderr)

    except subprocess.CalledProcessError as e:
        print(f"ERROR: GPT command failed with exit status {e.returncode}.")
        print(f"Command: {' '.join(e.cmd)}")
        if e.stdout:
            print("GPT STDOUT:")
            print(e.stdout)
        if e.stderr:
            print("GPT STDERR:")
            print(e.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print(f"ERROR: GPT command not found. Ensure SNAP is installed and '/opt/snap/bin/gpt' is correct.")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()