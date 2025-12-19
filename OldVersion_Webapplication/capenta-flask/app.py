from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from datetime import timedelta
import os
import sys
import pandas as pd
import plotly.graph_objects as go

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-change-me")
app.permanent_session_lifetime = timedelta(hours=6)

# -----------------------
# Session helpers
# -----------------------

def ensure_session_state():
    if "logged_in" not in session:
        session["logged_in"] = False
    session.setdefault("username", "Guest")
    session.setdefault("theme", "dark")  # "dark" of "light"
    session.setdefault("plant_data", [])
    session.setdefault("weed_data", [])
    session.setdefault("sensor_data", [])

@app.context_processor
def inject_theme():
    return {"theme": session.get("theme", "dark")}

# -----------------------
# Plot builders (dark-aware)
# -----------------------

def _plot_colors(is_dark: bool):
    if is_dark:
        return {"paper":"#0b1020","plot":"#0f1530","grid":"#2a3357","axis":"#b8c1ff"}
    return {"paper":"#ffffff","plot":"#ffffff","grid":"#e5e7eb","axis":"#111827"}

def build_garden_figure(plant_data, weed_data, is_dark: bool):
    C = _plot_colors(is_dark)
    fig = go.Figure()

    # Mooie assen + grid
    fig.update_xaxes(range=[0,1000], dtick=100, gridcolor=C["grid"], zeroline=True, zerolinewidth=1, showline=True, linecolor=C["grid"])
    fig.update_yaxes(range=[0,1000], dtick=100, gridcolor=C["grid"], scaleanchor="x", scaleratio=1, showline=True, linecolor=C["grid"])

    # Planten (verschillende marker-symbolen op exact XY)
    if plant_data:
        df = pd.DataFrame(plant_data)
        if set(["x","y"]).issubset(df.columns):
            # zachte highlightring
            fig.add_trace(go.Scatter(
                x=df["x"], y=df["y"], mode="markers",
                marker=dict(size=18, color="rgba(34,197,94,0.15)", line=dict(width=0)),
                hoverinfo="skip", showlegend=False
            ))
            # echte markers
            symbols = ["circle","square","diamond","triangle-up","hexagram"]
            colors  = ["#86efac","#a7f3d0","#bef264","#93c5fd","#fca5a5"]
            texts = []
            for _,r in df.iterrows():
                t = r.get("type","Plant")
                texts.append(f"{t}<br>x:{float(r.get('x',0)):.0f}mm, y:{float(r.get('y',0)):.0f}mm")
            fig.add_trace(go.Scatter(
                x=df["x"], y=df["y"], mode="markers+text",
                marker=dict(
                    size=10,
                    color=[colors[i % len(colors)] for i in range(len(df))],
                    symbol=[symbols[i % len(symbols)] for i in range(len(df))],
                    line=dict(color="rgba(0,0,0,0.35)" if not is_dark else "rgba(255,255,255,0.25)", width=1)
                ),
                textposition="top center",
                hovertemplate="%{text}",
                text=[p.get("type","Plant") for p in plant_data],
                showlegend=False
            ))

    # Weeds (duidelijke rode X)
    if weed_data:
        wdf = pd.DataFrame(weed_data)
        if set(["x","y"]).issubset(wdf.columns):
            fig.add_trace(go.Scatter(
                x=wdf["x"], y=wdf["y"], mode="markers",
                name="Weeds",
                marker=dict(size=10, color="#ef4444", symbol="x", line=dict(color="#ef4444", width=2)),
                hovertemplate="Weed<br>x:%{x:.0f}mm y:%{y:.0f}mm<extra></extra>"
            ))

    fig.update_layout(
        title="Garden Bed (1000mm × 1000mm)",
        paper_bgcolor=C["paper"],
        plot_bgcolor=C["plot"],
        font=dict(color=C["axis"]),
        margin=dict(l=20,r=20,t=50,b=20),
        width=520, height=520,
        legend=dict(bgcolor="rgba(0,0,0,0)"),
    )
    return fig.to_html(full_html=False, include_plotlyjs='cdn')


def build_sensor_figure(sensor_data, is_dark: bool):
    if not sensor_data:
        return None
    C = _plot_colors(is_dark)
    df = pd.DataFrame(sensor_data)
    fig = go.Figure()

    def add(name, color):
        cols = set(df.columns)
        if {"Timestamp",name}.issubset(cols):
            fig.add_trace(go.Scatter(x=df["Timestamp"], y=df[name], mode="lines", name=name, line=dict(width=2)))

    add("Air Temp (°C)",   "#f87171")
    add("Soil Temp (°C)",  "#fb923c")
    add("Soil Moisture (%)","#60a5fa")
    add("Humidity (%)",    "#a78bfa")
    add("Light (Lux)",     "#facc15")
    add("Soil pH",         "#34d399")

    fig.update_layout(
        title="Sensor Data Over Time",
        xaxis_title="Time",
        yaxis_title="Value",
        hovermode="x unified",
        paper_bgcolor=C["paper"],
        plot_bgcolor=C["plot"],
        font=dict(color=C["axis"]),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=30,r=20,t=60,b=40),
        height=360
    )
    fig.update_xaxes(gridcolor=C["grid"], linecolor=C["grid"])
    fig.update_yaxes(gridcolor=C["grid"], linecolor=C["grid"])
    return fig.to_html(full_html=False, include_plotlyjs='cdn')


def compute_alerts(sensor_data):
    if not sensor_data:
        return []
    latest = pd.DataFrame(sensor_data).iloc[-1]
    alerts = []
    try:
        if float(latest.get("Soil Moisture (%)", 100)) < 30:
            alerts.append("⚠️ Low soil moisture – initiate watering!")
        air = float(latest.get("Air Temp (°C)", 20))
        if air > 30 or air < 10:
            alerts.append("⚠️ Air temperature out of optimal range (10–30°C).")
        ph = float(latest.get("Soil pH", 6.5))
        if ph < 6 or ph > 7:
            alerts.append("⚠️ Soil pH imbalance – consider amendments.")
        lux = float(latest.get("Light (Lux)", 500))
        if lux < 300:
            alerts.append("⚠️ Low light levels – check for shading.")
    except Exception:
        pass
    return alerts

# -----------------------
# Routes
# -----------------------

@app.route("/", methods=["GET","POST"])
def login():
    ensure_session_state()
    if request.method == "POST":
        username = request.form.get("username","").strip() or "Guest"
        password = request.form.get("password","")
        if password == "Flexers123!":
            session["logged_in"] = True
            session["username"] = username
            return redirect(url_for("dashboard"))
        flash("Incorrect password. Please try again.", "error")
    if session.get("logged_in"):
        return redirect(url_for("dashboard"))
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/set_theme", methods=["POST"])
def set_theme():
    ensure_session_state()
    mode = (request.json or {}).get("mode","dark")
    if mode not in ("dark","light"):
        return jsonify({"status":"error","message":"invalid mode"}), 400
    session["theme"] = mode
    return jsonify({"status":"ok","theme":mode})

@app.route("/dashboard")
def dashboard():
    ensure_session_state()
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    is_dark = (session.get("theme","dark") == "dark")
    garden = build_garden_figure(session["plant_data"], session["weed_data"], is_dark)
    sensor = build_sensor_figure(session["sensor_data"], is_dark)
    alerts = compute_alerts(session["sensor_data"])
    weeds_recent = session["weed_data"][-5:] if session["weed_data"] else []
    return render_template("dashboard.html",
                           garden_fig=garden,
                           sensor_fig=sensor,
                           alerts=alerts,
                           weeds=weeds_recent,
                           username=session.get("username","Guest"))

@app.route("/api/mock_seed", methods=["POST"])
def api_mock_seed():
    ensure_session_state()
    session["plant_data"] = [
        {"type": "Tomato", "x": 120, "y": 180},
        {"type": "Lettuce","x": 340, "y": 260},
        {"type": "Carrot", "x": 520, "y": 420},
        {"type": "Basil",  "x": 700, "y": 640},
        {"type": "Spinach","x": 860, "y": 780},
    ]
    session["weed_data"] = [
        {"timestamp":"2025-11-01 10:05:00","x":150,"y":220,"area":210},
        {"timestamp":"2025-11-02 11:20:00","x":260,"y":360,"area":190},
        {"timestamp":"2025-11-03 09:45:00","x":480,"y":500,"area":230},
        {"timestamp":"2025-11-04 12:10:00","x":720,"y":660,"area":175},
        {"timestamp":"2025-11-05 15:30:00","x":900,"y":820,"area":205},
    ]
    sensor_rows=[]
    for i in range(100):
        sensor_rows.append({
            "Timestamp": f"2025-11-01 12:{i:02d}:00",
            "Air Temp (°C)": 15 + (i % 10) * 0.8,
            "Soil Temp (°C)": 14 + (i % 10) * 0.5,
            "Soil Moisture (%)": 25 + (i % 20),
            "Humidity (%)": 40 + (i % 30),
            "Light (Lux)": 200 + (i % 100) * 5,
            "Soil pH": 6.2 + ((i % 5) * 0.15)
        })
    session["sensor_data"] = sensor_rows
    return jsonify({"status":"ok","message":"Seed data inserted."})

# -----------------------
# Entry
# -----------------------

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else int(os.getenv("PORT","5000"))
    app.run(host="127.0.0.1", port=port, debug=True)
