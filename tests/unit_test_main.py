import unittest
from unittest.mock import patch
import responses

# You will need to change the script name here to whatever you are testing, followed by the required functions. 
from your_script_name import (
    fetch_stalled_items,
    remove_and_blocklist_item,
    trigger_search,
    process_queue
)

class TestFetchStalledItems(unittest.TestCase):
    @responses.activate
    def test_fetch_stalled_items(self):
        # Mock API response
        api_url = "http://mock-api"
        api_key = "mock-key"
        queue_response = [
            {"id": 1, "title": "Stalled Movie", "status": "Stalled"},
            {"id": 2, "title": "Downloading Movie", "status": "Downloading"}
        ]
        responses.add(
            responses.GET,
            f"{api_url}/api/v3/queue",
            json=queue_response,
            status=200
        )

        # Call the function
        stalled_items = fetch_stalled_items(api_url, api_key)

        # Assertions
        self.assertEqual(len(stalled_items), 1)
        self.assertEqual(stalled_items[0]["title"], "Stalled Movie")

class TestRemoveAndBlocklistItem(unittest.TestCase):
    @responses.activate
    def test_remove_and_blocklist_item(self):
        # Mock API response
        api_url = "http://mock-api"
        api_key = "mock-key"
        item_id = 1
        title = "Stalled Movie"

        responses.add(
            responses.DELETE,
            f"{api_url}/api/v3/queue/{item_id}",
            status=200
        )

        # Call the function
        result = remove_and_blocklist_item(api_url, api_key, item_id, title)

        # Assertions
        self.assertTrue(result)

class TestTriggerSearch(unittest.TestCase):
    @responses.activate
    def test_trigger_search(self):
        # Mock API response
        api_url = "http://mock-api"
        api_key = "mock-key"
        title = "Stalled Movie"
        media_id = 123

        responses.add(
            responses.POST,
            f"{api_url}/api/v3/command",
            status=200
        )

        # Call the function
        result = trigger_search(api_url, api_key, title, media_id, is_movie=True)

        # Assertions
        self.assertTrue(result)

class TestProcessQueue(unittest.TestCase):
    @patch("your_script_name.fetch_stalled_items")
    @patch("your_script_name.remove_and_blocklist_item")
    @patch("your_script_name.trigger_search")
    def test_process_queue(self, mock_trigger_search, mock_remove_and_blocklist_item, mock_fetch_stalled_items):
        # Mock data
        mock_fetch_stalled_items.return_value = [
            {"id": 1, "title": "Stalled Movie", "status": "Stalled", "movieId": 123}
        ]
        mock_remove_and_blocklist_item.return_value = True
        mock_trigger_search.return_value = True

        # Call the function
        process_queue("http://mock-api", "mock-key", is_movie=True)

        # Assertions
        mock_fetch_stalled_items.assert_called_once()
        mock_remove_and_blocklist_item.assert_called_once_with("http://mock-api", "mock-key", 1, "Stalled Movie")
        mock_trigger_search.assert_called_once_with("http://mock-api", "mock-key", "Stalled Movie", 123, is_movie=True)
