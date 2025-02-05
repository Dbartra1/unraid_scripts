import os
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler
from api import routes

load_dotenv()

# Load server IP and port number from environment variables
SERVER_IP = os.getenv('SERVER_IP', '127.0.0.1')
PORT_NUMBER_FLASK = int(os.getenv('PORT_NUMBER_FLASK', 5000))

SCRIPTS_FOLDER = "./app/scripts/"

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

scheduler = BackgroundScheduler()
scheduler.start()
    
# Initialize the database
with app.app_context():
    db.create_all()


# @app.route("/")
# def home():
#     return render_template("index.html")

if __name__ == "__main__":
    app.register_blueprint(routes.job_router)
    app.run(host=SERVER_IP, port=PORT_NUMBER_FLASK)
