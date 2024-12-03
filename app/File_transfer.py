import os
import requests
import subprocess
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
    response = requests.post(url, json=payload, auth=(IDRAC_USER, IDRAC_PASS), verify=False)
    if response.status_code == 204:
        logging.debug("Dell server powered on successfully.")
    else:
        logging.error(f"Failed to power on Dell server: {response.status_code}, {response.text}")

# Function to power off the Dell server
def power_off_server():
    url = f"{IDRAC_HOST}/redfish/v1/Systems/System.Embedded.1/Actions/ComputerSystem.Reset"
    payload = {"ResetType": "ForceOff"}
    response = requests.post(url, json=payload, auth=(IDRAC_USER, IDRAC_PASS), verify=False)
    if response.status_code == 204:
        logging.debug("Dell server powered off successfully.")
    else:
        logging.error(f"Failed to power off Dell server: {response.status_code}, {response.text}")

# Function to compare directories on HP and Dell
def compare_directories():
    # List all files in both directories
    hp_files = set(os.listdir(DIRECTORY_1))
    dell_files = set(os.listdir(DIRECTORY_2))

    # Compare the files and return files missing on Dell
    missing_files = hp_files - dell_files
    logging.debug(f"Files missing on Dell: {missing_files}")
    return missing_files

# Function to transfer missing files from HP to Dell
def transfer_files(missing_files):
    for file in missing_files:
        src_file = os.path.join(DIRECTORY_1, file)
        dest_file = os.path.join(DIRECTORY_2, file)
        
        # Use rsync or scp to transfer files
        # Using rsync for efficiency and resumability
        command = f"rsync -avz {src_file} user@dell_ip:{dest_file}"
        logging.debug(f"Transferring file: {src_file} to {dest_file}")
        
        result = subprocess.run(command, shell=True, capture_output=True)
        
        if result.returncode == 0:
            logging.debug(f"Successfully transferred {file}.")
        else:
            logging.error(f"Failed to transfer {file}: {result.stderr.decode()}")

# This is the same function as above, just with a loading bar because it is a large operation that can take hours
def transfer_files(missing_files):
    with tqdm(total=len(missing_files), desc="Transferring Files", unit="file") as pbar:
        for file in missing_files:
            src_file = os.path.join(DIRECTORY_1, file)
            dest_file = os.path.join(DIRECTORY_2, file)
            
            # Use rsync for efficient file transfer
            command = f"rsync -avz {src_file} user@dell_ip:{dest_file}"
            logging.debug(f"Transferring file: {src_file} to {dest_file}")
            
            result = subprocess.run(command, shell=True, capture_output=True)
            
            if result.returncode == 0:
                logging.debug(f"Successfully transferred {file}.")
            else:
                logging.error(f"Failed to transfer {file}: {result.stderr.decode()}")
            
            # Update the progress bar
            pbar.update(1)


# Main logic
def main():
    # Step 1: Power on the Dell server
    logging.debug("Checking Dell server power status...")
    power_on_server()
    
    # Wait for Dell to fully power on before proceeding
    time.sleep(360)  # Adjust based on your server's boot time
    
    # Compare directories and identify missing files
    logging.debug("Comparing directories on HP and Dell...")
    missing_files = compare_directories()
    
    if missing_files:
        # Step 3: Transfer missing files to Dell
        logging.debug("Missing files detected, transferring...")
        transfer_files(missing_files)
    else:
        logging.debug("No missing files found. Nothing to transfer.")
    
    # Step 4: Shut down the Dell server gracefully
    logging.debug("Transfer complete, powering off Dell server.")
    power_off_server()

# Run the script
if __name__ == "__main__":
    main()
