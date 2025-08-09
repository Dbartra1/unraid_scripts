import os
import subprocess
import logging
from typing import Optional, Dict, Any
from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.pool import ThreadPoolExecutor

# Remove the import to break circular dependency
# from app.models.job import JobStatus, JobModelRegistry

logger = logging.getLogger(__name__)

class SchedulerService:
    def __init__(self):
        # Configure the scheduler with proper job stores and executors
        jobstores = {
            'default': MemoryJobStore()
        }
        executors = {
            'default': ThreadPoolExecutor(20)
        }
        job_defaults = {
            'coalesce': False,
            'max_instances': 3
        }
        
        self.scheduler = BackgroundScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults
        )
        
        # Start the scheduler
        self.scheduler.start()
    
    def _get_job_model(self):
        """Get the Job model from the registry"""
        from app.models.job import JobModelRegistry
        return JobModelRegistry.get_job_class()
    
    def parse_frequency(self, frequency: str) -> str:
        """
        Parse frequency string and convert to cron expression.
        Supports common formats like 'daily', 'hourly', 'weekly' and cron expressions.
        """
        frequency_lower = frequency.lower().strip()
        
        # Common frequency mappings
        frequency_map = {
            'hourly': '0 * * * *',
            'daily': '0 0 * * *',
            'weekly': '0 0 * * 0',
            'monthly': '0 0 1 * *',
            'yearly': '0 0 1 1 *',
            'every_minute': '* * * * *',
            'every_5_minutes': '*/5 * * * *',
            'every_15_minutes': '*/15 * * * *',
            'every_30_minutes': '*/30 * * * *'
        }
        
        if frequency_lower in frequency_map:
            return frequency_map[frequency_lower]
        
        # If it's already a cron expression, validate and return
        try:
            CronTrigger.from_crontab(frequency)
            return frequency
        except ValueError:
            # Default to daily if invalid
            logger.warning(f"Invalid frequency '{frequency}', defaulting to daily")
            return '0 0 * * *'
    
    def execute_script(self, script_name: str, job_id: str) -> Dict[str, Any]:
        """
        Execute a script and return the result.
        """
        try:
            # Look for script in multiple possible locations
            script_paths = [
                os.path.join("app", "scripts", f"{script_name}.py"),
                os.path.join("app", "scripts", script_name),
                os.path.join("app", f"{script_name}.py"),
                os.path.join("app", script_name)
            ]
            
            script_path = None
            for path in script_paths:
                if os.path.exists(path):
                    script_path = path
                    break
            
            if not script_path:
                logger.error(f"Script not found: {script_name}")
                return {
                    'success': False,
                    'error': f'Script not found: {script_name}',
                    'stdout': '',
                    'stderr': ''
                }
            
            # Execute the script
            result = subprocess.run(
                ["python", script_path],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            logger.info(f"Script {script_name} executed with return code: {result.returncode}")
            
            return {
                'success': result.returncode == 0,
                'return_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
            
        except subprocess.TimeoutExpired:
            logger.error(f"Script {script_name} timed out")
            return {
                'success': False,
                'error': 'Script execution timed out',
                'stdout': '',
                'stderr': ''
            }
        except Exception as e:
            logger.error(f"Error executing script {script_name}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'stdout': '',
                'stderr': ''
            }
    
    def schedule_job(self, job: 'Job') -> bool:
        """
        Schedule a job in the scheduler.
        """
        try:
            cron_expression = self.parse_frequency(job.frequency)
            
            # Add the job to the scheduler
            self.scheduler.add_job(
                func=self.execute_script,
                trigger=CronTrigger.from_crontab(cron_expression),
                args=[job.script_name, job.id],
                id=f"job_{job.id}",
                name=f"Script: {job.script_name}",
                replace_existing=True
            )
            
            logger.info(f"Job {job.id} scheduled successfully with frequency: {cron_expression}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to schedule job {job.id}: {str(e)}")
            return False
    
    def reschedule_job(self, job: 'Job') -> bool:
        """
        Reschedule an existing job with new frequency.
        """
        try:
            # Remove existing job
            self.unschedule_job(job)
            
            # Schedule with new frequency
            return self.schedule_job(job)
            
        except Exception as e:
            logger.error(f"Failed to reschedule job {job.id}: {str(e)}")
            return False
    
    def unschedule_job(self, job: 'Job') -> bool:
        """
        Remove a job from the scheduler.
        """
        try:
            job_id = f"job_{job.id}"
            if self.scheduler.get_job(job_id):
                self.scheduler.remove_job(job_id)
                logger.info(f"Job {job.id} unscheduled successfully")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to unschedule job {job.id}: {str(e)}")
            return False
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the current status of a scheduled job.
        """
        try:
            scheduler_job_id = f"job_{job_id}"
            job = self.scheduler.get_job(scheduler_job_id)
            
            if job:
                return {
                    'id': job_id,
                    'next_run_time': job.next_run_time.isoformat() if job.next_run_time else None,
                    'scheduled': True
                }
            else:
                return {
                    'id': job_id,
                    'next_run_time': None,
                    'scheduled': False
                }
                
        except Exception as e:
            logger.error(f"Failed to get job status for {job_id}: {str(e)}")
            return None
    
    def get_all_jobs(self) -> list:
        """
        Get all scheduled jobs.
        """
        try:
            jobs = []
            for job in self.scheduler.get_jobs():
                jobs.append({
                    'id': job.id,
                    'name': job.name,
                    'next_run_time': job.next_run_time.isoformat() if job.next_run_time else None,
                    'trigger': str(job.trigger)
                })
            return jobs
            
        except Exception as e:
            logger.error(f"Failed to get all jobs: {str(e)}")
            return []
    
    def shutdown(self):
        """
        Shutdown the scheduler gracefully.
        """
        try:
            self.scheduler.shutdown(wait=True)
            logger.info("Scheduler shutdown successfully")
        except Exception as e:
            logger.error(f"Error during scheduler shutdown: {str(e)}")
