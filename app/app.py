import os
import subprocess
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

load_dotenv()

# Load server IP and port number from environment variables
SERVER_IP = os.getenv('SERVER_IP', '127.0.0.1')
PORT_NUMBER_FLASK = int(os.getenv('PORT_NUMBER_FLASK', 5000))

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

# Scripts Route
@app.route('/api/<script_name>', methods=['POST'])
def run_script(script_name):
    try:
        scripts_folder = "./app"
        script_path = os.path.join(scripts_folder, f"{script_name}")

        if not os.path.exists(script_path):
            return jsonify({"error": "Script not found"}), 404

        # Run the script
        result = subprocess.run(
            ["python", script_path],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            return jsonify({"message": result.stdout.strip()}), 200
        else:
            return jsonify({"error": result.stderr.strip()}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to submit a cron job for a script
@app.route('/api/<script_name>/cron', methods=['POST'])
def submit_cron(script_name):
    cron_expression = request.json.get("cron")

    if not cron_expression:
        return jsonify({"error": "Invalid cron expression"}), 400

    try:
        cron_job = f"{cron_expression} python {script_name}"
        with open(f"/tmp/{script_name}_cron", "w") as f:
            f.write(cron_job + "\n")
        return jsonify({"message": "Cron job submitted successfully."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to cancel a cron job for a script
@app.route('/api/<script_name>/cron', methods=['DELETE'])
def cancel_cron(script_name):
    try:
        # Example: Remove cron job file
        cron_file = f"/tmp/{script_name}_cron"
        if os.path.exists(cron_file):
            os.remove(cron_file)
            return jsonify({"message": "Cron job cancelled successfully."}), 200
        else:
            return jsonify({"error": "No cron job found for this script."}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host=SERVER_IP, port=PORT_NUMBER_FLASK)
