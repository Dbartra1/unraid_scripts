## Installation

1. Clone the repository or download the scripts you need:
   ```bash
   git clone https://github.com/Dbartra1/unraid_scripts.git
   ```

2. Navigate to the `User Scripts` section in Unraid:
   - Go to **Settings** > **User Scripts**.
   - Add a new script and copy-paste the desired script from this repository.

3. Customize any variables or paths as needed within the .env file.


### General Installation Steps for Testing and Docker Build

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

### Adding Context-Specific Information:
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
   IDRAC_HOST=http://localhost:443

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

   # SMB
   SMB_USERNAME=smb_username
   SMB_PASSWORD=smb_password

   # Log path for container wide logs
   LOG_PATH=\\path\to\your\logs
   ```

- Make sure to specify the ports or volumes if needed:
   ```bash
   docker run -d -p 8080:8080 -v /host/path:/container/path my-unraid-scripts
   ```