import os
import subprocess

from apscheduler.triggers.cron import CronTrigger

from app.extensions import scheduler
from app.models.job import Job

def execute_script(script_name):
    script_path = os.path.join("app", script_name)
    result = subprocess.run(
        ["python", script_path],
        capture_output=True,
        text=True
    )
    print(result.stdout)

class SchedulerService:
    def __init__(self):
        pass

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
    
    def remove(self, job: Job): # TODO return something for error handling
        scheduler.remove_job(job_id=job.script_name)
