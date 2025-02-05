import os
import time
import logging
from dotenv import load_dotenv

"""__summary__
This script is used to clean up the log files in a specified directory, keeping only the current log file.
It logs the process and the files that are deleted.
"""

# Load environment variables from .env file
load_dotenv()

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

required_env_vars = ["LOG_LEVEL", "LOG_PATH"]
missing_vars = [var for var in required_env_vars if not os.getenv(var)]

if missing_vars:
    raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")

# Validate LOG_PATH
if not LOG_PATH or not os.path.isdir(LOG_PATH):
    raise ValueError(f"Invalid LOG_PATH: {LOG_PATH}. Please set a valid path in your .env file.")

# Default to DEBUG if the provided LOG_LEVEL isn't valid
log_level = LOG_LEVEL_MAPPING.get(LOG_LEVEL, logging.DEBUG)

# Setup Logging
logging.basicConfig(
    filename=f"{LOG_PATH}/directory_cleanup_log_{time.strftime('%Y-%m-%d_%H-%M-%S')}.log",
    level=log_level,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Log the start of the cleanup process
logging.info("Starting log cleanup process...")

# Function to clean up old log files except the current one
def cleanup_logs():
    for filename in os.listdir(LOG_PATH):
        file_path = os.path.join(LOG_PATH, filename)
        
        # Check if it's a file and not the current log file
        if os.path.isfile(file_path) and filename != current_log_file:
            try:
                os.remove(file_path)
                logging.info(f"Deleted old log file: {filename}")
            except Exception as e:
                logging.error(f"Failed to delete {filename}: {e}")

def main():
    # Perform the log cleanup
    cleanup_logs()
    # Log the end of the cleanup process
    logging.info("Log cleanup process completed.")

if __name__ == "__main__":
    main()
