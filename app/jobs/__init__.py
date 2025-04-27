# define the blueprint for routes.py here
from flask import Blueprint

bp = Blueprint('job_router', __name__, url_prefix="/job")

from app.jobs import routes