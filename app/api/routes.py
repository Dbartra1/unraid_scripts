import os
import subprocess
from apscheduler.triggers.cron import CronTrigger
from flask import Blueprint, jsonify, request
from app.services import job_service

job_router_blueprint = Blueprint('job_router', __name__, url_prefix="/job")
job_service = job_service.JobService()

@job_router_blueprint.route('/', methods=['GET'])
def list_jobs():
    print("WE ARE IN THE ROUTE")
    jobs = job_service.get_jobs()
    # return jsonify(jobs), 200
    blah = {job.id: job.id for job in jobs}
    return jsonify(blah), 200

    # @job_router.route('/job', methods=['POST'])
    # def add_job():
    #     data = request.json
    #     script_name = data.get('script_name')
    #     frequency = data.get('frequency')
        
    #     job = db.session.query(DBModels.Job).filter_by(script_name=script_name).first()
    #     if job:
    #         job.frequency = frequency
    #     else:
    #         job = DBModels.Job(script_name=script_name, frequency=frequency)
    #         db.session.add(job)
        
    #     db.session.commit()
        
    #     scheduler.add_job(
    #         execute_script,
    #         CronTrigger.from_crontab(frequency),
    #         args=[script_name],
    #         id=script_name
    #     )
        
    #     return jsonify({'message': 'Job added successfully'}), 200

    # @job_router.route('/job/<int:job_id>', methods=['DELETE'])
    # def cancel_job(job_id):
    #     job = db.session.query(DBModels.Job).get(job_id)
    #     if job:
    #         scheduler.remove_job(job.script_name)
    #         db.session.delete(job)
    #         job.status = 'inactive'
    #         db.session.commit()
    #         return jsonify({'message': 'Job deleted successfully'}), 200
    #     else:
    #         return jsonify({'error': 'Job not found'}), 404






# Scripts Route
# @job_router.route('/<script_name>', methods=['POST'])
# def run_script(script_name):
#     try:

        # SCRIPTS_FOLDER = "./app/scripts/"
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