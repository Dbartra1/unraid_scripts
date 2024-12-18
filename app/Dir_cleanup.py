import os
import time
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Directories to check
directories = [
    os.getenv('DIRECTORY_1'),
    os.getenv('DIRECTORY_2'),
    os.getenv('DIRECTORY_3'),
    os.getenv('DIRECTORY_4')
]

# File path for logs
LOG_PATH = os.getenv("LOG_PATH")

# Validate LOG_PATH
if not LOG_PATH or not os.path.isdir(LOG_PATH):
    raise ValueError(f"Invalid LOG_PATH: {LOG_PATH}. Please set a valid path in your .env file.")

# Media file extensions
MEDIA_EXTENSIONS = {'.mkv', '.mp4', '.mp3', '.wav', '.flac', '.avi', '.mov'}

# Setup Logging
logging.basicConfig(
    filename=f"{LOG_PATH}/directory_cleanup_log_{time.strftime('%Y-%m-%d_%H-%M-%S')}.log",
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def contains_only_non_media_files(directory):
    """Check if a directory contains only non-media files."""
    for entry in os.listdir(directory):
        full_path = os.path.join(directory, entry)
        if os.path.isfile(full_path):
            _, ext = os.path.splitext(full_path)
            if ext.lower() in MEDIA_EXTENSIONS:
                logging.debug(f"Media file detected: {full_path}")
                return False  # Found a media file
    return True  # No media files found

def remove_empty_dirs(directory, is_root=False, deleted_count=[0]):
    """Recursively remove empty or non-media directories."""
    logging.debug(f"Processing directory: {directory}")
    is_empty = True  # Assume the directory is empty unless files or non-empty subdirectories are found

    try:
        for entry in os.listdir(directory):
            full_path = os.path.join(directory, entry)
            logging.debug(f"Found entry: {full_path}")

            if os.path.isdir(full_path):
                logging.debug(f"Entering subdirectory: {full_path}")
                if not remove_empty_dirs(full_path, deleted_count=deleted_count):
                    is_empty = False
            else:
                _, ext = os.path.splitext(full_path)
                if ext.lower() in MEDIA_EXTENSIONS:
                    logging.debug(f"Media file found: {full_path}")
                    is_empty = False
                else:
                    # Delete non-media files
                    try:
                        os.remove(full_path)
                        logging.info(f"Deleted file: {full_path}")
                    except OSError as e:
                        logging.error(f"Failed to delete file {full_path}: {e}")
                        is_empty = False

        # If the directory is now empty, attempt to remove it
        if is_empty or not contains_only_non_media_files(directory):
            if not is_root:  # Do not delete the root working directory
                try:
                    os.rmdir(directory)
                    logging.info(f"Removed directory: {directory}")
                    deleted_count[0] += 1  # Increment the count
                    return True  # Directory was removed
                except OSError as e:
                    logging.error(f"Failed to remove {directory}: {e}")
                    return False
        else:
            is_empty = False
    except FileNotFoundError:
        logging.warning(f"Directory not found or inaccessible: {directory}")
        is_empty = False
    except PermissionError:
        logging.error(f"Permission denied for directory: {directory}")
        is_empty = False
    except Exception as e:
        logging.error(f"Unexpected error while processing {directory}: {e}")
        is_empty = False

    logging.debug(f"Finished processing directory: {directory}, is_empty: {is_empty}")
    return is_empty


def check_and_clean_directories(directories):
    """Check and clean all provided directories."""
    total_dirs_processed = 0
    deleted_count = [0]  # Use a mutable object to share count across recursive calls

    for directory in directories:
        if directory and os.path.exists(directory):
            logging.info(f"Checking directory: {directory}")
            remove_empty_dirs(directory, is_root=True, deleted_count=deleted_count)
            total_dirs_processed += 1
        else:
            logging.warning(f"Invalid or non-existent directory: {directory}")
            
    logging.info(f"Total directories processed: {total_dirs_processed}")
    logging.info(f"Total directories deleted: {deleted_count[0]}")

# Execute the script
if __name__ == "__main__":
    logging.info("Starting directory cleanup process...")
    check_and_clean_directories(directories)
    logging.info("Directory cleanup process completed.")

