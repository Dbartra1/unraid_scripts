from enum import Enum
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.extensions import db

class JobStatus(Enum):
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    COMPLETED = 'completed'

    def __str__(self):
        return str(self.value).lower()

class Job(db.Model):
    id: Mapped[str] = mapped_column(String(120), primary_key=True)
    script_name: Mapped[str] = mapped_column(String(120))
    frequency: Mapped[str] = mapped_column(String(120))
    status: Mapped[JobStatus] = mapped_column(insert_default=JobStatus.ACTIVE)