import os

from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from app.extensions import db, scheduler
from app.api import routes
from app.models.job import Job, JobStatus

load_dotenv()

# Run from base directory of unraid_scripts project with python(3) -m app.app
# Dillon which doc would you like me to put this in?

# Load server IP and port number from environment variables
SERVER_IP = os.getenv('SERVER_IP', '127.0.0.1')
PORT_NUMBER_FLASK = int(os.getenv('PORT_NUMBER_FLASK', 5000))


def create_app() -> Flask:
    app = Flask(__name__)
    app.register_blueprint(routes.job_router_blueprint)

    return app


def configure_container(app: Flask):
    # init DB
    # persistent DB, disabled for now
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    # in memory DB for development, maybe should be the default option
    # based on how you've described your vision of the DB lifecycle
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    db.init_app(app)
    
    with app.app_context():
        db.create_all()

    # start app scheduler
    scheduler.start()


def seed_test_jobs(app: Flask, db: SQLAlchemy):
    jobs = [
        Job(
            id=id,
            script_name="yada",
            frequency="daily",
            status=JobStatus.ACTIVE,
        )
        for id in range(0, 10)]
    with app.app_context():
        db.session.add_all(jobs)
        db.session.commit()


if __name__ == "__main__":
    app = create_app()
    configure_container(app)

    if os.getenv("SEED_TEST_DATA", "false").lower() == "true":
        seed_test_jobs(app, db)

    app.run(host=SERVER_IP, port=PORT_NUMBER_FLASK)