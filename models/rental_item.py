from extensions import db

class RentalItem(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(100), nullable=False)

    description = db.Column(db.Text, nullable=False)

    price_per_day = db.Column(db.Float, nullable=False)

    category = db.Column(db.String(100), nullable=False)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    status = db.Column(
        db.String(20),
        default="pending"
    )

    image = db.Column(
        db.String(255)
    )
    bookings = db.relationship(
        "Booking",
        backref="rental_item",
        lazy=True
    )

    quantity = db.Column(
        db.Integer,
        nullable=False,
        default=1
    )
    security_deposit = db.Column(
        db.Float,
        nullable=False,
        default=0
    )