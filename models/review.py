from extensions import db
from datetime import datetime

class Review(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    rating = db.Column(
        db.Integer,
        nullable=False
    )

    comment = db.Column(
        db.Text,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    booking_id = db.Column(
        db.Integer,
        db.ForeignKey("booking.id"),
        nullable=False,
        unique=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    rental_item_id = db.Column(
        db.Integer,
        db.ForeignKey("rental_item.id"),
        nullable=False
    )