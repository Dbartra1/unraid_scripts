from enum import Enum
from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.extensions import db

class JobStatus(Enum):
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    COMPLETED = 'completed'

class Job(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    script_name: Mapped[str] = mapped_column(String(120))
    frequency: Mapped[str] = mapped_column(String(120))
    status: Mapped[JobStatus] = mapped_column(insert_default=JobStatus.ACTIVE)