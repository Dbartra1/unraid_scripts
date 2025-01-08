# Unraid Scripts Collection

This repository contains a set of custom scripts designed to streamline and automate tasks on Unraid. A key feature of this repository is its integration with Plex Media Server and Dell iDRAC systems via the Redfish API. These scripts enable advanced functionality such as monitoring Plex traffic and dynamically managing the power state of a Dell rack-mounted server equipped with iDRAC, optimizing both performance and energy usage.

## Project Documentation

- [Install Guide](docs/INSTALL.md)
- [API Testing](docs/TESTING.md)
- [Project Definitions](docs/DEFINITIONS.md)


## Project Structure

- **app/templates**: Contains all of the HTML templating for flask.
- **app/**: Contains all the custom scripts, categorized by their functionality.
- **docs/**: Contains extended project documentation.
- **config/**: Contains configuration files for scripts contained in the app/ folder.
- **logs/**: Contains any logs output from the set of scripts in app/.
- **tests/**: Contains all the python specific unit testing materials.
- **Dockerfile**: Contains all of the needed information to build this as a docker container.
- **README.md**: Documentation for the repository, including setup and usage guidelines.
- **LICENSE**: Specifies the licensing terms for this repository.

## Features

- Ability to schedule tasks via chron jobs. 
- Automation of power state for IDRAC and WOL based systems
- Easy integration with Unraid's User Scripts plugin.
- Easy to understand project structure for further customization. 
- Modular scripts that are built to address automation tasks in the most platform agnostic way possible.
- Easy integration with Sonarr, Radarr, Overseer, and Plex.
- Easy file syncing between two servers either on the local network or in the cloud.
- Multiple file syncing methodologies with varying degrees of granularity and accuracy. 
- Lite Web UI via the Flask API

## Prerequisites

- **Unraid/Docker**: Ensure Unraid is installed and configured or Docker is installed on host machine.
- **Python Environment**: Most scripts are written in python and require a python environment locally to run.
- **Installed Dependencies**: Install dependencies as listed below, see the install documentation for more details.
- **Access Requirements**: The account running the Docker container needs proper Read/Write/Delete permissions to the directories it will be interacting with. More information in the install instructions.

## Python Imports/Dependencies

#### **These are all listed in the requirements.txt file in the repository, these can be mass installed via the CLI or installed when the docker container is built.**

- **requests**
- **dotenv**
- **crontab**
- **tarfile**
- **dotenv**
- **pdb**
- **responses**
- **coverage**
- **flask**
- **json**
- **tqdm**
- **psutil**

## Usage

- **Running Scripts**: Scripts can be executed manually or scheduled using the cron functionality built into the Flask UI/CLI.
- **Customization**: Modify script parameters located in the .env file to suit your specific setup.
- **Modularity**: This project was built with modularity in mind, trying our best to provide a customizable project structure.

## Other Dependencies

- **Unraid Tools**: Certain scripts may rely on pre-installed Unraid utilities.
- **Optional Tools**: For specific functionality, additional tools or Docker containers may be required. Check individual scripts for more details.
- **requirements.txt**: This will contain specific Python libraries needed in order to run the scripts. 

## Contribution

Feel free to contribute by submitting issues or creating pull requests. Ensure your contributions align with the project's structure and coding conventions.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.
