from datetime import datetime, UTC
from extensions import db


class Payment(db.Model):
    __tablename__ = "payment"

    id = db.Column(db.Integer, primary_key=True)

    booking_id = db.Column(
        db.Integer,
        db.ForeignKey("booking.id"),
        nullable=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    amount = db.Column(
        db.Float,
        nullable=False
    )

    currency = db.Column(
        db.String(10),
        default="INR",
        nullable=False
    )

    razorpay_order_id = db.Column(
        db.String(255),
        unique=True
    )

    razorpay_payment_id = db.Column(
        db.String(255),
        unique=True
    )

    razorpay_signature = db.Column(
        db.String(255)
    )

    payment_method = db.Column(
        db.String(50)
    )

    status = db.Column(
        db.String(50),
        default="created",
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(UTC)
    )