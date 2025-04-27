import os
import subprocess

from apscheduler.triggers.cron import CronTrigger
from flask import jsonify
from sqlalchemy.ext.declarative import DeclarativeMeta

from app.jobs.repository import Repository
from app.models.job import Job, JobStatus

from app.extensions import scheduler

repo = Repository()

def execute_script(script_name):
    script_path = os.path.join("app", script_name)
    result = subprocess.run(
        ["python", script_path],
        capture_output=True,
        text=True
    )
    print(result.stdout)

class JobService:
    def get_all(self) -> list[Job]:
        jobs = repo.get_jobs()
        jobs_serialized = [
            {
                'id': job.id,
                'script_name': job.script_name,
                'frequency': job.frequency,
                'status': str(job.status),
            }
            for job in jobs
        ] # TODO proper serializations
        return jobs_serialized

    def get(self, job_id) -> Job:
        # TODO validate input
        job = repo.get_job(job_id)
        job_serialized = {
            'id': job.id,
            'script_name': job.script_name,
            'frequency': job.frequency
        } # TODO proper serialization
        return job_serialized
    
    def add(self, script_name, frequency) -> Job:
        # TODO validate inputs

        job_serialized = {}
        try:
            job = repo.get_job(script_name)
        except:
            job = Job(
                id=script_name,
                script_name=script_name,
                frequency=frequency,
                status=JobStatus.ACTIVE
            )

            # scheduler_service.schedule(job) # TODO make this work
            repo.add_job(job) # TODO error handling

            job_serialized = {
                "id": script_name,
                "script_name": script_name,
                "frequency": frequency,
                "status": "active"
            } # TODO proper serialization

        return job_serialized
    
    def update(self, job_id, new_frequency) -> Job:
        # TODO validate inputs

        job = repo.get_job(job_id) # TODO error handling
        if job:
            job.frequency = new_frequency
        
        # scheduler_service.reschedule(job) # TODO make this work
        repo.update_job()

        return {
            "id": job_id,
            "script_name": job_id,
            "frequency": new_frequency,
            "status": "active",
        } # TODO proper serialization
    
    def cancel(self, job_id):
        job = repo.get_job(job_id)
        if job:
            # scheduler_service.remove(job) # TODO make this work
            repo.delete_job(job)

            self.unschedule(job)

            return jsonify({'message': 'Job deleted successfully'}), 200 # TODO error handling
        else:
            return jsonify({'error': 'Job not found'}), 404

    def schedule(self, job: Job): # TODO return something for error handling
        return scheduler.add_job(
            func=execute_script,
            trigger=CronTrigger.from_crontab(job.frequency),
            args=[job.script_name],
            id=job.script_name,
        )

    def reschedule(self, job: Job): # TODO return something for error handling
        return scheduler.reschedule_job(
            job_id=job.script_name,
            trigger=CronTrigger.from_crontab(job.frequency)
        )
    
    def unschedule(self, job: Job): # TODO return something for error handling
        scheduler.remove_job(job_id=job.script_name)