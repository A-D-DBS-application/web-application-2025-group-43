from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from ..models import Garden
from .. import db
import uuid

garden_bp = Blueprint("garden", __name__, url_prefix="/garden")


# -------------------------------------------
# Helper: enkel toegankelijk als je ingelogd bent
# -------------------------------------------
def require_login():
    if "user_email" not in session:
        flash("You must be logged in.", "error")
        return redirect(url_for("auth.login"))
    return None


# -------------------------------------------
# 1. Garden selection pagina
#    URL: /garden/select
# -------------------------------------------
@garden_bp.route("/select")
def garden_selection():
    check = require_login()
    if check:
        return check

    user_email = session["user_email"]
    gardens = Garden.query.filter_by(user_email=user_email).all()

    return render_template("garden_selection.html", gardens=gardens)


# -------------------------------------------
# 2. Add Garden pagina
#    URL: /garden/add
# -------------------------------------------
@garden_bp.route("/add", methods=["GET", "POST"])
def add_garden():
    check = require_login()
    if check:
        return check

    if request.method == "POST":
        name = request.form.get("garden_name")
        address = request.form.get("address")
        size = request.form.get("size")  # bv. 120

        # simpele validatie
        if not name:
            flash("Garden name is required.", "error")
            return render_template("add_garden.html")

        # size omzetten naar getal (mag leeg zijn)
        size_value = None
        if size:
            try:
                size_value = float(size)
            except ValueError:
                flash("Size must be a number.", "error")
                return render_template("add_garden.html")

        new_garden = Garden(
            garden_id=uuid.uuid4(),
            garden_name=name,
            adress_garden=address,
            area_garden=size_value,
            user_email=session["user_email"],
        )

        db.session.add(new_garden)
        db.session.commit()

        flash("Garden added!", "success")
        # terug naar de Select Your Garden–pagina
        return redirect(url_for("garden.garden_selection"))

    # GET → toon formulier
    return render_template("add_garden.html")


# -------------------------------------------
# 3. Garden aanklikken → volgende pagina
#    URL: /garden/<garden_id>
# -------------------------------------------
@garden_bp.route("/<uuid:garden_id>")
def enter_garden(garden_id):
    check = require_login()
    if check:
        return check

    garden = Garden.query.filter_by(garden_id=garden_id).first()

    if not garden:
        flash("Garden not found.", "error")
        return redirect(url_for("garden.garden_selection"))

    # Voor nu: placeholder – later playfields pagina
    # bv. redirect naar playfield blueprint
    # return redirect(url_for("playfield.playfield_selection", garden_id=garden_id))

    return f"You clicked on garden: {garden.garden_name}"
