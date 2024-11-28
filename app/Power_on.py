import requests
import logging
import pdb as p
import time as t

# Setup Logging
logging.basicConfig(
    filename="poweron_log.log",
    encoding="utf-8",
    filemode="a",
    format="{asctime} - {levelname} - {message}",
    style="{",
    datefmt="%Y-%m-%d %H:%M",
    level=logging.INFO
)

# Redfish API details
IDRAC_HOST = ''
USERNAME = ''
PASSWORD = ''

# Plex API details
PLEX_URL = ""
PLEX_TOKEN = ""

# Function to power on the server
def power_on_server():
    url = f"{IDRAC_HOST}/redfish/v1/Systems/System.Embedded.1/Actions/ComputerSystem.Reset"
    payload = {"ResetType": "On"}
    try:
        response = requests.post(url, json=payload, auth=(USERNAME, PASSWORD), verify=False)
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
    url = f"{PLEX_URL}?X-Plex-Token={PLEX_TOKEN}"
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

# Main Execution
if __name__ == "__main__":
    if has_active_sessions():
        p.set_trace()  # Optional: Remove for production unless debugging
        print("Plex traffic detected. Attempting to power on the server.")
        logging.info("Plex traffic detected. Attempting to power on the server.")
        power_on_server()
    else:
        print("No Plex traffic detected. No action required.")
        logging.info("No Plex traffic detected. No action required.")
