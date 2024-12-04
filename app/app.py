import os
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template
from app import main as ft
from Power_off import main as poff
from Power_on import main as pon
from Stall_handler import main as stall
from app.Overseer_Plex_watchlist import main as opw

# Load the environment variables from the .env file
load_dotenv()

# Load server IP and port number from environment variables
SERVER_IP = os.getenv('SERVER_IP', '127.0.0.1')  # Default to localhost if not set
PORT_NUMBER_FLASK = int(os.getenv('PORT_NUMBER_FLASK', 5000))  # Default to port 5000

app = Flask(__name__)



@app.route("/")
def home():
    return render_template("index.html")

@app.route('/run-script', methods=['POST'])
def run_script():
    script_name = request.json.get('script_name')
    if not script_name:
        return jsonify({"error": "No script name provided"}), 400
    
    try:
        # Make sure to set the correct path to your scripts folder
        scripts_folder = "./scripts"
        script_path = os.path.join(scripts_folder, f"{script_name}.py")
        
        if not os.path.exists(script_path):
            return jsonify({"error": "Script not found"}), 404
        
        # Run the script and capture output
        result = subprocess.run(
            ["python", script_path],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            return jsonify({"output": result.stdout}), 200
        else:
            return jsonify({"error": result.stderr}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/start-transfer", methods=["POST"])
def start_file_transfer():
    try:
        # Trigger the main logic from the file_transfer script
        ft()
        return jsonify({"message": "File transfer process initiated successfully."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/plex_power_off", methods=["POST"])
def plex_power_off():
    try:
        poff()
        return jsonify({"message": "No Plex activity detected, server powered off."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/api/plex_power_on", methods=["POST"])
def plex_power_on():
    try:
        pon()
        return jsonify({"message": "Plex detected, server powered on."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/api/stall_handler", methods=["POST"])
def stall_handler():
    try:
        stall()
        return jsonify({"message": "Stalls detected, blocklisting and researching."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/api/overseer_Plex_integration", methods=["POST"])
def overseer_Plex_integration():
    try:
        opw()
        return jsonify({"message": "Grabbed Plex watchlists and added requests to overseer."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

if __name__ == "__main__":
    app.run(host=SERVER_IP, port=PORT_NUMBER_FLASK)
