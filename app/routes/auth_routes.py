# app/routes/auth_routes.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from ..models import User
from .. import db

auth_bp = Blueprint("auth", __name__)


# ===========================================
# HOME -> redirect naar login
# ===========================================
@auth_bp.route("/")
def index():
    return redirect(url_for("auth.login"))


# ===========================================
# LOGIN
# ===========================================
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")

        # Geen / lege email
        if not email:
            flash("Please enter a valid email address.", "login-error")
            return render_template("login.html")

        # User zoeken in DB
        user = User.query.filter_by(uemail=email).first()

        # Geen user gevonden -> foutmelding
        if not user:
            flash(
                "We couldn’t find an account with that email address. "
                "Please create an account first.",
                "login-error",
            )
            return render_template("login.html")

        # Login ok -> sessie vullen
        session["user_email"] = user.uemail
        session["user_name"] = user.uname

        # Doorsturen naar garden selection
        return redirect(url_for("garden.garden_selection"))

    # GET: loginpagina tonen (zonder foutmeldingen)
    return render_template("login.html")


# ===========================================
# REGISTER
# ===========================================
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        name = request.form.get("name")
        phone = request.form.get("phone")
        adress = request.form.get("adress")
        password = request.form.get("password")

        # Basisvalidatie
        if not email or not name or not password:
            flash("Email, name and password are required.", "error")
            return render_template("register.html")

        # Bestaat user al?
        existing = User.query.filter_by(uemail=email).first()
        if existing:
            flash("An account with this email address already exists.", "error")
            return render_template("register.html")

        # Nieuwe gebruiker opslaan
        new_user = User(
            uemail=email,
            uname=name,
            phone=phone,
            adress=adress,
            password=password,  # later kan je hier hashing aan toevoegen
        )

        db.session.add(new_user)
        db.session.commit()

        # Succesboodschap (wordt NIET getoond op login, zie template-filter)
        flash("Account created successfully! Please log in.", "success")
        return redirect(url_for("auth.login"))

    # GET: registerpagina tonen
    return render_template("register.html")


# ===========================================
# LOGOUT
# ===========================================
@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
