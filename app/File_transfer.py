import os
import time
import requests
import logging
import shutil
from tqdm import tqdm
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Redfish API details from .env
IDRAC_USER = os.getenv("IDRAC_USER")
IDRAC_PASS = os.getenv("IDRAC_PASS")
IDRAC_HOST = os.getenv("IDRAC_HOST")

# Directories to compare and sync
DIRECTORY_1 = os.getenv("DIRECTORY_1")
DIRECTORY_2 = os.getenv("DIRECTORY_2")

# File path for logs
LOG_PATH = os.getenv("LOG_PATH")

# Setup Logging
logging.basicConfig(
    filename=f"{LOG_PATH}/file_transfer_log_{time.strftime('%Y-%m-%d_%H-%M-%S')}.log",  # Formatted with current time
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',  # Correct format string
    datefmt='%Y-%m-%d %H:%M:%S'  # Time format for the log timestamps
)

# Function to power on the Dell server
def power_on_server():
    url = f"{IDRAC_HOST}/redfish/v1/Systems/System.Embedded.1/Actions/ComputerSystem.Reset"
    payload = {"ResetType": "On"}
    
    while True:
        try:
            response = requests.post(url, json=payload, auth=(IDRAC_USER, IDRAC_PASS), verify=False)
            
            if response.status_code == 204:
                logging.debug("Power-on command sent successfully.")
                print("Giving time for the server to boot!")
                time.sleep(360)
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


def sync_directories():
    """
    Synchronize contents of two directories. Copies missing or updated files from src_dir to dest_dir.
    """
    if not os.path.exists(DIRECTORY_2):
        logging.info(f"Destination directory {DIRECTORY_2} does not exist. Creating it.")
        os.makedirs(DIRECTORY_2)

    files_copied = False  # Flag to track if any file is copied

    try:
        # Get the list of all files and directories in source directory
        total_files = sum(len(files) for _, _, files in os.walk(DIRECTORY_1))
        with tqdm(total=total_files, desc="Syncing Directories", unit="file") as progress:
            for root, _, files in os.walk(DIRECTORY_1):
                # Relative path from source directory
                rel_path = os.path.relpath(root, DIRECTORY_1)
                dest_subdir = os.path.join(DIRECTORY_2, rel_path)

                # Ensure the subdirectory exists in the destination
                if not os.path.exists(dest_subdir):
                    logging.debug(f"Creating directory: {dest_subdir}")
                    os.makedirs(dest_subdir)

                for file_name in files:
                    src_file = os.path.join(root, file_name)
                    dest_file = os.path.join(dest_subdir, file_name)

                    try:
                        # Compare files by size and modification time for performance
                        if not os.path.exists(dest_file) or not files_are_equal(src_file, dest_file):
                            logging.info(f"Copying {src_file} to {dest_file}")
                            shutil.copy2(src_file, dest_file)
                            files_copied = True
                    except Exception as file_error:
                        logging.error(f"Error copying {src_file}: {file_error}")
                    finally:
                        progress.update(1)

        if not files_copied:
            logging.info("No differences found between the directories. No files were copied.")
        else:
            logging.info("Directory synchronization complete.")

    except Exception as e:
        logging.error(f"An error occurred during synchronization: {e}")

def files_are_equal(file1, file2):
    """
    Compare two files by size and modification time. Use content comparison as a fallback.
    """
    try:
        stat1 = os.stat(file1)
        stat2 = os.stat(file2)
        return stat1.st_size == stat2.st_size and stat1.st_mtime == stat2.st_mtime
    except Exception as e:
        logging.error(f"Error comparing files {file1} and {file2}: {e}")
        return False

""" # This is a function that is the same as the sync function above, but adds a delete to the source directory if there is no differences in the two directories. This assumes there was a successful sync. 
def sync_directories_delete():
    
    Synchronize contents of two directories. Copies missing or updated files from src_dir to dest_dir.
    Deletes the source directory if both directories are identical after sync.
    
    if not os.path.exists(DIRECTORY_2):
        logging.info(f"Destination directory {DIRECTORY_2} does not exist. Creating it.")
        os.makedirs(DIRECTORY_2)

    try:
        # Synchronize files
        directories_identical = True
        for root, _, files in os.walk(DIRECTORY_1):
            rel_path = os.path.relpath(root, DIRECTORY_1)
            dest_subdir = os.path.join(DIRECTORY_2, rel_path)

            if not os.path.exists(dest_subdir):
                logging.debug(f"Creating directory: {dest_subdir}")
                os.makedirs(dest_subdir)

            for file_name in tqdm(files, desc=f"Syncing {rel_path}", unit="file"):
                src_file = os.path.join(root, file_name)
                dest_file = os.path.join(dest_subdir, file_name)

                if not os.path.exists(dest_file) or not filecmp.cmp(src_file, dest_file, shallow=False):
                    logging.info(f"Copying {src_file} to {dest_file}")
                    shutil.copy2(src_file, dest_file)
                    directories_identical = False  # A difference was found and resolved

        if directories_identical:
            logging.info("Directories are identical. Deleting the source directory.")
            shutil.rmtree(DIRECTORY_1)
        else:
            logging.info("Directories synchronized, but some files were updated.")
    except Exception as e:
        logging.error(f"An error occurred during synchronization: {e}")
 """

def main():
    logging.debug("Starting the script...")

    try:
        # Step 1: Power on the Dell server
        logging.debug("Checking Dell server power status...")
        power_on_server()

        # Step 2: Synchronize directories
        logging.debug(f"Starting synchronization: {DIRECTORY_1} -> {DIRECTORY_2}")
        sync_directories()

        # Step 3: Shut down the Dell server gracefully
        logging.debug("Synchronization complete. Powering off Dell server.")
        power_off_server()
    except Exception as e:
        logging.error(f"An unexpected error occurred in the main logic: {e}")


# Run the script
if __name__ == "__main__":
    main()


## Notes: I think that this should be run weekly as it can be a big operation depending on the amount of files to move. This can be run more frequently, but it will just return a 