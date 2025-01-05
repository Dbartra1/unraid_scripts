import os
import time
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# File path for logs
LOG_PATH = os.getenv("LOG_PATH")

# Validate LOG_PATH
if not LOG_PATH or not os.path.isdir(LOG_PATH):
    raise ValueError(f"Invalid LOG_PATH: {LOG_PATH}. Please set a valid path in your .env file.")

# Get the name of the log file that will be created
current_log_file = f"log_clear_{time.strftime('%Y-%m-%d_%H-%M-%S')}.log"

# Setup Logging
logging.basicConfig(
    filename=os.path.join(LOG_PATH, current_log_file),
    level=logging.DEBUG,
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
