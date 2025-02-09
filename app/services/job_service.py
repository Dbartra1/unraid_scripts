import os
import subprocess
from apscheduler.schedulers.background import BackgroundScheduler
from app.database import repository
# from apscheduler.triggers.cron import CronTrigger
from flask import jsonify

repo = repository.Repository()

# def execute_script(script_name):
#     script_path = os.path.join("app", script_name)
#     result = subprocess.run(
#         ["python", script_path],
#         capture_output=True,
#         text=True
#     )
#     print(result.stdout)

class JobService:
    def __init__(self):
        scheduler = BackgroundScheduler()
        scheduler.start()

        self.scheduler = scheduler
        # self.repo = repo

    def get_jobs(self):
        return repo.get_jobs()
        # jobs = self.repo.get_jobs()
        # jobs = [
        #     {
        #         'id': job.id,
        #         'script_name': job.script_name,
        #         'frequency': job.frequency,
        #         'status': job.status
        #     }
        #     for job in jobs
        # ]
        # return jsonify(jobs), 200
    
    # def add_job(self):
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
        
    #     self.scheduler.add_job(
    #         execute_script,
    #         CronTrigger.from_crontab(frequency),
    #         args=[script_name],
    #         id=script_name
    #     )
        
    #     return jsonify({'message': 'Job added successfully'}), 200
    
    # def cancel_job(self, job_id):
    #     job = db.session.query(DBModels.Job).get(job_id)
    #     if job:
    #         self.scheduler.remove_job(job.script_name)
    #         db.session.delete(job)
    #         job.status = 'inactive'
    #         db.session.commit()
    #         return jsonify({'message': 'Job deleted successfully'}), 200
    #     else:
    #         return jsonify({'error': 'Job not found'}), 404