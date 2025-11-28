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

        # User zoeken
        user = User.query.filter_by(uemail=email).first()

        if not user:
            flash("Geen account gevonden met dit e-mailadres.", "error")
            return render_template("login.html")

        # Login ok -> sessie vullen
        session["user_email"] = user.uemail
        session["user_name"] = user.uname

        # Doorsturen naar garden selection (volgende pagina)
        # LET OP: dit werkt alleen als je een blueprint 'garden'
        # met endpoint 'garden_selection' hebt geregistreerd.
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
        username = request.form.get("username")
        phone = request.form.get("phone")
        adress = request.form.get("adress")
        password = request.form.get("password")

        # Basisvalidatie
        if not email or not username or not password:
            flash("Email, username en password zijn verplicht.", "error")
            return render_template("register.html")

        # Bestaat user al?
        existing = User.query.filter_by(uemail=email).first()
        if existing:
            flash("Er bestaat al een account met dit e-mailadres.", "error")
            return render_template("register.html")

        # Nieuwe gebruiker opslaan
        new_user = User(
            uemail=email,
            uname=username,
            phone=phone,
            adress=adress,
            password=password   # Voor MVP oké → later hashing toevoegen
        )

        db.session.add(new_user)
        db.session.commit()

        flash("Account succesvol aangemaakt! Log nu in.", "success")

        # 🔥 TERUG NAAR LOGIN NA REGISTRATIE
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

