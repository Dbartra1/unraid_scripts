import os
import time
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Directories to check
directories = [
    os.getenv('CLEANUP_DIRECTORY_1'),
    os.getenv('CLEANUP_DIRECTORY_2'),
    os.getenv('CLEANUP_DIRECTORY_3'),
    os.getenv('CLEANUP_DIRECTORY_4')
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

def list_media_directories(directory, media_dirs, depth=0, max_depth=10):
    """List directories containing media files."""
    if depth > max_depth:
        logging.warning(f"Max recursion depth reached at: {directory}")
        return

    has_media = False
    for entry in os.scandir(directory):
        full_path = entry.path
        if entry.is_file():
            _, ext = os.path.splitext(entry.name)
            if ext.lower() in MEDIA_EXTENSIONS:
                has_media = True
        elif entry.is_dir():
            list_media_directories(full_path, media_dirs, depth=depth+1, max_depth=max_depth)

    if has_media:
        media_dirs.append(directory)

def remove_empty_dirs(directory, is_root=False, deleted_count=None):
    """Recursively remove empty directories and non-media files."""
    if deleted_count is None:
        deleted_count = [0]

    is_empty = True
    for entry in os.scandir(directory):
        full_path = entry.path
        if entry.is_dir():
            if not remove_empty_dirs(full_path, deleted_count=deleted_count):
                is_empty = False
        elif entry.is_file():
            _, ext = os.path.splitext(entry.name)
            if ext.lower() not in MEDIA_EXTENSIONS:
                try:
                    os.remove(full_path)
                    logging.info(f"Deleted file: {full_path}")
                except OSError as e:
                    logging.error(f"Failed to delete file {full_path}: {e}")
                    is_empty = False
            else:
                is_empty = False

    if is_empty and not is_root:
        try:
            os.rmdir(directory)
            logging.info(f"Removed directory: {directory}")
            deleted_count[0] += 1
            return True
        except OSError as e:
            logging.error(f"Failed to remove directory {directory}: {e}")
    return False


def check_and_clean_directories(directories):
    """Main function to check and clean directories."""
    total_dirs_processed = 0
    deleted_count = [0]
    media_dirs = []

    for directory in directories:
        if directory and os.path.exists(directory):
            logging.info(f"Checking directory: {directory}")
            list_media_directories(directory, media_dirs)
            remove_empty_dirs(directory, is_root=True, deleted_count=deleted_count)
            total_dirs_processed += 1
        else:
            logging.warning(f"Invalid or non-existent directory: {directory}")

    logging.info(f"Total directories processed: {total_dirs_processed}")
    logging.info(f"Total directories deleted: {deleted_count[0]}")
    logging.info("Directories containing media files:")
    for media_dir in media_dirs:
        logging.info(media_dir)

def main():
    """Entry point for the script."""
    logging.info("Starting directory cleanup process...")
    check_and_clean_directories(directories)
    logging.info("Directory cleanup process completed.")

if __name__ == "__main__":
    main()
