# Unraid Scripts Collection

This repository contains a set of custom scripts designed to streamline and automate tasks on Unraid. A key feature of this repository is its integration with Plex Media Server and Dell iDRAC systems via the Redfish API. These scripts enable advanced functionality such as monitoring Plex traffic and dynamically managing the power state of a Dell rack-mounted server equipped with iDRAC, optimizing both performance and energy usage.

## Project Structure

- **app/**: Contains all the custom scripts, categorized by their functionality.
- **logs/**: Contains any logs output from the set of scripts in app/.
- **tests/**: Contains all the python specific unit testing materials.
- **docker-compose**: Contains all of the needed information to build this as a docker container.
- **README.md**: Documentation for the repository, including setup and usage guidelines.
- **LICENSE**: Specifies the licensing terms for this repository.


## Definitions

**1. Overseerr**
- **Definition**: Overseerr is an open-source, web-based media request management tool that integrates with media servers like Plex and Jellyfin. It allows users to request new movies or TV shows, which can then be processed and added to the media server automatically. Overseerr provides a user-friendly interface for managing requests, approvals, and notifications.

**2. Plex**
- **Definition**: Plex is a popular media server platform that allows users to organize, stream, and share their media libraries, including movies, TV shows, music, and photos. The server application manages the media library, while the Plex client apps provide streaming capabilities across multiple devices. Plex also supports plugins and add-ons to enhance its features.

**3. UNRAID**
- **Definition**: UNRAID is an operating system designed for network-attached storage (NAS) and server management. It allows users to combine different types of storage devices into a unified system, providing features such as data protection, virtualization, and the ability to run various applications in Docker containers or virtual machines. UNRAID is often used for home and small office setups that require flexible storage and media server capabilities.

**4. Sonarr**
- **Definition**: Sonarr is an open-source tool used for automating the process of downloading, sorting, and managing TV shows. It monitors multiple torrent or Usenet indexers for new episodes, downloads them, and moves them into the correct folder structure in a media library. Sonarr can integrate with media servers like Plex, enabling seamless media management and viewing.

**5. Radarr**
- **Definition**: Radarr is a counterpart to Sonarr, specifically designed for automating the process of managing movies. It monitors movie indexers for new releases, handles automatic downloading, and organizes downloaded content into a media library. Like Sonarr, Radarr integrates with Plex for easy access to movies on various devices.

**6. iDRAC**
- **Definition**: iDRAC (Integrated Dell Remote Access Controller) is a management solution embedded in Dell servers that allows for remote monitoring, management, and troubleshooting of hardware. It provides out-of-band access to the server’s operating system, making it possible to control the server remotely, perform tasks like rebooting, updating firmware, and diagnosing hardware issues, all without needing to be physically present.

**7. Redfish**
- **Definition**: Redfish is a standardized API specification for managing and monitoring hardware in data centers. Developed by the Distributed Management Task Force (DMTF), it provides a RESTful interface for interacting with servers, enabling remote management and automation tasks such as power control, hardware monitoring, and configuration.

**8. Plex API**
- **Definition**: The Plex API is an interface that allows developers to interact with and automate Plex Media Server functionalities. It provides endpoints for managing libraries, retrieving media metadata, and controlling playback. The API facilitates integration with third-party applications to extend Plex's capabilities and enable custom workflows.

**9. Overseerr API**
- **Definition**: The Overseerr API is an application programming interface that allows developers to interact programmatically with the Overseerr app. It provides endpoints for managing media requests, handling user interactions, and automating request processing. This API enables integration with media servers and other applications for seamless media management.

## Features

- Automation of power state based on activity on a plex account.
- Easy integration with Unraid's User Scripts plugin.
- Modular scripts that address various system requirements.
- Easy file syncing between two servers on network.

## Prerequisites

- **Unraid**: Ensure Unraid is installed and configured.
- **User Scripts Plugin**: Install this from the Unraid App Store to manage and schedule custom scripts.
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


## Installation

1. Clone the repository or download the scripts you need:
   ```bash
   git clone https://github.com/Dbartra1/unraid_scripts.git
   ```

2. Navigate to the `User Scripts` section in Unraid:
   - Go to **Settings** > **User Scripts**.
   - Add a new script and copy-paste the desired script from this repository.

3. Customize any variables or paths as needed within the .env file.

## Usage

- **Running Scripts**: Scripts can be executed manually or scheduled using the cron functionality in the User Scripts plugin.
- **Customization**: Modify script parameters located in the .env file to suit your specific Unraid setup.

## Dependencies

- **Unraid Tools**: Certain scripts may rely on pre-installed Unraid utilities.
- **Optional Tools**: For specific functionality, additional tools or Docker containers may be required. Check individual scripts for more details.
- **requirements.txt**: This will contain specific Python libraries needed in order to run the scripts. 

## Contribution

Feel free to contribute by submitting issues or creating pull requests. Ensure your contributions align with the project's structure and coding conventions.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.