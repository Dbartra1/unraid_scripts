import os
from dotenv import load_dotenv
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed


load_dotenv()

# Plex API details from .env
PLEX_API_URL = os.getenv('PLEX_API_URL')
PLEX_API_TOKEN = os.getenv('PLEX_API_TOKEN')

# Overseer API details from .env
OVERSEERR_API_URL = os.getenv('OVERSEERR_API_URL')
OVERSEERR_API_TOKEN = os.getenv('OVERSEERR_API_TOKEN')
USER_IDS = os.getenv('USER_IDS')

# Convert the USER_IDS string from the environment variable to a list of integers
if USER_IDS:
    user_ids = list(map(int, USER_IDS.split(',')))
else:
    user_ids = []  # Default to an empty list if not set

# Function to get a user's watchlist
def get_watchlist(user_id):
    response = requests.get(
        f'{PLEX_API_URL}/library/sections/1/all',
        headers={'X-Plex-Token': PLEX_API_TOKEN}
    )
    if response.status_code == 200:
        data = response.json()
        watchlist = [item['title'] for item in data['MediaContainer']['Metadata']]
        return watchlist
    else:
        print(f"Failed to get watchlist for user {user_id}: {response.status_code}")
        return []

# Function to get existing requests in Overseerr
def get_existing_requests():
    response = requests.get(
        f'{OVERSEERR_API_URL}/api/v1/request',
        headers={'Authorization': f'Bearer {OVERSEERR_API_TOKEN}'}
    )
    if response.status_code == 200:
        return response.json()['results']
    else:
        print(f"Failed to get existing requests: {response.status_code}")
        return []

# Function to add a new request to Overseerr
def add_request_to_overseerr(title, year=2024):
    response = requests.post(
        f'{OVERSEERR_API_URL}/api/v1/request',
        headers={'Authorization': f'Bearer {OVERSEERR_API_TOKEN}'},
        json={'title': title, 'year': year, 'type': 'movie'}  # Adjust type if needed
    )
    if response.status_code == 201:
        print(f"Request for {title} added successfully.")
    else:
        print(f"Failed to add request for {title}: {response.status_code}")

# Multithreaded processing to fetch watchlists
def fetch_all_watchlists(user_ids):
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_user = {executor.submit(get_watchlist, user_id): user_id for user_id in user_ids}
        results = {}
        for future in as_completed(future_to_user):
            user_id = future_to_user[future]
            try:
                watchlist = future.result()
                results[user_id] = watchlist
            except Exception as e:
                print(f"Error fetching watchlist for user {user_id}: {e}")
        return results

# Main script to compare watchlists and add new requests
def main():
    if not user_ids:
        print("No user IDs provided. Please set the USER_IDS environment variable.")
        return

    user_watchlists = fetch_all_watchlists(user_ids)
    existing_requests = get_existing_requests()

    # Flatten the watchlists and find new unique titles
    all_titles = set(title for watchlist in user_watchlists.values() for title in watchlist)
    existing_titles = {request['title'] for request in existing_requests}
    new_titles = all_titles - existing_titles

    # Add new requests to Overseerr in parallel
    with ThreadPoolExecutor(max_workers=5) as executor:
        for title in new_titles:
            executor.submit(add_request_to_overseerr, title)

if __name__ == '__main__':
    main()
