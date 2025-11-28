from flask import Blueprint, render_template, request, redirect, url_for

main = Blueprint("main", __name__)

# --------------------------
# 1. LOGIN PAGE (GET)
# --------------------------
@main.route("/", methods=["GET"])
def login_page():
    return render_template("login.html")


# --------------------------
# 2. LOGIN SUBMIT (POST)
# --------------------------
@main.route("/login", methods=["POST"])
def login():
    email = request.form.get("email")

    # TODO: Replace with real DB authentication later
    if email:
        return redirect(url_for("main.garden_selection"))

    return redirect(url_for("main.login_page"))


# --------------------------
# 3. GARDEN SELECTION PAGE
# --------------------------
@main.route("/gardens", methods=["GET"])
def garden_selection():

    # Static demo data until database is plugged in
    main_garden = {
        "id": 1,
        "name": "Hoftuin Oost",
        "address": "Kerkstraat 42, 9000 Gent, België",
        "playfields": 6,
        "status": "Online",
        "image": "https://images.unsplash.com/photo-1667193426133-f940c155457a?auto=format&fit=crop&w=1000&q=80"
    }

    other_gardens = [
        {
            "id": 2,
            "name": "Stadsboerderij Zuid",
            "address": "Leopoldstraat 15, 2000 Antwerpen",
            "playfields": 4,
            "status": "Online",
            "image": "https://images.unsplash.com/photo-1728706613022-55c1d7559f21?auto=format&fit=crop&w=1000&q=80"
        },
        {
            "id": 3,
            "name": "Volkstuin Park",
            "address": "Parkweg 88, 3000 Leuven",
            "playfields": 8,
            "status": "Offline",
            "image": "https://images.unsplash.com/photo-1738669313657-07ebf0f23d15?auto=format&fit=crop&w=1000&q=80"
        },
        {
            "id": 4,
            "name": "Groene Oase",
            "address": "Tuinlaan 7, 8000 Brugge",
            "playfields": 5,
            "status": "Online",
            "image": "https://images.unsplash.com/photo-1661926272970-728f0d6389fd?auto=format&fit=crop&w=1000&q=80"
        },
    ]

    return render_template(
        "garden_selection.html",
        main_garden=main_garden,
        other_gardens=other_gardens,
    )


# --------------------------
# 4. DASHBOARD PLACEHOLDER
# --------------------------
@main.route("/dashboard/<int:garden_id>")
def dashboard(garden_id):
    return f"Dashboard for garden {garden_id}"