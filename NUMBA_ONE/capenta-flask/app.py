from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from datetime import timedelta
import os, sys
import pandas as pd
import plotly.graph_objects as go

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-change-me")
app.permanent_session_lifetime = timedelta(hours=6)

def ensure_session_state():
    if "logged_in" not in session: session["logged_in"] = False
    session.setdefault("plant_data", [])
    session.setdefault("weed_data", [])
    session.setdefault("sensor_data", [])

def build_garden_figure(plant_data, weed_data):
    fig = go.Figure()
    fig.update_layout(title="Garden Bed (1000mm x 1000mm)", width=300, height=300)
    return fig.to_html(full_html=False, include_plotlyjs='cdn')

def build_sensor_figure(sensor_data):
    if not sensor_data: return None
    df = pd.DataFrame(sensor_data)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['Timestamp'], y=df['Air Temp (°C)'], mode='lines', name='Air Temp (°C)'))
    return fig.to_html(full_html=False, include_plotlyjs='cdn')

def compute_alerts(sensor_data):
    if not sensor_data: return []
    latest = pd.DataFrame(sensor_data).iloc[-1]
    alerts=[]
    if latest.get('Soil Moisture (%)', 40) < 30: alerts.append("⚠️ Low soil moisture – initiate watering!")
    return alerts

@app.route("/", methods=["GET","POST"])
def login():
    ensure_session_state()
    if request.method=="POST":
        if request.form.get("password")=="Flexers123!":
            session["logged_in"]=True
            session["username"]=request.form.get("username") or "Guest"
            return redirect(url_for("dashboard"))
        flash("Incorrect password. Please try again.","error")
    if session.get("logged_in"):
        return redirect(url_for("dashboard"))
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    ensure_session_state()
    if not session.get("logged_in"): return redirect(url_for("login"))
    garden_fig=build_garden_figure(session["plant_data"],session["weed_data"])
    sensor_fig=build_sensor_figure(session["sensor_data"])
    alerts=compute_alerts(session["sensor_data"])
    return render_template("dashboard.html",
        username=session.get("username","Guest"),
        garden_fig=garden_fig,
        sensor_fig=sensor_fig,
        alerts=alerts,
        weeds=session["weed_data"][-5:])

@app.route("/api/mock_seed",methods=["POST"])
def api_mock_seed():
    ensure_session_state()
    session["plant_data"]=[{"type":"Tomato","x":150,"y":200}]
    session["sensor_data"]=[{"Timestamp":"now","Air Temp (°C)":22}]
    session["weed_data"]=[{"timestamp":"now","x":100,"y":150,"area":200}]
    return jsonify({"status":"ok","message":"Seed data inserted."})

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else int(os.getenv("PORT", "5000"))
    app.run(host="127.0.0.1", port=port, debug=True)
