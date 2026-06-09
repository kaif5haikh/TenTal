from flask import Blueprint, render_template
from flask_login import current_user
from models.rental_item import RentalItem
from extensions import db
from flask import request, redirect, url_for
from flask_login import login_required
import os
from werkzeug.utils import secure_filename
from flask import current_app
from models.user import User
from models.booking import Booking
from datetime import datetime, date, timedelta
from flask import flash


BUFFER_DAYS = 1
def dates_overlap(
    start_date,
    end_date,
    booking_start,
    booking_end
):
    return (
        start_date <= booking_end + timedelta(days=BUFFER_DAYS)
        and
        end_date >= booking_start
    )

def update_booking_status(booking):

    today = date.today()

    if booking.status == "cancelled":
        return

    if booking.start_date <= today <= booking.end_date:
        booking.status = "active"

    elif today > booking.end_date:
        booking.status = "completed"

main = Blueprint("main", __name__)


@main.route("/")
def home():
    return render_template("index.html")


@main.route("/browse")
def browse():

    search = request.args.get(
        "search",
        ""
    )
    category = request.args.get(
        "category",
        ""
    )

    rentals = RentalItem.query.filter_by(
        status="approved"
    ).all()

    rentals = [
        rental for rental in rentals
        if rental.owner.is_active_user
    ]

    if search:

        rentals = [
            rental
            for rental in rentals
            if search.lower()
            in rental.title.lower()
        ]
    if category:

        rentals = [
            rental
            for rental in rentals
            if rental.category == category
        ]

    return render_template(
        "browse.html",
        rentals=rentals,
        selected_category=category
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
        quantity = int(request.form["quantity"])
        security_deposit = float(
            request.form["security_deposit"]
        )

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
            quantity=quantity,
            security_deposit=security_deposit,
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

@main.route("/admin/listing/<int:id>")
@login_required
def admin_listing_detail(id):

    if not current_user.is_admin:
        return "Access Denied"

    rental = RentalItem.query.get_or_404(id)

    return render_template(
        "admin_listing_detail.html",
        rental=rental
    )

@main.route("/admin/dashboard")
@login_required
def admin_dashboard():

    if not current_user.is_admin:
        return "Access Denied"

    total_users = User.query.count()

    total_listings = RentalItem.query.count()

    pending_listings = RentalItem.query.filter_by(
        status="pending"
    ).count()

    approved_listings = RentalItem.query.filter_by(
        status="approved"
    ).count()

    rejected_listings = RentalItem.query.filter_by(
        status="rejected"
    ).count()

    recent_listings = RentalItem.query.order_by(
        RentalItem.id.desc()
    ).limit(5).all()

    return render_template(
        "admin_dashboard.html",
        total_users=total_users,
        total_listings=total_listings,
        pending_listings=pending_listings,
        approved_listings=approved_listings,
        rejected_listings=rejected_listings,
        recent_listings=recent_listings
    )

@main.route("/admin/users")
@login_required
def admin_users():

    if not current_user.is_admin:
        return "Access Denied"

    users = User.query.all()

    return render_template(
        "admin_users.html",
        users=users
    )

# check listing of users in usermanagement page
@main.route("/admin/user/<int:id>")
@login_required
def user_listings(id):

    if not current_user.is_admin:
        return "Access Denied"

    user = User.query.get_or_404(id)

    return render_template(
        "user_listings.html",
        user=user
    )

# Enable and disable account of users using
@main.route("/admin/disable-user/<int:id>")
@login_required
def disable_user(id):

    if not current_user.is_admin:
        return "Access Denied"

    user = User.query.get_or_404(id)

    user.is_active_user = False

    db.session.commit()

    return redirect(
        url_for("main.admin_users")
    )

@main.route("/admin/enable-user/<int:id>")
@login_required
def enable_user(id):

    if not current_user.is_admin:
        return "Access Denied"

    user = User.query.get_or_404(id)

    user.is_active_user = True

    db.session.commit()

    return redirect(
        url_for("main.admin_users")
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

@main.route(
    "/booking/request/<int:id>",
    methods=["POST"]
)
@login_required
def request_booking(id):

    rental = RentalItem.query.get_or_404(id)
    quantity_booked = int(
        request.form["quantity_booked"]
    )
    if rental.user_id == current_user.id:
        return "You cannot book your own listing"
    
    if quantity_booked > rental.quantity:
        return "Requested quantity exceeds total stock"
    
    if quantity_booked < 1:
        return "Invalid quantity"

    start_date = datetime.strptime(
        request.form.get("start_date"),
        "%Y-%m-%d"
    ).date()

    end_date = datetime.strptime(
        request.form.get("end_date"),
        "%Y-%m-%d"
    ).date()

    if start_date < date.today():
        return "Cannot book past dates"

    if end_date <= start_date:
        return "End date must be after start date"

    days = (end_date - start_date).days

    total_price = (
        days *
        rental.price_per_day *
        quantity_booked
    )
    grand_total = (
        total_price +
        rental.security_deposit
    )
    booked_quantity = 0

    for booking in rental.bookings:
        if booking.status != "approved":
            continue
        overlap = dates_overlap(
            start_date,
            end_date,
            booking.start_date,
            booking.end_date
        )
        print(
            "Booking:",
            booking.start_date,
            booking.end_date,
            "Overlap:",
            overlap
        )
        
        if overlap:
            booked_quantity += booking.quantity_booked

    available_quantity = (
        rental.quantity -
        booked_quantity
        )
    
    available_quantity = max(
        0,
        available_quantity
    )
    
    if quantity_booked > available_quantity:
        return f"Only {available_quantity} item(s) available for selected dates"

    booking = Booking(
        user_id=current_user.id,
        rental_item_id=rental.id,
        start_date=start_date,
        end_date=end_date,
        total_price=total_price,
        security_deposit=rental.security_deposit,
        quantity_booked=quantity_booked,
        status="approved"
    )

    db.session.add(booking)
    db.session.commit()
    flash(
        "Booking confirmed successfully!",
        "success"
    )
    return redirect(
        url_for(
            "main.listing_detail",
            id=rental.id
        )
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

    has_booking = any(
        booking.status != "cancelled"
        for booking in rental.bookings
    )

    if has_booking:
        return "Cannot delete listing because bookings exist"

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
        rental.security_deposit = float(
            request.form["security_deposit"]
        )

        rental.quantity = int(
            request.form["quantity"]
        )
        db.session.commit()

        return redirect(
            url_for("main.my_listings")
        )

    return render_template(
        "edit_listing.html",
        rental=rental
    )

@main.route("/my-bookings")
@login_required
def my_bookings():

    bookings = Booking.query.filter_by(
        user_id=current_user.id
    ).all()

    for booking in bookings:
        update_booking_status(
            booking
        )

    db.session.commit()

    return render_template(
        "my_bookings.html",
        bookings=bookings
    )

@main.route("/booking-requests")
@login_required
def booking_requests():

    bookings = Booking.query.join(
        Booking.rental_item
    ).filter(
        RentalItem.user_id == current_user.id
    ).order_by(
        Booking.created_at.desc()
    ).all()

    total_requests = len(bookings)

    active_count = sum(
        1 for booking in bookings
        if booking.status == "active"
    )

    completed_count = sum(
        1 for booking in bookings
        if booking.status == "completed"
    )

    cancelled_count = sum(
        1 for booking in bookings
        if booking.status == "cancelled"
    )

    return render_template(
        "booking_requests.html",
        bookings=bookings,
        total_requests=total_requests,
        active_count=active_count,
        completed_count=completed_count,
        cancelled_count=cancelled_count
    )


@main.route("/booking/cancel/<int:id>")
@login_required
def cancel_booking(id):

    booking = Booking.query.get_or_404(id)

    if booking.user_id != current_user.id:
        return "Access Denied"

    booking.status = "cancelled"

    db.session.commit()

    return redirect(
        url_for("main.my_bookings")
    )

@main.route("/check-availability/<int:id>")
@login_required
def check_availability(id):

    rental = RentalItem.query.get_or_404(id)
    start_date_str = request.args.get(
    "start_date"
)

    end_date_str = request.args.get(
        "end_date"
    )

    if not start_date_str or not end_date_str:
        return "Select dates first"

    start_date = datetime.strptime(
        request.args.get("start_date"),
        "%Y-%m-%d"
    ).date()

    end_date = datetime.strptime(
        request.args.get("end_date"),
        "%Y-%m-%d"
    ).date()

    booked_quantity = 0

    for booking in rental.bookings:

        if booking.status != "approved":
            continue

        overlap = dates_overlap(
            start_date,
            end_date,
            booking.start_date,
            booking.end_date
        )
        print(
            "Booking:",
            booking.start_date,
            booking.end_date,
            "Overlap:",
            overlap
        )

        if overlap:
            booked_quantity += booking.quantity_booked

    available_quantity = (
        rental.quantity -
        booked_quantity
    )

    return str(
        max(0, available_quantity)
    )

# Owner can check its listing and revnues:
@main.route("/owner-dashboard")
@login_required
def owner_dashboard():

    listings = RentalItem.query.filter_by(
        user_id=current_user.id
    ).all()

    total_listings = len(listings)

    active_rentals = 0
    completed_rentals = 0
    total_revenue = 0
    recent_bookings = []

    for listing in listings:
        recent_bookings.extend(
            listing.bookings
        )

    recent_bookings = sorted(
        recent_bookings,
        key=lambda booking: booking.created_at,
        reverse=True
    )[:5]

    for listing in listings:

        for booking in listing.bookings:

            if booking.status == "active":
                active_rentals += 1

            if booking.status == "completed":
                completed_rentals += 1
                total_revenue += booking.total_price

    return render_template(
        "owner_dashboard.html",
        total_listings=total_listings,
        active_rentals=active_rentals,
        completed_rentals=completed_rentals,
        total_revenue=total_revenue,
        recent_bookings=recent_bookings
    )