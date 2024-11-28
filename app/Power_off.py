import os
import requests
import logging
import time as t
import pdb as p
from dotenv import load_dotenv

# Setup Logging
logging.basicConfig(
    filename="poweroff_log.log",
    encoding="utf-8",
    filemode="a",
    format="{asctime} - {levelname} - {message}",
    style="{",
    datefmt="%Y-%m-%d %H:%M",
    level=logging.INFO
)

# Load environment variables from a .env file
load_dotenv()

# Redfish API details from .env
IDRAC_USER = os.getenv("IDRAC_USER")
IDRAC_PASS = os.getenv("IDRAC_PASS")
IDRAC_HOST = os.getenv("IDRAC_HOST")

# PLEX API details from .env
PLEX_API_URL = os.getenv("PLEX_API_URL")
PLEX_API_TOKEN = os.getenv("PLEX_API_TOKEN")

# Settings
MONITOR_DURATION = 30  # Duration in seconds to monitor Plex traffic


# Function to get Plex session data with retries
def get_plex_sessions_with_retries(retries=3, delay=5):
    for _ in range(retries):
        session_data = get_plex_sessions()
        if session_data:
            return session_data
        t.sleep(delay)
    return None

# Function to retrieve Plex session data
def get_plex_sessions():
    url = f"{PLEX_API_URL}?X-Plex-Token={PLEX_API_TOKEN}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print("Plex session data retrieved successfully.")
            logging.info("Plex session data retrieved successfully.")
            return response.json()
        else:
            print(f"Failed to retrieve sessions: {response.status_code}, {response.text}")
            logging.error(f"Failed to retrieve sessions: {response.status_code}, {response.text}")
            return None
    except Exception as e:
        print(f"Exception occurred while retrieving Plex sessions: {e}")
        logging.error(f"Exception occurred while retrieving Plex sessions: {e}")
        return None

# Function to check if there are active Plex sessions
def has_active_sessions():
    session_data = get_plex_sessions_with_retries()
    if session_data and "MediaContainer" in session_data:
        return session_data["MediaContainer"].get("size", 0) > 0
    return False


# Function to power off the server with retries
def power_off_server(retries=3, delay=5):
    url = f"{IDRAC_HOST}/redfish/v1/Systems/System.Embedded.1/Actions/ComputerSystem.Reset"
    payload = {"ResetType": "GracefulShutdown"}
    
    for attempt in range(retries):
        try:
            response = requests.post(url, json=payload, auth=(IDRAC_USER, IDRAC_PASS), verify=False)
            if response.status_code == 200:
                print("Server powered off successfully.")
                logging.info("Server powered off successfully.")
                return
            else:
                print(f"Failed to power off: {response.status_code}, {response.text}")
                logging.error(f"Failed to power off: {response.status_code}, {response.text}")
        except Exception as e:
            print(f"Exception occurred while powering off the server: {e}")
            logging.error(f"Exception occurred while powering off the server: {e}")
        
        # Retry logic with delay
        t.sleep(delay)

    print("Failed to power off the server after multiple attempts.")
    logging.error("Failed to power off the server after multiple attempts.")

# Function to check if the server is on
def is_server_on():
    url = f"{IDRAC_HOST}/redfish/v1/Systems/System.Embedded.1/"
    try:
        response = requests.get(url, auth=(IDRAC_USER, IDRAC_PASS), verify=False)
        if response.status_code == 200:
            power_state = response.json().get("PowerState", "Unknown")
            return power_state == "On"
        else:
            print(f"Failed to check server state: {response.status_code}, {response.text}")
            logging.error(f"Failed to check server state: {response.status_code}, {response.text}")
            return False
    except Exception as e:
        print(f"Exception occurred while checking server state: {e}")
        logging.error(f"Exception occurred while checking server state: {e}")
        return False

# Main execution
if __name__ == "__main__":
    # Debugging (remove or comment out if not needed)
    # p.set_trace()

    if has_active_sessions():
        print("Plex traffic detected. No action required.")
        logging.info("Plex traffic detected. No action required.")
    else:
        print("No Plex traffic detected.")
        logging.info("No Plex traffic detected.")
        if is_server_on():
            print("Shutting down the server...")
            logging.info("Shutting down the server...")
            power_off_server()
        else:
            print("Server is already off.")
            logging.info("Server is already off.")
