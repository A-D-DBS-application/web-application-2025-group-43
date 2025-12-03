from flask import Blueprint, render_template, redirect, url_for, session, flash
from ..models import User

profile_bp = Blueprint("profile", __name__, url_prefix="/profile")


@profile_bp.route("/")
def profile():
    # Enkel toegankelijk indien ingelogd
    user_email = session.get("user_email")
    if not user_email:
        flash("You must be logged in.", "error")
        return redirect(url_for("auth.login"))

    # User ophalen uit database
    user = User.query.filter_by(uemail=user_email).first()
    if not user:
        flash("User not found in database.", "error")
        return redirect(url_for("auth.login"))

    # Initialen uit naam (max 2 letters)
    parts = user.uname.split() if user.uname else []
    initials = ""
    for part in parts[:2]:
        if part:
            initials += part[0].upper()
    if not initials:
        initials = "US"

    return render_template(
        "profile.html",
        name=user.uname,
        email=user.uemail,
        phone=user.phone,
        address=user.adress,
        initials=initials,
    )
