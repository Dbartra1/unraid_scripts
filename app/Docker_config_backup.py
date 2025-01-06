import os
import tarfile
import json
import logging
from datetime import datetime, timedelta
import argparse
import time
import subprocess

# Configuration
CONFIG_FILE = os.path.join(os.getenv("CONFIG_PATH", ""), "backup_config.json")

# File path for logs
LOG_PATH = os.getenv("LOG_PATH", "")

# Validate LOG_PATH
if not os.path.exists(LOG_PATH):
    os.makedirs(LOG_PATH, exist_ok=True)

# Setup Logging
logging.basicConfig(
    filename=os.path.join(LOG_PATH, f"docker_config_backup_{time.strftime('%Y-%m-%d_%H-%M-%S')}.log"),
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Toggle for pausing containers during backup
PAUSE_CONTAINERS = False

def load_config(config_file):
    """Load and validate configuration from a JSON file."""
    try:
        with open(config_file, "r") as file:
            config = json.load(file)
        
        required_keys = ["BACKUP_LOCATION", "RETENTION_DAYS", "CONTAINERS"]
        for key in required_keys:
            if key not in config:
                raise KeyError(f"Missing required key: {key}")
        
        return config
    except (FileNotFoundError, KeyError, json.JSONDecodeError) as e:
        logging.critical(f"Failed to load or validate config: {e}")
        exit(1)

def manage_container(container_name, action):
    """Pause or start a Docker container."""
    try:
        subprocess.run(["docker", action, container_name], check=True)
        logging.info(f"Container {container_name} {action} successfully.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to {action} container {container_name}: {e}")

def create_backup(source_path, backup_location, container_name, dry_run=False):
    """Create a compressed backup for a container."""
    logging.info(f"Starting backup for container: {container_name}")
    if not os.path.exists(source_path):
        logging.error(f"Appdata path for {container_name} does not exist: {source_path}")
        return

    os.makedirs(backup_location, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"{container_name}_backup_{timestamp}.tar.gz"
    backup_path = os.path.join(backup_location, backup_filename)

    if dry_run:
        logging.info(f"[DRY-RUN] Would create backup: {backup_path}")
        return

    try:
        logging.info(f"Creating backup archive: {backup_path}")
        with tarfile.open(backup_path, "w:gz") as tar:
            for root, dirs, files in os.walk(source_path):
                for file in files:
                    full_path = os.path.join(root, file)
                    arcname = os.path.relpath(full_path, start=source_path)
                    logging.debug(f"Adding file: {full_path} as {arcname}")
                    try:
                        tar.add(full_path, arcname=arcname)
                    except (PermissionError, FileNotFoundError) as e:
                        logging.warning(f"Skipping file due to error: {full_path}. Reason: {e}")
        logging.info(f"[SUCCESS] Backup created: {backup_path}")
    except PermissionError as e:
        logging.error(f"Permission denied: {e}")
    except Exception as e:
        logging.error(f"Failed to create backup for {container_name}: {e}")

def cleanup_old_backups(backup_location, retention_days, dry_run=False):
    """Remove backups older than the retention period."""
    logging.info(f"Cleaning up backups older than {retention_days} days in {backup_location}")
    cutoff_date = datetime.now() - timedelta(days=retention_days)

    for filename in os.listdir(backup_location):
        file_path = os.path.join(backup_location, filename)
        if os.path.isfile(file_path) and filename.endswith(".tar.gz"):
            file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            if file_time < cutoff_date:
                if dry_run:
                    logging.info(f"[DRY-RUN] Would delete old backup: {file_path}")
                else:
                    try:
                        os.remove(file_path)
                        logging.info(f"Deleted old backup: {file_path}")
                    except Exception as e:
                        logging.error(f"Failed to delete {file_path}: {e}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true', help='Simulate backup process without changes')
    args = parser.parse_args()

    logging.info("Loading configuration...")
    config = load_config(CONFIG_FILE)
    backup_location = config["BACKUP_LOCATION"]
    retention_days = config["RETENTION_DAYS"]
    containers = config["CONTAINERS"]

    # Create backups for each container
    for container in containers:
        if PAUSE_CONTAINERS:
            manage_container(container["name"], "stop")
            create_backup(container["appdata_path"], backup_location, container["name"], args.dry_run)
            manage_container(container["name"], "start")
        else:
            create_backup(container["appdata_path"], backup_location, container["name"], args.dry_run)


    # Cleanup old backups
    logging.info("Starting cleanup process...")
    cleanup_old_backups(backup_location, retention_days, args.dry_run)
    logging.info("Backup process completed!")

if __name__ == "__main__":
    main()
