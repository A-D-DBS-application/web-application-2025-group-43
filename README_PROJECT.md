# Capenta - Plant Monitoring Flask Application

A structured Flask application for monitoring and managing plant growth in gardens with sensor data analysis and plant recommendations.

## 📋 Assignment Documentation

### Project Resources
- **UI Prototype**: https://www.figma.com/make/F485MUBTo7iPmAxZP5K8IE/Dark-Mode-Garden-Robot-UI--Copy-?t=mpQSq4EU5akJkubI-1

Screenshots can be find in the folder 'UI prototype'

--------------------------------

Presentation + Demo: https://ugentbe-my.sharepoint.com/:p:/g/personal/marthe_fruyt_ugent_be/IQA6VEFsIFcCS4RlA7MSO2uwATNtkp72NzY3WUnHaufySXQ?e=cZFgUs
### Feedback Sessions
#### Audio/Video Recordings with Partner (Please Click on the link and download)
- **Session 1**: https://1drv.ms/v/c/ab63c4fd72dee8ef/IQBgn0CorPyxS58X28CgcdtGAYq4jb-BkcTRxufID3lEtlc?e=l1rPpO
- **Session 2**: (https://1drv.ms/v/c/ab63c4fd72dee8ef/IQDpmWv6lFd0T7pi0eFq_qGBAbNu5xnGcsMPgraputt4H_g?e=hocPfH)

---

## Database

The models (ERD & DDL) and database dump can be found in the 'db' folder

---

## 📁 Project Structure

```
/
├── app/                           # Flask application package
│   ├── __init__.py               # Flask app factory
│   ├── config.py                 # Configuration settings
│   ├── models.py                 # Database models (User, Garden, PlantProfile, etc.)
│   ├── routes/                   # API routes
│   │   ├── __init__.py
│   │   ├── auth_routes.py        # Authentication (login, register, logout)
│   │   ├── garden_routes.py      # Garden management
│   │   ├── playfield_routes.py   # Playfield/robotzone management
│   │   ├── dashboard_routes.py   # Dashboard, sensors, health scores, plant recommendations
│   │   ├── profile_routes.py     # User profile
│   │   └── dashboard_routes.py   # Plant recommendations & health scoring
│   ├── static/                   # Frontend assets
│   │   ├── img/                  # Images
│   │   ├── js/                   # JavaScript
│   │   └── styles/               # CSS
│   ├── templates/                # Jinja2 HTML templates
│   │   ├── dashboard.html        # Main dashboard with plant recommendations
│   │   ├── sensor_detail.html    # Sensor detail pages
│   │   └── ...other templates
│   └── scripts/                  # Utility scripts
│       ├── __init__.py
│       ├── create_health_score_table.py     # Database setup
│       ├── generate_sample_data.py          # Test data generation
│       ├── generate_health_scores.py        # Health score calculation
│       ├── setup_test_environment.py        # Test environment setup
│       └── test_plant_recommendation.py     # Recommendation verification
│
├── migrations/                   # Database migrations
│   └── add_health_score_table.sql
│
├── docs/                         # Documentation
│   ├── HEALTH_SCORE_IMPLEMENTATION.md    # Health score documentation
│   └── HEALTH_TREND_FEATURE.md           # Trend feature documentation
│
├── run.py                        # Application entry point
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- PostgreSQL (Supabase database)
- pip package manager
- Git

### Step 1: Clone the Repository
```bash
git clone <repo-url>
cd web-application-2025-group-43
```

### Step 2: Create Virtual Environment
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run the Application
```bash
python run.py
```

The application will start at `http://localhost:5000`

---

## 🎯 Usage Guide

### About Demo Data
Since this application relies on physical sensors to collect plant data, newly created accounts will not have any sensor measurements or data to display. To see the full functionality of the application, including health scores, trends, and plant recommendations, you can log in with our **demo user account**.

**Demo User Login Credentials:**
- **Email**: demo2@capenta.com

The demo account includes sample gardens, playfields, and sensor data so you can explore all features of the application.

### User Authentication
1. Navigate to the login page at `http://localhost:5000/`
2. **New users**: Click "Register" to create an account (note: your account will not have sensor data until physical sensors are configured)
3. **Demo users**: Use the demo credentials above to see the application with sample data

### Creating a Garden
1. After login, click "Add Garden"
2. Enter garden name, address (optional), and area (optional)
3. Click "Save" to create the garden

### Adding a Playfield (Robot Zone)
1. Select your garden from the garden selection screen
2. Click "Add Playfield"
3. Enter playfield name and select a plant type
4. Click "Save"

### Viewing Dashboard
1. Select a garden
2. Select a playfield
3. The dashboard displays:
   - **Health Score**: Overall plant health (0-100%)
   - **Health Factors**: Individual sensor readings
   - **Trend Chart**: Health trend over selected period (7d, 30d, 90d, 1y)
   - **Plant Recommendations**: Top 3 recommended plants for current conditions
   - **Alerts**: Conditions outside optimal range

### Viewing Sensor Details
1. Click on any health factor on the dashboard
2. View sensor readings history
3. See current sensor value and status

### Selecting Time Periods
- Click period buttons (7d, 30d, 3m, 1y) on trend chart to change timeframe
- Trend percentage shows change compared to previous period

---

## 📊 Features

### 1. **Plant Health Scoring**
- Automatic daily health scores (0-100%)
- Based on 6 sensor types: moisture, temperature, humidity, rainfall, light, CO₂
- Compares real-time measurements against plant profile optimal values
- Quadratic penalty formula for accurate assessment

### 2. **Plant Recommendations**
- Intelligent plant recommendations based on current environmental conditions
- Analyzes 5-day average of all sensors
- Evaluates all 10 available plants
- Displays top 3 recommendations on dashboard with visual score bars

### 3. **Health Trend Analysis**
- Visualize health trends over time periods (7d, 30d, 3m, 1y)
- Dynamic trend calculation (% change vs. previous period)
- Interactive Chart.js graphs
- Real-time API updates without page refresh

### 4. **Sensor Management**
- Clickable sensor cards on dashboard
- Detailed sensor history
- Real-time sensor value display
- Status indicators (OK, Warning, Critical)

### 5. **Multi-User Gardens**
- User authentication & authorization
- Multiple gardens per user
- Multiple playfields per garden
- Role-based access control


**10 Available Plants**:
1. Tomato
2. Zuccini
3. Lettuce
4. Beans
5. Strawberry
6. Carrot
7. Leek
8. Onion/shallot
9. Paprika/pepper
10. Pumpkin


## 📝 Database Models

- **User**: User accounts
- **Garden**: User's gardens
- **RobotZone**: Playfields in gardens
- **Sensor**: Sensor definitions
- **Measurement**: Sensor readings
- **PlantProfile**: Plant optimal values (10 plants)
- **HealthScore**: Daily health scores

## 🐛 Troubleshooting

### New Account Has No Data
- This is normal! Newly created accounts have no sensor measurements because we don't have physical sensors connected
- Use the demo account to see sample data and test all features
- When physical sensors are integrated, new measurements will automatically appear

### Health Score Shows 0%
- Ensure playfield has a PlantProfile assigned
- Check that sensor measurements exist
- Verify PlantProfile has mean/std values

### No Plant Recommendations
- Playfield needs measurements from last 5 days
- Plant profile must be assigned to playfield
- All 6 sensor types must have data

### Dashboard Not Loading
- Check browser console for errors
- Verify user is logged in
- Ensure playfield serial_number is valid

---


