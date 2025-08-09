from enum import Enum
from datetime import datetime
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column

class JobStatus(Enum):
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    COMPLETED = 'completed'
    RUNNING = 'running'
    FAILED = 'failed'

    def __str__(self):
        return str(self.value).lower()

class JobModelRegistry:
    """Registry to hold the Job model class"""
    _job_class = None
    
    @classmethod
    def set_job_class(cls, job_class):
        cls._job_class = job_class
    
    @classmethod
    def get_job_class(cls):
        if cls._job_class is None:
            raise RuntimeError("Job model not initialized. Call create_job_model first.")
        return cls._job_class

def create_job_model(db):
    """Create the Job model class with the given db instance"""
    class Job(db.Model):
        __tablename__ = 'jobs'
        
        id: Mapped[str] = mapped_column(String(120), primary_key=True)
        script_name: Mapped[str] = mapped_column(String(120))
        frequency: Mapped[str] = mapped_column(String(120))
        status: Mapped[JobStatus] = mapped_column(insert_default=JobStatus.ACTIVE)
        created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
        last_run: Mapped[datetime] = mapped_column(DateTime, nullable=True)
        next_run: Mapped[datetime] = mapped_column(DateTime, nullable=True)
        description: Mapped[str] = mapped_column(String(500), nullable=True)
        
        def to_dict(self):
            """Convert job to dictionary for serialization."""
            return {
                'id': self.id,
                'script_name': self.script_name,
                'frequency': self.frequency,
                'status': str(self.status),
                'created_at': self.created_at.isoformat() if self.created_at else None,
                'last_run': self.last_run.isoformat() if self.last_run else None,
                'next_run': self.next_run.isoformat() if self.next_run else None,
                'description': self.description
            }
    
    # Register the created class
    JobModelRegistry.set_job_class(Job)
    return Job

# For backward compatibility
Job = None