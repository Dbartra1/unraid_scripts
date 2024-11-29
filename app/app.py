import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template

# Load the environment variables from the .env file
load_dotenv()

# Load server IP and port number from environment variables
SERVER_IP = os.getenv('SERVER_IP', '127.0.0.1')  # Default to localhost if not set
PORT_NUMBER_FLASK = int(os.getenv('PORT_NUMBER_FLASK', 5000))  # Default to port 5000

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/data", methods=["POST"])
def handle_data():
    data = request.json  # Accept JSON input
    processed_data = f"Processed: {data.get('input')}"  # Example processing
    return jsonify({"message": "Success", "processed_data": processed_data})

if __name__ == "__main__":
    app.run(host=SERVER_IP, port=PORT_NUMBER_FLASK)
