from typing import List, Optional
from app.models.job import JobStatus, JobModelRegistry

class Repository:
    def __init__(self, db=None):
        self.db = db
    
    def _get_job_model(self):
        """Get the Job model from the registry"""
        return JobModelRegistry.get_job_class()
    
    def get_jobs(self) -> List:
        """Get all jobs from the database."""
        try:
            Job = self._get_job_model()
            return self.db.session.query(Job).all()
        except Exception as e:
            self.db.session.rollback()
            raise e

    def get_job(self, job_id: str):
        """Get a specific job by ID."""
        try:
            Job = self._get_job_model()
            return self.db.session.query(Job).filter_by(id=job_id).first()
        except Exception as e:
            self.db.session.rollback()
            raise e
    
    def add_job(self, job) -> bool:
        """Add a new job to the database."""
        try:
            self.db.session.add(job)
            self.db.session.commit()
            return True
        except Exception as e:
            self.db.session.rollback()
            raise e
    
    def update_job(self, job) -> bool:
        """Update an existing job."""
        try:
            self.db.session.commit()
            return True
        except Exception as e:
            self.db.session.rollback()
            raise e

    def delete_job(self, job) -> bool:
        """Mark a job as inactive instead of deleting."""
        try:
            job.status = JobStatus.INACTIVE
            self.db.session.commit()
            return True
        except Exception as e:
            self.db.session.rollback()
            raise e
    
    def update_job_status(self, job_id: str, status: JobStatus) -> bool:
        """Update the status of a specific job."""
        try:
            job = self.get_job(job_id)
            if job:
                job.status = status
                self.db.session.commit()
                return True
            return False
        except Exception as e:
            self.db.session.rollback()
            raise e
    
    def update_job_last_run(self, job_id: str, last_run) -> bool:
        """Update the last run time of a job."""
        try:
            job = self.get_job(job_id)
            if job:
                job.last_run = last_run
                self.db.session.commit()
                return True
            return False
        except Exception as e:
            self.db.session.rollback()
            raise e
    
    def update_job_next_run(self, job_id: str, next_run) -> bool:
        """Update the next run time of a job."""
        try:
            job = self.get_job(job_id)
            if job:
                job.next_run = next_run
                self.db.session.commit()
                return True
            return False
        except Exception as e:
            self.db.session.rollback()
            raise e