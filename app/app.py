import os
import subprocess
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy, enum
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

load_dotenv()

# Load server IP and port number from environment variables
SERVER_IP = os.getenv('SERVER_IP', '127.0.0.1')
PORT_NUMBER_FLASK = int(os.getenv('PORT_NUMBER_FLASK', 5000))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

scheduler = BackgroundScheduler()
scheduler.start()

class JobStatus(enum.Enum):
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    COMPLETED = 'completed'

# Job model
class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    script_name = db.Column(db.String(120), nullable=False)
    frequency = db.Column(db.String(120), nullable=False)
    status = db.Column(db.Enum(JobStatus), default=JobStatus.ACTIVE)
    
# Initialize the database
with app.app_context():
    db.create_all()
    
# Job function
def execute_script(script_name):
    script_path = os.path.join("app", script_name)
    result = subprocess.run(
        ["python", script_path],
        capture_output=True,
        text=True
    )
    print(result.stdout)
    
# API to add/update a job
@app.route('/add_job', methods=['POST'])
def add_job():
    data = request.json
    script_name = data.get('script_name')
    frequency = data.get('frequency')
    
    job = Job.query.filter_by(script_name=script_name).first()
    if job:
        job.frequency = frequency
    else:
        job = Job(script_name=script_name, frequency=frequency)
        db.session.add(job)
    
    db.session.commit()
    
    scheduler.add_job(
        execute_script,
        CronTrigger.from_crontab(frequency),
        args=[script_name],
        id=script_name
    )
    
    return jsonify({'message': 'Job added successfully'}), 200

# API to delete a job
@app.route('/delete_job/<int:job_id>', methods=['DELETE'])
def cancel_job(job_id):
    job = Job.query.get(job_id)
    if job:
        scheduler.remove_job(job.script_name)
        db.session.delete(job)
        job.status = 'inactive'
        db.session.commit()
        return jsonify({'message': 'Job deleted successfully'}), 200
    else:
        return jsonify({'error': 'Job not found'}), 404

# API to list all jobs
@app.route('/list_jobs', methods=['GET'])
def list_jobs():
    jobs = Job.query.all()
    jobs = [
        {
            'id': job.id,
            'script_name': job.script_name,
            'frequency': job.frequency,
            'status': job.status
        }
        for job in jobs
    ]
    return jsonify(jobs), 200


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
