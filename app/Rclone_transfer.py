import os
import time
import psutil
import shutil
import logging
import requests
import platform
import socket
from dotenv import load_dotenv
import subprocess

"""__summary__
This script is used to synchronize two directories using rclone with delta transfers.
It uses environment variables to specify the directories and log file path.
The number of transfers is dynamically calculated based on system resources.
This is useful for keeping directories in sync across different systems or locations.
This script can send WOL packets as well as power on/off Dell servers using iDRAC. This needs to be enabled in the .env file.
"""

# Load environment variables from a .env file
load_dotenv()

# Directories to compare and sync
DIRECTORY_1 = os.getenv("DIRECTORY_1")
DIRECTORY_2 = os.getenv("DIRECTORY_2")

# Redfish API details from .env
IDRAC_USER = os.getenv("IDRAC_USER")
IDRAC_PASS = os.getenv("IDRAC_PASS")
IDRAC_HOST = os.getenv("IDRAC_HOST")
ENABLE_IDRAC = os.getenv("ENABLE_IDRAC", "FALSE").upper()

# WOL Configurations
ENABLE_WOL = os.getenv("ENABLE_WOL", "False").lower() == "true"
TARGET_MAC = os.getenv("TARGET_MAC")
TARGET_IP = os.getenv("TARGET_IP", "255.255.255.255")  # Default to broadcast
TARGET_PORT = int(os.getenv("TARGET_PORT", 9))


# File path for logs
LOG_PATH = os.getenv("LOG_PATH")
LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG").upper()

# Map the log level string to actual logging levels
LOG_LEVEL_MAPPING = {
    'CRITICAL': logging.CRITICAL,
    'ERROR': logging.ERROR,
    'WARNING': logging.WARNING,
    'INFO': logging.INFO,
    'DEBUG': logging.DEBUG,
    'NOTSET': logging.NOTSET
}

required_env_vars = ["DIRECTORY_1", "DIRECTORY_2", "LOG_PATH", "LOG_LEVEL"]
missing_vars = [var for var in required_env_vars if not os.getenv(var)]

if missing_vars:
    raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")

# Default to DEBUG if the provided LOG_LEVEL isn't valid
log_level = LOG_LEVEL_MAPPING.get(LOG_LEVEL, logging.DEBUG)

# Setup Logging
logging.basicConfig(
    filename=f"{LOG_PATH}/directory_cleanup_log_{time.strftime('%Y-%m-%d_%H-%M-%S')}.log",
    level=log_level,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def send_wol_packet(mac_address):
    """Send a Wake-On-LAN magic packet to a specific MAC address."""
    if not mac_address:
        logging.error("No MAC address provided for WOL. Skipping WOL.")
        return

    mac_address = mac_address.replace(":", "").replace("-", "")
    if len(mac_address) != 12:
        raise ValueError("Invalid MAC address format")

    # Create the magic packet
    data = b"FF" * 6 + (mac_address * 16).encode()
    magic_packet = bytes.fromhex(data.decode())

    # Send the packet
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.sendto(magic_packet, (TARGET_IP, TARGET_PORT))
        logging.info(f"Magic packet sent to {mac_address} via {TARGET_IP}:{TARGET_PORT}")
    except Exception as e:
        logging.error(f"Failed to send WOL packet: {e}")

def shutdown_machine():
    system = platform.system()
    if system == "Windows":
        os.system("shutdown /s /t 0")
    elif system in ("Linux", "Darwin"):  # Linux or macOS
        os.system("sudo shutdown now")
    else:
        logging.info(f"Unsupported OS: {system}")


# Function to power on the Dell server
def power_on_server():
    url = f"{IDRAC_HOST}/redfish/v1/Systems/System.Embedded.1/Actions/ComputerSystem.Reset"
    payload = {"ResetType": "On"}
    max_retries = 12 # 12 retries * 5 seconds = 60 seconds
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            response = requests.post(url, json=payload, auth=(IDRAC_USER, IDRAC_PASS), verify=False)
            
            if response.status_code == 204:
                logging.debug("Power-on command sent successfully.")
                print("Giving time for the server to boot!")
                time.sleep(360)
                return
            elif response.status_code == 409:
                logging.debug("Server is already powered on.")
                break
            else:
                logging.warning(f"Unexpected response: {response.status_code}, {response.text}")
            
            # Wait for a short duration before sending the next request
            retry_count += 1
            time.sleep(5)
        except requests.RequestException as e:
            logging.error(f"Error while sending power-on request: {e}")
            retry_count += 1
            time.sleep(5)  # Retry after a delay
    logging.error("Failed to power on Dell server. Exiting script.")

# Function to power off the Dell server
def power_off_server():
    url = f"{IDRAC_HOST}/redfish/v1/Systems/System.Embedded.1/Actions/ComputerSystem.Reset"
    payload = {"ResetType": "ForceOff"}
    max_retries = 5
    
    for attempt in range(max_retries):
        try:
            response = requests.post(url, json=payload, auth=(IDRAC_USER, IDRAC_PASS), verify=False)
            if response.status_code == 204:
                logging.debug("Dell server powered off successfully.")
                return
            logging.warning(f"Attempt {attempt + 1}: Unexpected response - {response.status_code}, {response.text}")
        except requests.RequestException as e:
            logging.error(f"Attempt {attempt + 1}: Error while powering off server: {e}")
        time.sleep(5)
    logging.error("Failed to power off Dell server after retries.")


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

    # Step 1: Handle WOL if enabled
    if ENABLE_WOL == "TRUE":
        try:
            logging.info("WOL mode enabled. Attempting to power on the Dell server.")
            send_wol_packet(TARGET_MAC)
            logging.info("WOL packet sent successfully. Waiting for the server to boot.")
            time.sleep(30)  # Wait for the server to power on (adjust as needed)
        except Exception as e:
            logging.error(f"Error during WOL execution: {e}")
            return  # Exit script if WOL fails

    # Step 2: Handle iDRAC if enabled
    if ENABLE_IDRAC == "TRUE":
        try:
            logging.info("IDRAC mode enabled. Powering on the Dell server.")
            power_on_server()
        except Exception as e:
            logging.error(f"Error during iDRAC power-on: {e}")
            return  # Exit script if iDRAC fails

    # Step 3: Perform synchronization
    try:
        logging.info("Starting directory synchronization.")
        sync_directories_with_rclone()
        logging.info("Directory synchronization completed successfully.")
    except Exception as e:
        logging.error(f"An error occurred during synchronization: {e}")
        return  # Exit script if synchronization fails

    # Step 4: Handle shutdown if WOL or iDRAC was used
    try:
        if ENABLE_WOL == "TRUE":
            logging.info("WOL mode enabled. Sending shutdown magic packet.")
            shutdown_machine()
        if ENABLE_IDRAC == "TRUE":
            logging.info("IDRAC mode enabled. Powering off the Dell server.")
            power_off_server()
    except Exception as e:
        logging.error(f"Error during server shutdown: {e}")

    logging.info("Rclone transfer script completed successfully.")

# Run the script
if __name__ == "__main__":
    main()
