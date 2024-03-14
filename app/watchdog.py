import subprocess
import sys

RESTART_EXIT_CODE = 42  # Define a unique exit code to signal a restart


def main():
    args = [sys.executable, "main.py"]
    while True:
        process = subprocess.Popen(args)
        process.wait()
        if process.returncode != RESTART_EXIT_CODE:
            break  # Exit the loop if the application didn't exit with the restart code


if __name__ == "__main__":
    main()
