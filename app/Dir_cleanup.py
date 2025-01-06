import os
import time
import logging
from dotenv import load_dotenv

"""__summary__
This script is used to clean up specified directories, removing empty directories and non-media files. 
It logs the process and the directories containing media files. 
This is useful for use cases like cleaning up download directories on media servers and removing orphaned media directories and files within established media directories.
"""

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
LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG").upper()

# Map the log level string to actual logging levels
LOG_LEVEL_MAPPING = {
    'CRITICAL': logging.CRITICAL,
    'ERROR': logging.ERROR,
    'WARNING': logging.WARNING,
    'INFO': logging.INFO,
    'DEBUG': logging.DEBUG,
    'NOTSET': logging.NOTSET
}

required_env_vars = ["CLEANUP_DIRECTORY_1", "LOG_LEVEL", "LOG_PATH"]
missing_vars = [var for var in required_env_vars if not os.getenv(var)]

if missing_vars:
    raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")

# Validate LOG_PATH
if not LOG_PATH or not os.path.isdir(LOG_PATH):
    raise ValueError(f"Invalid LOG_PATH: {LOG_PATH}. Please set a valid path in your .env file.")

# Media file extensions
MEDIA_EXTENSIONS = {'.mkv', '.mp4', '.mp3', '.wav', '.flac', '.avi', '.mov'}

# Default to DEBUG if the provided LOG_LEVEL isn't valid
log_level = LOG_LEVEL_MAPPING.get(LOG_LEVEL, logging.DEBUG)

# Setup Logging
logging.basicConfig(
    filename=f"{LOG_PATH}/directory_cleanup_log_{time.strftime('%Y-%m-%d_%H-%M-%S')}.log",
    level=log_level,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def process_directory(directory, media_dirs, deleted_count, depth=0, max_depth=10):
    """Process a directory to identify media and clean non-media files."""
    if depth > max_depth:
        logging.warning(f"Max recursion depth reached at: {directory}")
        return False
    
    has_media = False
    is_empty = True
    
    try:
        for entry in os.scandir(directory):
            full_path = entry.path
            if entry.is_file():
                _, ext = os.path.splitext(entry.name)
                if ext.lower() in MEDIA_EXTENSIONS:
                    has_media = True
                    is_empty = False
                else:
                    try:
                        os.remove(full_path)
                        logging.info(f"Deleted file: {full_path}")
                    except OSError as e:
                        logging.error(f"Failed to delete file {full_path}: {e}")
                        is_empty = False
            elif entry.is_dir():
                if not process_directory(full_path, media_dirs, deleted_count, depth=depth+1, max_depth=max_depth):
                    is_empty = False
        
        if has_media:
            media_dirs.append(directory)
        
        if is_empty and depth > 0:
            os.rmdir(directory)
            logging.info(f"Removed directory: {directory}")
            deleted_count[0] += 1
            return True
        
    except OSError as e:
        logging.error(f"Failed to process directory {directory}: {e}")
    
    return False


def check_and_clean_directories(directories):
    """Main function to check and clean directories."""
    total_dirs_processed = 0
    deleted_count = [0]
    media_dirs = []

    for directory in directories:
        if directory and os.path.exists(directory):
            logging.info(f"Checking directory: {directory}")
            process_directory(directory, media_dirs, deleted_count)
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
