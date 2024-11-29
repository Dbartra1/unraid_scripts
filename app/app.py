from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return "Welcome to the Flask Web UI!"

@app.route("/api/data", methods=["POST"])
def handle_data():
    data = request.json  # Accept JSON input
    processed_data = f"Processed: {data.get('input')}"  # Example processing
    return jsonify({"message": "Success", "processed_data": processed_data})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

