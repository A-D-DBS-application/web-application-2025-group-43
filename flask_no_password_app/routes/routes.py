from flask import render_template, request, redirect, url_for
from app import app

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Hier kan je later echte loginlogica zetten
        email = request.form.get("email")
        # Voor nu: altijd naar garden selection
        return redirect(url_for("garden_selection"))
    return render_template("login.html")


@app.route("/gardens")
def garden_selection():
    return render_template("garden_selection.html")


@app.route("/playfields/<garden_id>")
def playfield_selection(garden_id):
    return render_template("playfield_selection.html", garden_id=garden_id)


@app.route("/dashboard/<playfield_id>")
def dashboard(playfield_id):
    return render_template("dashboard.html", playfield_id=playfield_id)