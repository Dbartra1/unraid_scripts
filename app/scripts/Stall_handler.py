import os
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

# Environment variables
RADARR_API_URL = os.getenv("RADARR_API_URL")
RADARR_API_KEY = os.getenv("RADARR_API_KEY")
SONARR_API_URL = os.getenv("SONARR_API_URL")
SONARR_API_KEY = os.getenv("SONARR_API_KEY")

def fetch_stalled_items(api_url, api_key):
    """Fetch stalled items from Radarr or Sonarr."""
    try:
        url = f"{api_url}/api/v3/queue"
        params = {"apikey": api_key}
        response = requests.get(url, params=params)
        response.raise_for_status()
        queue = response.json()
        # Filter for stalled items
        stalled_items = [item for item in queue if item.get("status") == "Stalled"]
        return stalled_items
    except Exception as e:
        print(f"Error fetching queue from {api_url}: {e}")
        return []

def remove_and_blocklist_item(api_url, api_key, item_id, title):
    """Remove and blocklist an item."""
    try:
        url = f"{api_url}/api/v3/queue/{item_id}"
        params = {"apikey": api_key, "blacklist": "true"}
        response = requests.delete(url, params=params)
        response.raise_for_status()
        print(f"Blocked and removed: {title}")
        return True
    except Exception as e:
        print(f"Error removing {title}: {e}")
        return False

def trigger_search(api_url, api_key, title, media_id, is_movie=True):
    """Trigger a search for the given media."""
    try:
        url = f"{api_url}/api/v3/command"
        data = {
            "name": "Search" if is_movie else "EpisodeSearch",
            "movieId": media_id if is_movie else None,
            "episodeIds": [media_id] if not is_movie else None
        }
        # Remove None keys from the payload
        data = {k: v for k, v in data.items() if v is not None}
        headers = {"X-Api-Key": api_key}
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        print(f"Search triggered for: {title}")
        return True
    except Exception as e:
        print(f"Error triggering search for {title}: {e}")
        return False

def process_queue(api_url, api_key, is_movie=True):
    """Process the activity queue for stalled items."""
    stalled_items = fetch_stalled_items(api_url, api_key)
    for item in stalled_items:
        title = item["title"]
        item_id = item["id"]
        media_id = item["movieId"] if "movieId" in item else item["episodeId"]

        print(f"Processing stalled item: {title}")
        removed = remove_and_blocklist_item(api_url, api_key, item_id, title)
        if removed:
            trigger_search(api_url, api_key, title, media_id, is_movie=is_movie)

def main():
    print("Processing Radarr queue...")
    process_queue(RADARR_API_URL, RADARR_API_KEY, is_movie=True)

    print("Processing Sonarr queue...")
    process_queue(SONARR_API_URL, SONARR_API_KEY, is_movie=False)

if __name__ == "__main__":
    main()
