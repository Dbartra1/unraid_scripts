import os
import requests
import subprocess
import time
import logging

# Setup Logging
logging.basicConfig(
    filename='/path/to/your/logfile.log',
    level=logging.DEBUG,
    format='{asctime} - {levelname} - {message}',
    style='{',
    datefmt='%Y-%m-%d %H:%M'
)

# Redfish API details
IDRAC_HOST = 'https://192.168.0.40'
USERNAME = 'root'
PASSWORD = 'yourpassword'

# Directories to compare and sync
HP_DIRECTORY = '/mnt/user/your_hp_directory'
DELL_DIRECTORY = '/mnt/user/your_dell_directory'

# Function to power on the Dell server
def power_on_server():
    url = f"{IDRAC_HOST}/redfish/v1/Systems/System.Embedded.1/Actions/ComputerSystem.Reset"
    payload = {"ResetType": "On"}
    response = requests.post(url, json=payload, auth=(USERNAME, PASSWORD), verify=False)
    if response.status_code == 200:
        logging.debug("Dell server powered on successfully.")
    else:
        logging.error(f"Failed to power on Dell server: {response.status_code}, {response.text}")

# Function to power off the Dell server
def power_off_server():
    url = f"{IDRAC_HOST}/redfish/v1/Systems/System.Embedded.1/Actions/ComputerSystem.Reset"
    payload = {"ResetType": "ForceOff"}
    response = requests.post(url, json=payload, auth=(USERNAME, PASSWORD), verify=False)
    if response.status_code == 200:
        logging.debug("Dell server powered off successfully.")
    else:
        logging.error(f"Failed to power off Dell server: {response.status_code}, {response.text}")

# Function to compare directories on HP and Dell
def compare_directories():
    # List all files in both directories
    hp_files = set(os.listdir(HP_DIRECTORY))
    dell_files = set(os.listdir(DELL_DIRECTORY))

    # Compare the files and return files missing on Dell
    missing_files = hp_files - dell_files
    logging.debug(f"Files missing on Dell: {missing_files}")
    return missing_files

# Function to transfer missing files from HP to Dell
def transfer_files(missing_files):
    for file in missing_files:
        src_file = os.path.join(HP_DIRECTORY, file)
        dest_file = os.path.join(DELL_DIRECTORY, file)
        
        # Use rsync or scp to transfer files
        # Using rsync for efficiency and resumability
        command = f"rsync -avz {src_file} user@dell_ip:{dest_file}"
        logging.debug(f"Transferring file: {src_file} to {dest_file}")
        
        result = subprocess.run(command, shell=True, capture_output=True)
        
        if result.returncode == 0:
            logging.debug(f"Successfully transferred {file}.")
        else:
            logging.error(f"Failed to transfer {file}: {result.stderr.decode()}")

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
