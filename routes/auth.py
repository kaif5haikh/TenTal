from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for
)
from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from models.user import User
from extensions import db
from flask_login import login_user
from flask_login import logout_user

auth = Blueprint("auth", __name__)

@auth.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(
            email=email
        ).first()

        if user and check_password_hash(user.password,password):
            if not user.is_active_user:
                return "Account Disabled"
            login_user(user)
            return redirect(url_for("main.home"))

        return "Invalid Email or Password"

    return render_template("login.html")

@auth.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get("name")
        email = request.form.get("email")
        existing_user = User.query.filter_by(
            email=email
        ).first()

        if existing_user:
            return "Email already registered"

        password = generate_password_hash(
            request.form.get("password")
        )
        user = User(
            name=name,
            email=email,
            password=password
        )

        db.session.add(user)
        db.session.commit()

        return redirect(url_for("auth.login"))

    return render_template("register.html")

@auth.route("/logout")
def logout():

    logout_user()

    return redirect(url_for("main.home"))