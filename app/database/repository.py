from app.models import job
from app.extensions import db

class Repository:
    def __init__(self):
        pass

    def get_jobs(self):
        return  db.session.query(job.Job).all()