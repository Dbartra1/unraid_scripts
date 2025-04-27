from app.models.job import Job, JobStatus
from app.extensions import db

class Repository:
    def get_jobs(self):
        return  db.session.query(Job).all()

    def get_job(self, job_id):
        return db.session.query(Job).filter_by(id=job_id).first()
    
    def add_job(self, job: Job):
        db.session.add(job)
        db.session.commit()
    
    def update_job(self):
        db.session.commit()

    def delete_job(self, job: Job):
        job.status = JobStatus.INACTIVE
        db.session.commit()