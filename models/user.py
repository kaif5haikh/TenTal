from flask_login import UserMixin
from extensions import db
from extensions import login_manager



# User database model
# Stores user account information used for authentication
class User(UserMixin, db.Model):

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(255),
        nullable=False
    )

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))