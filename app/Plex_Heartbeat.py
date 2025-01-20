import os
import time
import logging
import requests
import re
import socket
import platform
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed

"""_summary_
This is an experimental script that looks for active Plex sessions and performs a series of actions based on the results.
The script can be configured to:    
1. Power on a Dell server using iDRAC.
2. Send a Wake-On-LAN (WOL) packet to a target machine.

Due to the nature of monitoring inbound network traffic, the script is designed to be run on a machine that is always on.
Monitoring inbound traffic on a machine that is powered off will not be possible. This will require a proxy server such as a Raspberry Pi.
The nature of peoples network topology will vary, so the script may need to be modified to suit individual needs.
THERE IS NO GUARANTEE THAT THIS SCRIPT WILL WORK FOR EVERYONE.
"""

load_dotenv()

# Idle Timeout in seconds before shutting down the server
IDLE_TIMEOUT = int(os.getenv("IDLE_TIMEOUT", 300))

# Redfish API details from .env
IDRAC_USER = os.getenv("IDRAC_USER")
IDRAC_PASS = os.getenv("IDRAC_PASS")
IDRAC_HOST = os.getenv("IDRAC_HOST")
ENABLE_IDRAC = os.getenv("ENABLE_IDRAC", "FALSE").upper()

if ENABLE_IDRAC == "TRUE" and not all([IDRAC_USER, IDRAC_PASS, IDRAC_HOST]):
    raise EnvironmentError("Missing iDRAC configurations. Please provide IDRAC_USER, IDRAC_PASS, and IDRAC_HOST.")

# WOL Configurations
ENABLE_WOL = os.getenv("ENABLE_WOL", "False").lower() == "true"
TARGET_MAC = os.getenv("TARGET_MAC")
TARGET_IP = os.getenv("TARGET_IP", "255.255.255.255")  # Default to broadcast
TARGET_PORT = int(os.getenv("TARGET_PORT", 9))

if ENABLE_WOL == "TRUE" and not all([TARGET_MAC, TARGET_IP, TARGET_PORT]):
    raise ValueError("Missing WOL configurations. Please provide TARGET_MAC, TARGET_IP, and TARGET_PORT.")

# PLEX API details from .env
PLEX_API_URL = os.getenv("PLEX_API_URL")
PLEX_API_TOKEN = os.getenv("PLEX_API_TOKEN")

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
log_level = LOG_LEVEL_MAPPING.get(LOG_LEVEL, logging.INFO)

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
    
    if not re.match(r"([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})", mac_address):
        raise ValueError("Invalid MAC address format. Must be in the format 'XX:XX:XX:XX:XX:XX' or 'XX-XX-XX-XX-XX-XX'")

    mac_address = mac_address.replace(":", "").replace("-", "").upper()
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
        logging.debug(f"Magic packet sent to {TARGET_IP}:{TARGET_PORT}")
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

# Function to check if there are active Plex sessions
def has_active_sessions():
    session_data = get_plex_sessions_with_retries()
    if session_data and "MediaContainer" in session_data:
        return session_data["MediaContainer"].get("size", 0) > 0
    return False

# Function to retrieve Plex session data
def get_plex_sessions():
    url = f"{PLEX_API_URL}?X-Plex-Token={PLEX_API_TOKEN}"
    response = requests.get(url)
    if response.status_code == 200:
        print("Plex session data retrieved successfully.")
        return response.json()
    else:
        print(f"Failed to retrieve sessions: {response.status_code}, {response.text}")
        logging.error(f"Failed to retrieve sessions: {response.status_code}, {response.text}")
        return None

# Function with retries to fetch Plex session data
def get_plex_sessions_with_retries(retries=3, delay=5):
    for _ in range(retries):
        session_data = get_plex_sessions()
        if session_data:
            return session_data
        t.sleep(delay)
    return None

def main():
    logging.debug("Starting the Plex heartbeat monitor...")

    if has_active_sessions():
        logging.info("Active Plex sessions detected. Ensuring the server is powered on.")
        
        # Step 1: Attempt to power on the server
        try:
            if ENABLE_WOL:
                send_wol_packet(TARGET_MAC)
                logging.info("WOL packet sent successfully. Waiting for the server to boot.")
                time.sleep(30)  # Adjust boot time as needed
            
            if ENABLE_IDRAC:
                power_on_server()
                logging.info("Server powered on successfully using iDRAC.")
        except Exception as e:
            logging.error(f"Error during server power-on: {e}")
            return  # Exit script if server power-on fails
        
        # Step 2: Monitor Plex activity
        logging.info("Monitoring Plex sessions...")
        while True:
            if has_active_sessions():
                logging.info("Active Plex sessions ongoing. Server remains powered on.")
                time.sleep(60)  # Polling interval
            else:
                logging.info("No active Plex sessions detected. Starting idle countdown.")
                
                # Grace period logic
                idle_start_time = time.time()
                while time.time() - idle_start_time < IDLE_TIMEOUT:
                    if has_active_sessions():
                        logging.info("Activity resumed during grace period. Resetting idle timer.")
                        idle_start_time = time.time()  # Reset idle timer
                    time.sleep(60)  # Polling interval during grace period
                
                # If no activity resumes during the grace period, proceed to shutdown
                logging.info(f"No activity detected for {IDLE_TIMEOUT} seconds. Proceeding to shut down the server.")
                break
            
        # Step 3: No active sessions detected, shut down the server
        logging.info("No active Plex sessions detected. Proceeding to shut down the server.")
        try:
            if ENABLE_WOL:
                shutdown_machine()
                logging.info("Shutdown command issued via WOL.")
            if ENABLE_IDRAC:
                power_off_server()
                logging.info("Shutdown command issued via iDRAC.")
        except Exception as e:
            logging.error(f"Error during server shutdown: {e}")
    else:
        logging.info("No active Plex sessions detected. No action required.")

    logging.info("Plex heartbeat monitor script completed.")

if __name__ == "__main__":
    main()
