import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.jobs.repository import Repository
from app.models.job import JobStatus, JobModelRegistry

logger = logging.getLogger(__name__)

class JobService:
    def __init__(self, db=None):
        self.repo = Repository(db)
        self._scheduler = None
    
    @property
    def scheduler(self):
        """Lazy initialization of scheduler to avoid circular imports"""
        if self._scheduler is None:
            from app.jobs.scheduler_service import SchedulerService
            self._scheduler = SchedulerService()
        return self._scheduler
    
    def _get_job_model(self):
        """Get the Job model from the registry"""
        return JobModelRegistry.get_job_class()
    
    def get_all(self) -> List[Dict[str, Any]]:
        """Get all jobs with their current status."""
        try:
            jobs = self.repo.get_jobs()
            jobs_serialized = []
            
            for job in jobs:
                job_data = job.to_dict()
                # Get scheduler status for each job
                scheduler_status = self.scheduler.get_job_status(job.id)
                if scheduler_status:
                    job_data['scheduled'] = scheduler_status['scheduled']
                    job_data['next_run_time'] = scheduler_status['next_run_time']
                else:
                    job_data['scheduled'] = False
                    job_data['next_run_time'] = None
                
                jobs_serialized.append(job_data)
            
            return jobs_serialized
            
        except Exception as e:
            logger.error(f"Error getting all jobs: {str(e)}")
            raise e

    def get(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific job by ID."""
        try:
            job = self.repo.get_job(job_id)
            if not job:
                return None
            
            job_data = job.to_dict()
            # Get scheduler status
            scheduler_status = self.scheduler.get_job_status(job_id)
            if scheduler_status:
                job_data['scheduled'] = scheduler_status['scheduled']
                job_data['next_run_time'] = scheduler_status['next_run_time']
            else:
                job_data['scheduled'] = False
                job_data['next_run_time'] = None
            
            return job_data
            
        except Exception as e:
            logger.error(f"Error getting job {job_id}: {str(e)}")
            raise e
    
    def add(self, script_name: str, frequency: str, description: str = None) -> Dict[str, Any]:
        """Add a new job and schedule it."""
        try:
            # Validate inputs
            if not script_name or not frequency:
                raise ValueError("Script name and frequency are required")
            
            # Check if job already exists
            existing_job = self.repo.get_job(script_name)
            if existing_job:
                raise ValueError(f"Job with script name '{script_name}' already exists")
            
            # Create new job
            Job = self._get_job_model()
            job = Job(
                id=script_name,
                script_name=script_name,
                frequency=frequency,
                status=JobStatus.ACTIVE,
                description=description
            )
            
            # Add to database
            self.repo.add_job(job)
            
            # Schedule the job
            if not self.scheduler.schedule_job(job):
                # If scheduling fails, mark job as inactive
                self.repo.update_job_status(script_name, JobStatus.INACTIVE)
                raise RuntimeError(f"Failed to schedule job for script '{script_name}'")
            
            # Get the scheduled job info
            scheduler_status = self.scheduler.get_job_status(script_name)
            if scheduler_status and scheduler_status['next_run_time']:
                # Convert ISO string back to datetime object for database storage
                from datetime import datetime
                next_run_time = datetime.fromisoformat(scheduler_status['next_run_time'].replace('Z', '+00:00'))
                self.repo.update_job_next_run(script_name, next_run_time)
            
            logger.info(f"Job '{script_name}' added and scheduled successfully")
            return self.get(script_name)
            
        except Exception as e:
            logger.error(f"Error adding job '{script_name}': {str(e)}")
            raise e
    
    def update(self, job_id: str, frequency: str = None, description: str = None) -> Optional[Dict[str, Any]]:
        """Update an existing job."""
        try:
            job = self.repo.get_job(job_id)
            if not job:
                raise ValueError(f"Job '{job_id}' not found")
            
            # Update fields if provided
            if frequency:
                job.frequency = frequency
            if description is not None:
                job.description = description
            
            # Update in database
            self.repo.update_job(job)
            
            # Reschedule if frequency changed
            if frequency:
                if not self.scheduler.reschedule_job(job):
                    raise RuntimeError(f"Failed to reschedule job '{job_id}'")
                
                # Update next run time
                scheduler_status = self.scheduler.get_job_status(job_id)
                if scheduler_status and scheduler_status['next_run_time']:
                    # Convert ISO string back to datetime object for database storage
                    from datetime import datetime
                    next_run_time = datetime.fromisoformat(scheduler_status['next_run_time'].replace('Z', '+00:00'))
                    self.repo.update_job_next_run(job_id, next_run_time)
            
            logger.info(f"Job '{job_id}' updated successfully")
            return self.get(job_id)
            
        except Exception as e:
            logger.error(f"Error updating job '{job_id}': {str(e)}")
            raise e
    
    def cancel(self, job_id: str) -> bool:
        """Cancel a job by marking it inactive and unscheduling it."""
        try:
            job = self.repo.get_job(job_id)
            if not job:
                return False
            
            # Unschedule the job
            self.scheduler.unschedule_job(job)
            
            # Mark as inactive
            self.repo.update_job_status(job_id, JobStatus.INACTIVE)
            
            # Clear next run time
            self.repo.update_job_next_run(job_id, None)
            
            logger.info(f"Job '{job_id}' cancelled successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error cancelling job '{job_id}': {str(e)}")
            raise e
    
    def activate(self, job_id: str) -> bool:
        """Activate a previously cancelled job."""
        try:
            job = self.repo.get_job(job_id)
            if not job:
                return False
            
            # Mark as active
            self.repo.update_job_status(job_id, JobStatus.ACTIVE)
            
            # Schedule the job
            if not self.scheduler.schedule_job(job):
                # If scheduling fails, mark job as inactive
                self.repo.update_job_status(job_id, JobStatus.INACTIVE)
                raise RuntimeError(f"Failed to schedule job '{job_id}'")
            
            # Update next run time
            scheduler_status = self.scheduler.get_job_status(job_id)
            if scheduler_status and scheduler_status['next_run_time']:
                # Convert ISO string back to datetime object for database storage
                from datetime import datetime
                next_run_time = datetime.fromisoformat(scheduler_status['next_run_time'].replace('Z', '+00:00'))
                self.repo.update_job_next_run(job_id, next_run_time)
            
            logger.info(f"Job '{job_id}' activated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error activating job '{job_id}': {str(e)}")
            raise e
    
    def run_now(self, job_id: str) -> Dict[str, Any]:
        """Run a job immediately."""
        try:
            job = self.repo.get_job(job_id)
            if not job:
                raise ValueError(f"Job '{job_id}' not found")
            
            # Update status to running
            self.repo.update_job_status(job_id, JobStatus.RUNNING)
            
            # Execute the script
            result = self.scheduler.execute_script(job.script_name, job.id)
            
            # Update last run time
            self.repo.update_job_last_run(job_id, datetime.utcnow())
            
            # Update status based on result
            if result['success']:
                self.repo.update_job_status(job_id, JobStatus.ACTIVE)
                logger.info(f"Job '{job_id}' executed successfully")
            else:
                self.repo.update_job_status(job_id, JobStatus.FAILED)
                logger.error(f"Job '{job_id}' execution failed: {result.get('error', 'Unknown error')}")
            
            return {
                'job_id': job_id,
                'execution_result': result,
                'status': self.repo.get_job(job_id).status.value
            }
            
        except Exception as e:
            logger.error(f"Error running job '{job_id}' now: {str(e)}")
            # Reset status to active if there was an error
            if job:
                self.repo.update_job_status(job_id, JobStatus.ACTIVE)
            raise e
    
    def get_scheduler_status(self) -> Dict[str, Any]:
        """Get the overall scheduler status."""
        try:
            return {
                'running': self.scheduler.scheduler.running,
                'job_count': len(self.scheduler.get_all_jobs()),
                'jobs': self.scheduler.get_all_jobs()
            }
        except Exception as e:
            logger.error(f"Error getting scheduler status: {str(e)}")
            raise e