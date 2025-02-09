import os

from dotenv import load_dotenv
from flask import Flask

from app.extensions import db
from app.api import routes
from app.models.job import Job, JobStatus

load_dotenv()

# Run from base directory of unraid_scripts project with python(3) -m app.app
# Dillon which doc would you like me to put this in?

# Load server IP and port number from environment variables
SERVER_IP = os.getenv('SERVER_IP', '127.0.0.1')
PORT_NUMBER_FLASK = int(os.getenv('PORT_NUMBER_FLASK', 5000))

app = Flask(__name__)

# persistent DB, disabled for now
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
# in memory DB for development
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

db.init_app(app)
    
# Initialize the database
with app.app_context():
    db.create_all()

app.register_blueprint(routes.job_router_blueprint)


if __name__ == "__main__":
    jobs = []
    for id in range(0, 10):
        jobs.append(Job(
            id=id,
            script_name="yada",
            frequency="daily",
            status=JobStatus.ACTIVE,
        ))
    with app.app_context():
        for job in jobs:
            db.session.add(job)
            db.session.commit()

    app.run(host=SERVER_IP, port=PORT_NUMBER_FLASK)