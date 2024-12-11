import os
import tarfile
import json
from datetime import datetime, timedelta

CONFIG_FILE = "backup_config.json"

def load_config(config_file):
    """Load configuration from a JSON file."""
    try:
        with open(config_file, "r") as file:
            return json.load(file)
    except Exception as e:
        print(f"[ERROR] Failed to load config: {e}")
        exit(1)

def create_backup(source_path, backup_location, container_name):
    """Create a compressed backup for a container."""
    if not os.path.exists(source_path):
        print(f"[ERROR] Appdata path for {container_name} does not exist: {source_path}")
        return

    if not os.path.exists(backup_location):
        os.makedirs(backup_location)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"{container_name}_backup_{timestamp}.tar.gz"
    backup_path = os.path.join(backup_location, backup_filename)

    try:
        print(f"Creating backup for {container_name}...")
        with tarfile.open(backup_path, "w:gz") as tar:
            tar.add(source_path, arcname=os.path.basename(source_path))
        print(f"[SUCCESS] Backup created: {backup_path}")
    except Exception as e:
        print(f"[ERROR] Failed to create backup for {container_name}: {e}")

def cleanup_old_backups(backup_location, retention_days):
    """Remove backups older than the retention period."""
    cutoff_date = datetime.now() - timedelta(days=retention_days)

    for filename in os.listdir(backup_location):
        file_path = os.path.join(backup_location, filename)
        if os.path.isfile(file_path) and filename.endswith(".tar.gz"):
            file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            if file_time < cutoff_date:
                try:
                    os.remove(file_path)
                    print(f"[INFO] Deleted old backup: {file_path}")
                except Exception as e:
                    print(f"[ERROR] Failed to delete {file_path}: {e}")

def main():
    # Load configuration
    config = load_config(CONFIG_FILE)
    backup_location = config["backup_location"]
    retention_days = config["retention_days"]
    containers = config["containers"]

    # Create backups for each container
    for container in containers:
        create_backup(container["appdata_path"], backup_location, container["name"])

    # Cleanup old backups
    print("Cleaning up old backups...")
    cleanup_old_backups(backup_location, retention_days)
    print("Backup process completed!")

if __name__ == "__main__":
    main()
