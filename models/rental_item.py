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