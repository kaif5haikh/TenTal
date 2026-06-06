from flask import Blueprint, render_template
from flask_login import current_user
from models.rental_item import RentalItem
from extensions import db
from flask import request, redirect, url_for
from flask_login import login_required
import os
from werkzeug.utils import secure_filename
from flask import current_app


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

@main.route("/listing/<int:id>")
def listing_detail(id):

    rental = RentalItem.query.get_or_404(id)

    return render_template(
        "listing_detail.html",
        rental=rental
    )

@main.route("/create-listing", methods=["GET", "POST"])
@login_required
def create_listing():

    if request.method == "POST":

        title = request.form.get("title")
        description = request.form.get("description")
        price = request.form.get("price")
        category = request.form.get("category")
        image = request.files.get("image")

        filename = None

        if image and image.filename:

            filename = secure_filename(
                image.filename
            )

            image.save(
                os.path.join(
                    current_app.config["UPLOAD_FOLDER"],
                    filename
                )
            )

        item = RentalItem(
            title=title,
            description=description,
            price_per_day=price,
            category=category,
            image=filename,
            user_id=current_user.id,
            status="pending",
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
@login_required
def admin_listings():
    if not current_user.is_admin:
        return "Access Denied"

    rentals = RentalItem.query.filter_by(
        status="pending"
    ).all()

    return render_template(
        "admin_listings.html",
        rentals=rentals
    )

@main.route("/approve/<int:id>")
@login_required
def approve_listing(id):
    if not current_user.is_admin:
        return "Access Denied"

    rental = RentalItem.query.get_or_404(id)

    rental.status = "approved"

    db.session.commit()

    return redirect(
        url_for("main.admin_listings")
    )

@main.route("/reject-listing/<int:id>")
@login_required
def reject_listing(id):
    if not current_user.is_admin:
        return "Access Denied"

    rental = RentalItem.query.get_or_404(id)

    rental.status = "rejected"

    db.session.commit()

    return redirect(
        url_for("main.admin_listings")
    )

# listing for specific users like what they are giving for rent.
@main.route("/my-listings")
@login_required
def my_listings():

    rentals = current_user.rentals

    return render_template(
        "my_listings.html",
        rentals=rentals
    )

@main.route("/delete-listing/<int:id>")
@login_required
def delete_listing(id):

    rental = RentalItem.query.get_or_404(id)

    if rental.user_id != current_user.id:
        return "Access Denied"

    db.session.delete(rental)
    db.session.commit()

    return redirect(
        url_for("main.my_listings")
    )

@main.route("/edit-listing/<int:id>",methods=["GET", "POST"])
@login_required
def edit_listing(id):

    rental = RentalItem.query.get_or_404(id)

    if rental.user_id != current_user.id:
        return "Access Denied"

    if request.method == "POST":

        rental.title = request.form.get("title")

        rental.description = request.form.get(
            "description"
        )

        rental.price_per_day = request.form.get(
            "price"
        )

        rental.category = request.form.get(
            "category"
        )

        db.session.commit()

        return redirect(
            url_for("main.my_listings")
        )

    return render_template(
        "edit_listing.html",
        rental=rental
    )