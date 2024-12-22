import os
import time
import psutil
import logging
import shutil
from tqdm import tqdm
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed

# Load environment variables from a .env file
load_dotenv()

# Directories to compare and sync
DIRECTORY_1 = os.getenv("DIRECTORY_1")
DIRECTORY_2 = os.getenv("DIRECTORY_2")

# File path for logs
LOG_PATH = os.getenv("LOG_PATH")

# Setup Logging
logging.basicConfig(
    filename=f"{LOG_PATH}/file_transfer_log_{time.strftime('%Y-%m-%d_%H-%M-%S')}.log",  # Formatted with current time
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'  
)

# Function to determine system resources and set max_workers
def get_max_workers():
    """Dynamically calculate the number of worker threads based on system resources."""
    # Get the number of available CPU cores
    cpu_cores = psutil.cpu_count(logical=True)
    
    # Get available memory (in GB)
    available_memory = psutil.virtual_memory().available / (1024 ** 3)  # Convert to GB
    
    # A simple heuristic: use up to 75% of the CPU cores or 4, whichever is less, based on available memory
    max_cpu_threads = max(1, int(cpu_cores * 0.75))  # Use 75% of the CPU threads
    if available_memory < 8:  # If less than 8GB of available memory, reduce workers
        max_workers = max(1, max_cpu_threads // 2)
    else:
        max_workers = max_cpu_threads  # Use the full available CPU threads
    
    logging.info(f"System Resources: {cpu_cores} CPU cores, {available_memory:.2f} GB memory")
    logging.info(f"Max Workers set to: {max_workers}")
    
    return max_workers

def hash_file(filepath):
    """Generate a SHA-256 hash of the file contents for comparison."""
    import hashlib
    hasher = hashlib.sha256()
    try:
        with open(filepath, 'rb') as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
    except Exception as e:
        logging.error(f"Error hashing file {filepath}: {e}")
        return None
    return hasher.hexdigest()

def files_are_equal(file1, file2):
    """Compare two files to check if they are identical."""
    try:
        stat1 = os.stat(file1)
        stat2 = os.stat(file2)
        if stat1.st_size != stat2.st_size:
            return False
        
        # Use hash comparison for accuracy
        hash1 = hash_file(file1)
        hash2 = hash_file(file2)
        if hash1 is None or hash2 is None:
            logging.error(f"Hash comparison failed for files: {file1}, {file2}")
            return False
        return hash1 == hash2
    except Exception as e:
        logging.error(f"Error comparing files {file1} and {file2}: {e}")
        return False

def sync_file(src_file, dest_file, files_copied):
    """Compare and copy a single file if necessary."""
    try:
        # Compare files and log actions
        if os.path.exists(dest_file) and files_are_equal(src_file, dest_file):
            logging.debug(f"Skipping identical file: {src_file}")
        else:
            logging.info(f"Copying {src_file} to {dest_file}")
            shutil.copy2(src_file, dest_file)
            files_copied[0] += 1  # Increment the copied files counter
    except Exception as file_error:
        logging.error(f"Error copying {src_file}: {file_error}")

def sync_directories():
    """Synchronize contents of two directories. Copies missing or updated files from src_dir to dest_dir."""
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

    total_files = sum(len(files) for _, _, files in os.walk(DIRECTORY_1))
    
    # Track number of files copied
    files_copied = [0]  # List to allow mutation inside the sync_file function
    
    # Get dynamically calculated max_workers
    max_workers = get_max_workers()
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:  # Set number of workers dynamically
        futures = []
        with tqdm(total=total_files, desc="Syncing Directories", unit="file") as progress:
            for root, _, files in os.walk(DIRECTORY_1):
                rel_path = os.path.relpath(root, DIRECTORY_1)
                dest_subdir = os.path.join(DIRECTORY_2, rel_path)

                if not os.path.exists(dest_subdir):
                    os.makedirs(dest_subdir)

                for file_name in files:
                    src_file = os.path.join(root, file_name)
                    dest_file = os.path.join(dest_subdir, file_name)

                    # Submit the file copy task to the thread pool, passing files_copied
                    futures.append(executor.submit(sync_file, src_file, dest_file, files_copied))
            
            for _ in as_completed(futures):
                progress.update(1)

    logging.info(f"Directory synchronization complete. Files copied: {files_copied[0]}")

def main():
    logging.debug("Starting the script...")

    try:
        # Synchronize directories
        logging.debug(f"Starting synchronization: {DIRECTORY_1} -> {DIRECTORY_2}")
        sync_directories()

    except Exception as e:
        logging.error(f"An unexpected error occurred in the main logic: {e}")

# Run the script
if __name__ == "__main__":
    main()
