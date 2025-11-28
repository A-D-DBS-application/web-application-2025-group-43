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

        if not email:
            flash("Vul een geldig e-mailadres in.", "error")
            return render_template("login.html")

        # User zoeken in DB
        user = User.query.filter_by(uemail=email).first()

        if not user:
            flash("Geen account gevonden met dit e-mailadres.", "error")
            return render_template("login.html")

        # Login ok -> sessie vullen
        session["user_email"] = user.uemail
        session["user_name"] = user.uname

        # Doorsturen naar garden selection (volgende pagina)
        # Zorg dat je een garden blueprint hebt met endpoint 'garden_selection'
        return redirect(url_for("garden.garden_selection"))

    # GET: loginpagina tonen
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
            flash("Email, name en password zijn verplicht.", "error")
            return render_template("register.html")

        # Bestaat user al?
        existing = User.query.filter_by(uemail=email).first()
        if existing:
            flash("Er bestaat al een account met dit e-mailadres.", "error")
            return render_template("register.html")

        # Nieuwe gebruiker opslaan
        new_user = User(
            uemail=email,
            uname=name,
            phone=phone,
            adress=adress,
            password=password   # Voor MVP oké – later kan je hashing toevoegen
        )

        db.session.add(new_user)
        db.session.commit()

        flash("Account succesvol aangemaakt! Log nu in.", "success")

        # 🔥 Na 'Create Account' DIRECT terug naar login
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
