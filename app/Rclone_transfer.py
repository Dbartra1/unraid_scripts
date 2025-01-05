import os
import time
import psutil
import shutil
import logging
from dotenv import load_dotenv
import subprocess

# Load environment variables from a .env file
load_dotenv()

# Directories to compare and sync
DIRECTORY_1 = os.getenv("DIRECTORY_1")
DIRECTORY_2 = os.getenv("DIRECTORY_2")

# File path for logs
LOG_PATH = os.getenv("LOG_PATH")

if not DIRECTORY_1 or not DIRECTORY_2 or not LOG_PATH:
    raise ValueError("DIRECTORY_1, DIRECTORY_2, and LOG_PATH must be set in the .env file.")

# Setup Logging
log_file = f"{LOG_PATH}/rclone_sync_log_{time.strftime('%Y-%m-%d_%H-%M-%S')}.log",  # Formatted with current time
logging.basicConfig(
    filename=log_file,
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'  
)

def get_max_transfers():
    """Dynamically calculate the number of max transfers based on system resources."""
    cpu_cores = psutil.cpu_count(logical=True)
    available_memory = psutil.virtual_memory().available / (1024 ** 3)  # Convert to GB

    # A heuristic: Use 75% of the CPU cores or reduce if memory is low
    max_transfers = max(1, int(cpu_cores * 0.75))
    if available_memory < 8:
        max_transfers = max(1, max_transfers // 2)

    logging.info(f"System Resources: {cpu_cores} CPU cores, {available_memory:.2f} GB memory")
    logging.info(f"Max Transfers set to: {max_transfers}")
    return max_transfers

def sync_directories_with_rclone():
    """Use rclone to synchronize directories with delta transfers."""
    if not os.path.exists(DIRECTORY_1):
        logging.error(f"Source directory {DIRECTORY_1} does not exist. Exiting.")
        return
    if not os.path.isdir(DIRECTORY_1):
        logging.error(f"{DIRECTORY_1} is not a valid directory. Exiting.")
        return

    if not os.path.exists(DIRECTORY_2):
        logging.info(f"Destination directory {DIRECTORY_2} does not exist. Creating it.")
        os.makedirs(DIRECTORY_2, exist_ok=True)
        if not os.path.exists(DIRECTORY_2):
            raise OSError(f"Failed to create destination directory: {DIRECTORY_2}. Exiting.")
    if not os.path.isdir(DIRECTORY_2):
        logging.error(f"{DIRECTORY_2} is not a valid directory. Exiting.")
        return

    max_transfers = get_max_transfers()

    # Common fallback paths for rclone
    COMMON_RCLONE_PATHS = [
        "/usr/local/bin/rclone",
        "/usr/bin/rclone",
        "C:\\Program Files\\rclone\\rclone.exe",
        "C:\\Program Files (x86)\\rclone\\rclone.exe"
    ]

    # Check environment variable first
    rclone_executable = os.getenv("RCLONE_EXECUTABLE")

    # If not set, check system PATH
    if not rclone_executable:
        rclone_executable = shutil.which("rclone")

    # If still not found, search common fallback paths
    if not rclone_executable:
        for path in COMMON_RCLONE_PATHS:
            if os.path.isfile(path) and os.access(path, os.X_OK):
                rclone_executable = path
                break

    # Raise an error if rclone still isn't found
    if not rclone_executable:
        raise FileNotFoundError(
            "Rclone executable not found. Ensure it's installed and either set via the 'RCLONE_EXECUTABLE' "
            "environment variable, available in your system PATH, or located in a standard install directory."
        )

    logging.info(f"Using rclone executable: {rclone_executable}")

    # Construct the rclone command
    rclone_command = [
        rclone_executable, "copy", 
        DIRECTORY_1, DIRECTORY_2,
        "--transfers", str(max_transfers),
        "--checkers", str(max_transfers),
        "--progress",
        "--log-file", log_file,
        "--log-level", "DEBUG",
        "--exclude", ".Trash-99/**"
    ]

    logging.info(f"Starting rclone sync: {DIRECTORY_1} -> {DIRECTORY_2}")
    try:
        result = subprocess.run(rclone_command, check=True, capture_output=True, text=True, timeout=3600)
        logging.info(result.stdout)
        if result.stderr:
            logging.error(result.stderr)
        logging.info("Directory synchronization complete.")
    except subprocess.CalledProcessError as e:
        logging.error(f"rclone command failed with error: {e.stderr}")
    except Exception as e:
        logging.error(f"Unexpected error during rclone sync: {e}")

def main():
    logging.debug("Starting the script...")

    try:
        # Synchronize directories using rclone
        logging.debug(f"Starting synchronization: {DIRECTORY_1} -> {DIRECTORY_2}")
        sync_directories_with_rclone()

    except Exception as e:
        logging.error(f"An unexpected error occurred in the main logic: {e}")
    
    logging.info("Rclone transfer script completed successfully.")

# Run the script
if __name__ == "__main__":
    main()
