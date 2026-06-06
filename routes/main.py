from flask import Blueprint, render_template
from flask_login import current_user
from models.rental_item import RentalItem
from extensions import db
from flask import request, redirect, url_for
from flask_login import login_required


main = Blueprint("main", __name__)


@main.route("/")
def home():
    return render_template("index.html")


@main.route("/browse")
def browse():

    rentals = RentalItem.query.filter_by(
        status="approved"
    ).all()

    return render_template(
        "browse.html",
        rentals=rentals
    )

@main.route("/create-listing", methods=["GET", "POST"])
@login_required
def create_listing():

    if request.method == "POST":

        title = request.form.get("title")
        description = request.form.get("description")
        price = request.form.get("price")
        category = request.form.get("category")

        item = RentalItem(
            title=title,
            description=description,
            price_per_day=price,
            category=category,
            user_id=current_user.id,
            status="pending"
        )
        db.session.add(item)
        db.session.commit()

        return redirect(
            url_for("main.browse")
        )

    return render_template(
        "create_listing.html"
    )

@main.route("/admin/listings")
def admin_listings():

    rentals = RentalItem.query.filter_by(
        status="pending"
    ).all()

    return render_template(
        "admin_listings.html",
        rentals=rentals
    )

@main.route("/approve/<int:id>")
def approve_listing(id):

    rental = RentalItem.query.get_or_404(id)

    rental.status = "approved"

    db.session.commit()

    return redirect(
        url_for("main.admin_listings")
    )