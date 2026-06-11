from extensions import db
from datetime import datetime



class Booking(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
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

    status = db.Column(
        db.String(20),
        default="pending"
    )
    start_date = db.Column(
        db.Date,
        nullable=False
    )

    end_date = db.Column(
        db.Date,
        nullable=False
    )

    total_price = db.Column(
        db.Float,
        nullable=False
    )
    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )
    quantity_booked = db.Column(
        db.Integer,
        nullable=False,
        default=1
    )
    security_deposit = db.Column(
        db.Float,
        nullable=False,
        default=0
    )
    review = db.relationship(
        "Review",
        backref="booking",
        uselist=False
    )