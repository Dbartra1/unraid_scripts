from enum import Enum
from sqlalchemy import String, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class JobStatus(Enum):
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    COMPLETED = 'completed'

# Job model
class Job(Base):
    __tablename__ = "job"

    id = mapped_column(Integer, primary_key=True)
    script_name: Mapped[str] = mapped_column(String(120))
    frequency: Mapped[str] = mapped_column(String(120))
    status: Mapped[JobStatus] = mapped_column(insert_default=JobStatus.ACTIVE)