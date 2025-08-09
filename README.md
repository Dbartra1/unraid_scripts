# Unraid Scripts Collection

This repository contains a set of custom scripts designed to streamline and automate tasks on Unraid. A key feature of this repository is its integration with Plex Media Server and Dell iDRAC systems via the Redfish API. These scripts enable advanced functionality such as monitoring Plex traffic and dynamically managing the power state of a Dell rack-mounted server equipped with iDRAC, optimizing both performance and energy usage.

## 🚀 New Features

- **Advanced Job Scheduling System**: Robust job scheduling with support for common frequencies and custom cron expressions
- **REST API**: Full REST API for managing jobs programmatically
- **Real-time Job Monitoring**: Track job status, execution history, and scheduling information
- **Flexible Script Execution**: Run scripts on-demand or on schedule with comprehensive error handling
- **Modern Architecture**: Clean separation of concerns with service, repository, and scheduler layers

## Project Documentation

- [Install Guide](docs/INSTALL.md)
- [API Testing](docs/TESTING.md)
- [Project Definitions](docs/DEFINITIONS.md)
- [**Job Scheduling System**](docs/JOB_SCHEDULING.md) ← **NEW!**

## Project Structure

- **app/templates**: Contains all of the HTML templating for flask.
- **app/**: Contains all the custom scripts, categorized by their functionality.
- **app/jobs/**: Job scheduling system components (routes, service, repository, scheduler).
- **docs/**: Contains extended project documentation.
- **config/**: Contains configuration files for scripts contained in the app/ folder.
- **logs/**: Contains any logs output from the set of scripts in app/.
- **tests/**: Contains all the python specific unit testing materials.
- **Dockerfile**: Contains all of the needed information to build this as a docker container.
- **README.md**: Documentation for the repository, including setup and usage guidelines.
- **LICENSE**: Specifies the licensing terms for this repository.

## Features

- **Job Scheduling**: Advanced job scheduling system with flexible frequency options
- **REST API**: Full REST API for job management and script execution
- **Script Automation**: Schedule and manage script execution automatically
- **Real-time Monitoring**: Monitor job status and execution history
- **Flexible Frequencies**: Support for common schedules (daily, hourly, weekly) and custom cron expressions
- **Easy Integration**: Simple integration with Unraid's User Scripts plugin
- **Modular Design**: Built with modularity and extensibility in mind
- **Comprehensive Logging**: Detailed logging for debugging and monitoring
- **Error Handling**: Robust error handling and recovery mechanisms

## Prerequisites

- **Unraid/Docker**: Ensure Unraid is installed and configured or Docker is installed on host machine.
- **Python Environment**: Most scripts are written in python and require a python environment locally to run.
- **Installed Dependencies**: Install dependencies as listed below, see the install documentation for more details.
- **Access Requirements**: The account running the Docker container needs proper Read/Write/Delete permissions to the directories it will be interacting with. More information in the install instructions.

## Python Imports/Dependencies

#### **These are all listed in the requirements.txt file in the repository, these can be mass installed via the CLI or installed when the docker container is built.**

- **requests**
- **python-dotenv**
- **flask**
- **flask-sqlalchemy**
- **apscheduler**
- **tqdm**
- **psutil**
- **werkzeug**

## Quick Start

### Running the Application

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd unraid_scripts
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the application**:
   ```bash
   python -m app.app
   ```

4. **Test the API**:
   ```bash
   python test_api.py
   ```

### Using Docker

#### Prerequisites
- Docker Desktop installed and running
- Docker Compose available

#### Quick Start with Docker

**Option 1: Use the provided scripts (Windows)**
```cmd
# Run the batch file
start-docker.bat

# Or run the PowerShell script
.\start-docker.ps1
```

**Option 2: Manual Docker commands**
```bash
# Build the container
docker build -t my-unraid-scripts .

# Run with docker-compose (recommended)
docker-compose up --build

# Or run directly
docker run -p 5000:5000 my-unraid-scripts
```

#### Docker Configuration
- **Port**: 5000 (Flask application)
- **Volumes**: 
  - `./config` → `/app/config` (read-only)
  - `./app/scripts` → `/app/app/scripts` (read-only)
- **Environment**: Configured via `config.env` or docker-compose.yml
- **Health Check**: Automatic health monitoring every 30 seconds

## Usage

### Job Scheduling

The new job scheduling system allows you to:

- **Create Jobs**: Schedule scripts to run automatically
- **Manage Frequencies**: Use predefined frequencies or custom cron expressions
- **Monitor Status**: Track job execution and scheduling information
- **Run On-Demand**: Execute scripts immediately when needed

### API Endpoints

- `GET /api/jobs/` - List all jobs
- `POST /api/jobs/` - Create a new job
- `GET /api/jobs/{id}` - Get job details
- `PATCH /api/jobs/{id}` - Update job settings
- `DELETE /api/jobs/{id}` - Cancel a job
- `POST /api/jobs/{id}/run` - Run job immediately
- `POST /api/jobs/{id}/activate` - Activate a cancelled job
- `GET /api/jobs/scheduler/status` - Get scheduler status

### Example: Creating a Daily Backup Job

```bash
curl -X POST http://localhost:5000/api/jobs/ \
  -H "Content-Type: application/json" \
  -d '{
    "script_name": "backup_script",
    "frequency": "daily",
    "description": "Daily backup of important data"
  }'
```

## Other Dependencies

- **Unraid Tools**: Certain scripts may rely on pre-installed Unraid utilities.
- **Optional Tools**: For specific functionality, additional tools or Docker containers may be required. Check individual scripts for more details.
- **requirements.txt**: This will contain specific Python libraries needed in order to run the scripts.

## Testing

Use the provided test script to verify the API functionality:

```bash
python test_api.py
```

This will test all the major API endpoints and demonstrate the job scheduling capabilities.

## Contribution

Feel free to contribute by submitting issues or creating pull requests. Ensure your contributions align with the project's structure and coding conventions.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.
