# API Testing with Postman

### This project includes a Postman API testing collection, stored as a JSON file (static/api_tests.json), to simplify API testing for developers. Follow the steps below to use it:

#### 1. Import the API Testing Collection

    - Open Postman.
    - Click on the Import button (top left corner of Postman).
    - Select the Upload Files tab.
    - Navigate to the project directory and select the static/api_tests.json file.
    - Postman will import the API requests into a new collection.

#### 2. Configure Environment Variables

#### Some API endpoints may require environment-specific variables, such as:

    - Base URL (e.g., http://localhost:5000 or your server's address).
    - Authentication Tokens (e.g., API keys or session cookies).

#### To set these up:

    - Go to Environment in Postman (top right).
    - Create a new environment or select an existing one.
    - Add variables like base_url, auth_token, etc., and provide their values.

#### 3. Execute API Requests

    - Open the imported collection and expand the list of API requests.
    - Click on a request to see its details (method, URL, headers, etc.).
    - Hit Send to execute the request and view the response.

#### 4. Customize Requests

#### Feel free to modify or extend the API tests to match your use case:

    - Add additional headers, query parameters, or body data as needed.
    - Save changes to the collection or export a new version for sharing.

#### 5. Sharing the Collection

#### To share the updated collection with others:

    - Export the modified collection as a JSON file:
    - Click the collection's three-dot menu > Export.
    - Replace the existing static/api_tests.json file or add a versioned file for tracking.

