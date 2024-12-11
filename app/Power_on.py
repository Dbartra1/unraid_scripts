import os
import requests
import logging
import time as t
from dotenv import load_dotenv

load_dotenv()

# Redfish API details from .env
IDRAC_USER = os.getenv("IDRAC_USER")
IDRAC_PASS = os.getenv("IDRAC_PASS")
IDRAC_HOST = os.getenv("IDRAC_HOST")

# PLEX API details from .env
PLEX_API_URL = os.getenv("PLEX_API_URL")
PLEX_API_TOKEN = os.getenv("PLEX_API_TOKEN")

# File path for logs
LOG_PATH = os.getenv("LOG_PATH")

logging.basicConfig(
    filename=f"{LOG_PATH}/power_off_log_{t.strftime('%Y-%m-%d_%H-%M-%S')}.log",  # Formatted with current time
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',  # Correct format string
    datefmt='%Y-%m-%d %H:%M:%S'  # Time format for the log timestamps
)

def power_on_server():
    url = f"{IDRAC_HOST}/redfish/v1/Systems/System.Embedded.1/Actions/ComputerSystem.Reset"
    payload = {"ResetType": "On"}
    try:
        response = requests.post(url, json=payload, auth=(IDRAC_USER, IDRAC_PASS), verify=False)
        t.sleep(320)  # Sleep for 320 seconds after the power-on request (may want to shorten)
        if response.status_code == 200:
            print("Server powered on successfully.")
            logging.info("Server powered on successfully.")
        else:
            print(f"Failed to power on: {response.status_code}, {response.text}")
            logging.error(f"Failed to power on: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"Exception occurred while powering on the server: {e}")
        logging.error(f"Exception occurred while powering on the server: {e}")

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

if __name__ == "__main__":
    if has_active_sessions():
        print("Plex traffic detected. Attempting to power on the server.")
        logging.info("Plex traffic detected. Attempting to power on the server.")
        power_on_server()
    else:
        print("No Plex traffic detected. No action required.")
        logging.info("No Plex traffic detected. No action required.")
