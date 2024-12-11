import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Redfish API details from .env
IDRAC_USER = os.getenv("IDRAC_USER")
IDRAC_PASS = os.getenv("IDRAC_PASS")
IDRAC_HOST = os.getenv("IDRAC_HOST")

# Plex API details from .env
PLEX_API_URL = os.getenv('PLEX_API_URL')
PLEX_API_TOKEN = os.getenv('PLEX_API_TOKEN')

# Overseer API details from .env
OVERSEERR_API_URL = os.getenv('OVERSEERR_API_URL')
OVERSEERR_API_TOKEN = os.getenv('OVERSEERR_API_TOKEN')

# Radarr API details from .env
RADARR_API_URL= os.getenv('RADARR_API_URL')
RADARR_API_KEY= os.getenv('RADARR_API_KEY')

# Sonarr API details from .env
SONARR_API_URL= os.getenv('SONARR_API_URL')
SONARR_API_KEY= os.getenv('SONARR_API_KEY')

# API Endpoints and credentials from .env
API_ENDPOINTS = {
    "plex": {
        "url": os.getenv("PLEX_API_URL", "http://localhost:32400/status"),
        "token": os.getenv("PLEX_API_TOKEN")
    },
    "overseer": {
        "url": os.getenv("OVERSEER_API_URL", "http://localhost:5055/api/v1/status"),
        "token": os.getenv("OVERSEER_TOKEN")
    },
    "sonarr": {
        "url": os.getenv("SONARR_API_URL", "http://localhost:8989/api/system/status"),
        "token": os.getenv("SONARR_API_KEY")
    },
    "radarr": {
        "url": os.getenv("RADARR_API_URL", "http://localhost:7878/api/system/status"),
        "token": os.getenv("RADARR_API_KEY")
    },
    "redfish": {
        "url": os.getenv("REDFISH_URL", "http://localhost/redfish/v1"),
        "username": os.getenv("REDFISH_USERNAME"),
        "password": os.getenv("REDFISH_PASSWORD")
    }
}

def check_api_status():
    results = {}

    # Check Plex API
    plex = API_ENDPOINTS.get("plex")
    if plex:
        headers = {"X-Plex-Token": plex["token"]}
        try:
            response = requests.get(plex["url"], headers=headers, timeout=10)
            results["plex"] = {
                "status_code": response.status_code,
                "response": response.json() if response.headers.get("Content-Type") == "application/json" else response.text
            }
        except Exception as e:
            results["plex"] = {"error": str(e)}

    # Check Overseerr API
    overseer = API_ENDPOINTS.get("overseer")
    if overseer:
        headers = {"Authorization": f"Bearer {overseer['token']}"}
        try:
            response = requests.get(overseer["url"], headers=headers, timeout=10)
            results["overseer"] = {
                "status_code": response.status_code,
                "response": response.json() if response.headers.get("Content-Type") == "application/json" else response.text
            }
        except Exception as e:
            results["overseer"] = {"error": str(e)}

    # Check Sonarr API
    sonarr = API_ENDPOINTS.get("sonarr")
    if sonarr:
        params = {"apikey": sonarr["token"]}
        try:
            response = requests.get(sonarr["url"], params=params, timeout=10)
            results["sonarr"] = {
                "status_code": response.status_code,
                "response": response.json() if response.headers.get("Content-Type") == "application/json" else response.text
            }
        except Exception as e:
            results["sonarr"] = {"error": str(e)}

    # Check Radarr API
    radarr = API_ENDPOINTS.get("radarr")
    if radarr:
        params = {"apikey": radarr["token"]}
        try:
            response = requests.get(radarr["url"], params=params, timeout=10)
            results["radarr"] = {
                "status_code": response.status_code,
                "response": response.json() if response.headers.get("Content-Type") == "application/json" else response.text
            }
        except Exception as e:
            results["radarr"] = {"error": str(e)}

    # Check Redfish API
    redfish = API_ENDPOINTS.get("redfish")
    if redfish:
        try:
            response = requests.get(redfish["url"], auth=(redfish["username"], redfish["password"]), timeout=10)
            results["redfish"] = {
                "status_code": response.status_code,
                "response": response.json() if response.headers.get("Content-Type") == "application/json" else response.text
            }
        except Exception as e:
            results["redfish"] = {"error": str(e)}

    return results

if __name__ == "__main__":
    api_statuses = check_api_status()
    for api, result in api_statuses.items():
        print(f"\n{api.upper()} API:")
        if "error" in result:
            print(f"  Error: {result['error']}")
        else:
            print(f"  Status Code: {result['status_code']}")
            print(f"  Response: {result['response']}")
