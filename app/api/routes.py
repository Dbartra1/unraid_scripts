import os
import subprocess
from __main__ import app
from flask import Blueprint, jsonify, request
from database import models as DBModels
from apscheduler.triggers.cron import CronTrigger

job_router = Blueprint('job_router', __name__)

def execute_script(script_name):
    script_path = os.path.join("app", script_name)
    result = subprocess.run(
        ["python", script_path],
        capture_output=True,
        text=True
    )
    print(result.stdout)

@job_router.route('/job', methods=['GET'])
def list_jobs():
    jobs = db.session.query(DBModels.Job).all()
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

@job_router.route('/job', methods=['POST'])
def add_job():
    data = request.json
    script_name = data.get('script_name')
    frequency = data.get('frequency')
    
    job = db.session.query(DBModels.Job).filter_by(script_name=script_name).first()
    if job:
        job.frequency = frequency
    else:
        job = DBModels.Job(script_name=script_name, frequency=frequency)
        db.session.add(job)
    
    db.session.commit()
    
    scheduler.add_job(
        execute_script,
        CronTrigger.from_crontab(frequency),
        args=[script_name],
        id=script_name
    )
    
    return jsonify({'message': 'Job added successfully'}), 200

@job_router.route('/job/<int:job_id>', methods=['DELETE'])
def cancel_job(job_id):
    job = db.session.query(DBModels.Job).get(job_id)
    if job:
        scheduler.remove_job(job.script_name)
        db.session.delete(job)
        job.status = 'inactive'
        db.session.commit()
        return jsonify({'message': 'Job deleted successfully'}), 200
    else:
        return jsonify({'error': 'Job not found'}), 404

# Scripts Route
# @job_router.route('/<script_name>', methods=['POST'])
# def run_script(script_name):
#     try:
#         script_path = os.path.join(SCRIPTS_FOLDER, f"{script_name}")

#         if not os.path.exists(script_path):
#             return jsonify({"error": "Script not found"}), 404

#         # Run the script
#         result = subprocess.run(
#             ["python", script_path],
#             capture_output=True,
#             text=True
#         )

#         if result.returncode == 0:
#             return jsonify({"message": result.stdout.strip()}), 200
#         else:
#             return jsonify({"error": result.stderr.strip()}), 500
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500