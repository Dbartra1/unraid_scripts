import os
import subprocess

from apscheduler.triggers.cron import CronTrigger
from flask import jsonify
from sqlalchemy.ext.declarative import DeclarativeMeta

from app.database.repository import Repository
from app.models.job import Job, JobStatus
from app.services.scheduler_service import SchedulerService

repo = Repository()
scheduler_service = SchedulerService()

class JobService:
    def __init__(self):
        pass

    def get_jobs(self) -> list[Job]:
        jobs = repo.get_jobs()
        jobs_serialized = [
            {
                'id': job.id,
                'script_name': job.script_name,
                'frequency': job.frequency,
                'status': str(job.status),
            }
            for job in jobs
        ]
        return jobs_serialized

    def get_job(self, job_id) -> Job:
        job = repo.get_job(job_id)
        job_serialized = {
            'id': job.id,
            'script_name': job.script_name,
            'frequency': job.frequency
        }
        return job_serialized
    
    def add_job(self, script_name, frequency) -> Job:
        # TODO validate inputs

        job = repo.get_job()
        if job:
            return # TODO error handling
        else:
            job = Job(
                script_name=script_name,
                frequency=frequency,
                status=JobStatus.ACTIVE
            )

        repo.add_job(job) # TODO error handling
        scheduler_service.schedule(job) # TODO error handling

        return job
    
    def update_job(self, job_id, new_frequency) -> Job:
        # TODO validate inputs

        job = repo.get_job(job_id) # TODO error handling
        if job:
            job.frequency = new_frequency
        
        repo.update_job() # TODO this work?
        scheduler_service.reschedule(job)

        return job
    
    def cancel_job(self, job_id):
        job = repo.get_job(job_id)
        if job:
            scheduler_service.remove(job)
            repo.delete_job(job)

            return jsonify({'message': 'Job deleted successfully'}), 200 # TODO error handling
        else:
            return