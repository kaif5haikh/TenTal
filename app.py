from flask import Flask
from dotenv import load_dotenv
import os

from extensions import db, login_manager
from flask_migrate import Migrate
from routes.main import main
from routes.auth import auth

from models.user import User
from models.rental_item import RentalItem
from models.booking import Booking
from models.review import Review

# Load environment variables from .env file
load_dotenv()

# Create Flask application instance
app = Flask(__name__)


app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = "static/uploads"

# Attach SQLAlchemy database instance to Flask app
db.init_app(app)

migrate = Migrate(app, db)

# Initialize Flask-Login for user session management
login_manager.init_app(app)
login_manager.login_view = "auth.login"


# Initialize Flask-Login for user session management
app.register_blueprint(main)
app.register_blueprint(auth)

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)