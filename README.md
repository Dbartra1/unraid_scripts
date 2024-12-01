# Unraid Scripts Collection

This repository contains a set of custom scripts designed to streamline and automate tasks on Unraid. A key feature of this repository is its integration with Plex Media Server and Dell iDRAC systems via the Redfish API. These scripts enable advanced functionality such as monitoring Plex traffic and dynamically managing the power state of a Dell rack-mounted server equipped with iDRAC, optimizing both performance and energy usage.

## Project Documentation

- [Install Guide](docs/INSTALL.md)
- [API Testing](docs/TESTING.md)
- [Project Definitions](docs/DEFINITIONS.md)


## Project Structure

- **app/templates**: Contains all of the HTML templating for flask.
- **app/**: Contains all the custom scripts, categorized by their functionality.
- **logs/**: Contains any logs output from the set of scripts in app/.
- **tests/**: Contains all the python specific unit testing materials.
- **docker-compose**: Contains all of the needed information to build this as a docker container.
- **README.md**: Documentation for the repository, including setup and usage guidelines.
- **LICENSE**: Specifies the licensing terms for this repository.

## Features

- Automation of power state based on activity on a plex account.
- Easy integration with Unraid's User Scripts plugin.
- Modular scripts that address various system requirements.
- Easy integration with Sonarr, Radarr, and Overseer
- Easy file syncing between two servers on network.
- Lite Web UI via the Flask API

## Prerequisites

- **Unraid/Docker**: Ensure Unraid is installed and configured or Docker is installed on host machine.
- **Python Environment**: Most scripts are written in python and require a python environment locally to run.

## Python Imports/Dependencies

#### **These are all listed in the requirements.txt file in the repository, these can be mass installed via the CLI or installed when the docker container is built.**

- **requests**
- **subprocess**
- **time**
- **logging**
- **dotenv**
- **pdb**
- **responses**
- **coverage**
- **flask**

## Usage

- **Running Scripts**: Scripts can be executed manually or scheduled using the cron functionality in the User Scripts plugin.
- **Customization**: Modify script parameters located in the .env file to suit your specific Unraid setup.

## Other Dependencies

- **Unraid Tools**: Certain scripts may rely on pre-installed Unraid utilities.
- **Optional Tools**: For specific functionality, additional tools or Docker containers may be required. Check individual scripts for more details.
- **requirements.txt**: This will contain specific Python libraries needed in order to run the scripts. 

## Contribution

Feel free to contribute by submitting issues or creating pull requests. Ensure your contributions align with the project's structure and coding conventions.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.
