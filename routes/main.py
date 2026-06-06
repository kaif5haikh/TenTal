from flask import Blueprint, render_template

main = Blueprint("main", __name__)


@main.route("/")
def home():
    return render_template("index.html")


@main.route("/browse")
def browse():
    return render_template("browse.html")