import os
import logging
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from app.extensions import db
from app.jobs import bp as jobs_bp

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Run from base directory of unraid_scripts project with python(3) -m app.app

# Load server IP and port number from environment variables
SERVER_IP = os.getenv('SERVER_IP', '0.0.0.0')  # IP must be 0.0.0.0 to expose API with Docker
PORT_NUMBER_FLASK = int(os.getenv('PORT_NUMBER_FLASK', 5000))


def create_app() -> Flask:
    app = Flask(__name__)
    
    # Register blueprints
    app.register_blueprint(jobs_bp, url_prefix='/api/jobs')
    
    # Configure extensions
    configure_extensions(app)
    
    return app


def configure_extensions(app: Flask):
    """Configure Flask extensions."""
    # Configure database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db.init_app(app)
    
    # Create database tables
    with app.app_context():
        # Initialize the Job model first
        from app.models.job import create_job_model
        global Job
        Job = create_job_model(db)
        
        # Now create all tables after the model is defined
        db.create_all()
        logging.info("Database initialized successfully")
        logging.info("Job model initialized successfully")
    
    # Note: Scheduler is initialized in JobService when needed
    logging.info("Extensions configured successfully")


def seed_test_jobs(app: Flask, db: SQLAlchemy):
    """Seed the database with test jobs if SEED_TEST_DATA is enabled."""
    try:
        from app.models.job import JobStatus
        
        # Use the global Job variable that was initialized in configure_extensions
        global Job
        
        if Job is None:
            logging.warning("Job model not initialized, skipping test data seeding")
            return
        
        jobs = [
            Job(
                id="test_script_1",
                script_name="test_script_1",
                frequency="daily",
                status=JobStatus.ACTIVE,
                description="Test script that runs daily"
            ),
            Job(
                id="test_script_2", 
                script_name="test_script_2",
                frequency="hourly",
                status=JobStatus.ACTIVE,
                description="Test script that runs hourly"
            )
        ]
        
        with app.app_context():
            db.session.add_all(jobs)
            db.session.commit()
            logging.info("Test jobs seeded successfully")
            
    except Exception as e:
        logging.error(f"Failed to seed test jobs: {str(e)}")


if __name__ == "__main__":
    app = create_app()
    
    # Always seed test data for testing
    seed_test_jobs(app, db)
    
    # Run the application
    logging.info(f"Starting Flask app on {SERVER_IP}:{PORT_NUMBER_FLASK}")
    app.run(host=SERVER_IP, port=PORT_NUMBER_FLASK, debug=True)