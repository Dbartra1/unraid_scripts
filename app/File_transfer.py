import os
import requests
import time
import logging
from tqdm import tqdm
from dotenv import load_dotenv

# Setup Logging
logging.basicConfig(
    filename='C:\Users\dfbar\Documents\repos\github\unraid_scripts\logs', # This will need to change if put into a docker container/cloned to another machine for testing
    level=logging.DEBUG,
    format='{asctime} - {levelname} - {message}',
    style='{',
    datefmt='%Y-%m-%d %H:%M'
)

# Load environment variables from a .env file
load_dotenv()

# Redfish API details from .env
IDRAC_USER = os.getenv("IDRAC_USER")
IDRAC_PASS = os.getenv("IDRAC_PASS")
IDRAC_HOST = os.getenv("IDRAC_HOST")

# Directories to compare and sync
DIRECTORY_1 = os.getenv("DIRECTORY_1")
DIRECTORY_2 = os.getenv("DIRECTORY_2")

# Function to power on the Dell server
def power_on_server():
    url = f"{IDRAC_HOST}/redfish/v1/Systems/System.Embedded.1/Actions/ComputerSystem.Reset"
    payload = {"ResetType": "On"}
    
    while True:
        try:
            response = requests.post(url, json=payload, auth=(IDRAC_USER, IDRAC_PASS), verify=False)
            
            if response.status_code == 204:
                logging.debug("Power-on command sent successfully.")
            elif response.status_code == 409:
                logging.debug("Server is already powered on.")
                break
            else:
                logging.warning(f"Unexpected response: {response.status_code}, {response.text}")
            
            # Wait for a short duration before sending the next request
            time.sleep(5)
        except requests.RequestException as e:
            logging.error(f"Error while sending power-on request: {e}")
            time.sleep(5)  # Retry after a delay


# Function to power off the Dell server
def power_off_server():
    url = f"{IDRAC_HOST}/redfish/v1/Systems/System.Embedded.1/Actions/ComputerSystem.Reset"
    payload = {"ResetType": "ForceOff"}
    response = requests.post(url, json=payload, auth=(IDRAC_USER, IDRAC_PASS), verify=False)
    if response.status_code == 204:
        logging.debug("Dell server powered off successfully.")
    else:
        logging.error(f"Failed to power off Dell server: {response.status_code}, {response.text}")


# Function to sync the two directories 
def sync_directories():
    """
    Synchronize contents of two directories. Copies missing or updated files from src_dir to dest_dir.
    """
    if not os.path.exists(DIRECTORY_2):
        logging.info(f"Destination directory {DIRECTORY_2} does not exist. Creating it.")
        os.makedirs(DIRECTORY_2)

    try:
        # Get the list of files in both directories
        for root, _, files in os.walk(DIRECTORY_1):
            # Relative path from source directory
            rel_path = os.path.relpath(root, DIRECTORY_1)
            dest_subdir = os.path.join(DIRECTORY_2, rel_path)

            if not os.path.exists(dest_subdir):
                logging.debug(f"Creating directory: {dest_subdir}")
                os.makedirs(dest_subdir)

            # Compare files in current directory
            for file_name in tqdm(files, desc=f"Syncing {rel_path}", unit="file"):
                src_file = os.path.join(root, file_name)
                dest_file = os.path.join(dest_subdir, file_name)

                if not os.path.exists(dest_file) or not filecmp.cmp(src_file, dest_file, shallow=False):
                    logging.info(f"Copying {src_file} to {dest_file}")
                    shutil.copy2(src_file, dest_file)

        logging.info("Directory synchronization complete.")
    except Exception as e:
        logging.error(f"An error occurred: {e}")


# Main logic
def main():
    # Step 1: Power on the Dell server
    logging.debug("Checking Dell server power status...")
    power_on_server()
    
    # Wait for Dell to fully power on before proceeding
    time.sleep(360)  # Adjust based on your server's boot time
    
    sync_directories()
    
    # Step 4: Shut down the Dell server gracefully
    logging.debug("Transfer complete, powering off Dell server.")
    power_off_server()

# Run the script
if __name__ == "__main__":
    main()
