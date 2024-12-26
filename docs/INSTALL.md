# 📄 Installation

1. Clone the repository or download the scripts you need:
   ```bash
   git clone https://github.com/Dbartra1/unraid_scripts.git
   ```

2. Customize any variables or paths as needed within the .env file.


## General Installation Steps for Testing and Docker Build

1. **Clone the Repository**
   ```bash
   git clone https://github.com/Dbartra1/unraid_scripts.git
   cd unraid_scripts
   ```

2. **Building the Docker Container**
   ```bash
   docker build -t my-unraid-scripts .
   ```

3. **Run the Container**
   To start the container, you can use:
   ```bash
   docker run -d --name unraid-scripts-container my-unraid-scripts
   ```

## Adding Context-Specific Information:
- Edit the .env file to suit your setup
   ```env
   # Unraid Server
   SERVER_IP=0.0.0.0
   SERVER_2_IP=0.0.0.0
   SERVER_3_IP=0.0.0.0

   # Flask
   PORT_NUMBER_FLASK=5000

   # IDRAC
   IDRAC_USER=myuser
   IDRAC_PASS=mypassword
   IDRAC_HOST=https://localhost:443

   # Plex
   PLEX_API_URL=http://localhost:8989
   PLEX_API_TOKEN=plexapitoken

   # File Transfer
   DIRECTORY_1=\\IP\or\dir\path
   DIRECTORY_2=\\IP\or\dir\path
   DIRECTORY_3=\\IP\or\dir\path
   DIRECTORY_4=\\IP\or\dir\path

   # Overseer
   OVERSEERR_API_URL=http://localhost:5055
   OVERSEERR_API_TOKEN=your_overseerr_api_token
   USER_IDS=1,2,3,4  # List user IDs as comma-separated values

   # Radarr
   RADARR_API_URL=http://localhost:7878
   RADARR_API_KEY=your_radarr_api_key

   # Sonarr
   SONARR_API_URL=http://localhost:8989
   SONARR_API_KEY=your_sonarr_api_key

   # Log path for container wide logs
   LOG_PATH=\\path\to\your\logs
   ```

- Make sure to specify the ports or volumes if needed:
   ```bash
   docker run -d -p 8080:8080 -v /host/path:/container/path my-unraid-scripts
   ```

# 📄 Directory Cleanup Script Setup Guide

This guide outlines steps for setting up and running the Directory Cleanup Script on Linux and Windows systems, including permission adjustments.

🛠️ 1. Prerequisites

    Python 3.x installed.

    Access to the target directories.

    .env file configured with:
      
      ```env
      CLEANUP_DIRECTORY_1=/path/to/dir1
      CLEANUP_DIRECTORY_2=/path/to/dir2
      CLEANUP_DIRECTORY_3=/path/to/dir3
      CLEANUP_DIRECTORY_4=/path/to/dir4
      LOG_PATH=/path/to/log
      ```

🐧 2. Linux Setup

A. Adjust Directory Permissions

Ensure the user running the script has read, write, and execute permissions:
```bash
sudo chmod -R u+rwX,g+rwX,o+rX /path/to/your/directories
sudo chown -R youruser:users /path/to/your/directories
```

🪟 3. Windows Setup

A. Map SMB Share with Credentials

    Open File Explorer → Map Network Drive.
    Enter the network path:
   ```
    \\UnraidServer\YourShare
   ```
    Enable "Reconnect at sign-in" and "Connect using different credentials".

    Store credentials in Windows Credential Manager:
        - Open Credential Manager.
        - Add a new Windows Credential.

B. Adjust Permissions on Unraid (via CLI)

On your Unraid server:

```bash
chmod -R u+rwX,g+rwX,o+rX /mnt/user/YourShare
chown -R nobody:users /mnt/user/YourShare
```

📊 4. Verify Logs

Logs are generated in the path set by LOG_PATH in your .env file.
Check logs for errors or successes.

# 📄 Docker Configuration Backup Script Setup Guide

🛠️ 1. Prerequisites

   python 3.x installed.

   Access to the \appdata directory on whatever server you have the docker containers running on.

   Json configuration setup with the three required variables. `backup_location`, `retention_days`, and `containers`

   ```JSON
   {
   {
    "backup_location": "/mnt/user/backups/appdata",
    "retention_days": 7,
    "containers": [
        {
            "name": "sonarr",
            "appdata_path": "/mnt/user/appdata/sonarr"
        },
        {
            "name": "radarr",
            "appdata_path": "/mnt/user/appdata/radarr"
        },
        {
            "name": "plex",
            "appdata_path": "/mnt/user/appdata/plex"
        }
    ]
   }
   }
   ```
   ### Docker Container Pausing

   This script supports pausing all of the docker containers listed in the JSON configuration file, this could be useful if you need to copy all directories including locked ones. 

   All you need to do is edit the script to set the following variable to 'TRUE', as it is set to false by default.

   ```python
   # Toggle for pausing containers during backup
   PAUSE_CONTAINERS = False
   ```

   THIS SCRIPT WILL NOT COPY OVER KEYS OR LOCKED FILES USED BY DOCKER SECRETS, THIS IS ONLY TO BACK UP ITEMS LIKE DATABASE FILES SO THAT A DOCKER CONTAINER CAN BE RESTORED INCASE OF FAILURE!! 