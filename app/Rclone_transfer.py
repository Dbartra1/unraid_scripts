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

# Setup Logging
logging.basicConfig(
    filename=f"{LOG_PATH}/rclone_sync_log_{time.strftime('%Y-%m-%d_%H-%M-%S')}.log",  # Formatted with current time
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
        os.makedirs(DIRECTORY_2)
    if not os.path.isdir(DIRECTORY_2):
        logging.error(f"{DIRECTORY_2} is not a valid directory. Exiting.")
        return

    max_transfers = get_max_transfers()
    
    rclone_executable = shutil.which("rclone")
    
    if not rclone_executable:
        raise FileNotFoundError(
            "Rclone executable not found. Ensure it's installed and available in your system PATH."
        )

    # Construct the rclone command
    rclone_command = [
        rclone_executable, "sync", 

        DIRECTORY_1, DIRECTORY_2,
        "--transfers", str(max_transfers),
        "--checkers", str(max_transfers),
        "--progress",
        "--log-file", f"{LOG_PATH}/rclone_sync_log_{time.strftime('%Y-%m-%d_%H-%M-%S')}.log",
        "--log-level", "DEBUG"
    ]

    logging.info(f"Starting rclone sync: {DIRECTORY_1} -> {DIRECTORY_2}")
    try:
        # Run the rclone command
        subprocess.run(rclone_command, check=True)
        logging.info("Directory synchronization complete.")
    except subprocess.CalledProcessError as e:
        logging.error(f"rclone command failed with error: {e}")
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

# Run the script
if __name__ == "__main__":
    main()
