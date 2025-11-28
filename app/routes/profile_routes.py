# app/routes/profile_routes.py
from flask import Blueprint, render_template, redirect, url_for, session

profile_bp = Blueprint("profile", __name__, url_prefix="/profile")


@profile_bp.route("/")
def profile():
    # Alleen toegankelijk als je ingelogd bent
    if "user_email" not in session:
        return redirect(url_for("auth.login"))

    # Basisgegevens uit de sessie (fallback naar dummy waarden)
    name = session.get("user_name", "Jan Modaal")
    email = session.get("user_email", "jan.modaal@email.com")
    phone = session.get("user_phone", "+32 495 12 34 56")
    address = session.get("user_address", "Kerkstraat 42, 9000 Gent, België")

    # Initialen voor de avatar (max 2 letters, vb. 'JM')
    parts = name.split()
    initials = ""
    for part in parts[:2]:
        if part:
            initials += part[0].upper()
    if not initials:
        initials = "JM"

    return render_template(
        "profile.html",
        name=name,
        email=email,
        phone=phone,
        address=address,
        initials=initials,
    )