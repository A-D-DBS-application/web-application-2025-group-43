# Capenta - Plant Monitoring Flask Application

Gestructureerde Flask applicatie voor het monitoren en beheren van plantgroei in indoor gardens met sensordata analyse en plantaanbevelingen.

## 📁 Project Structuur

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

## 🚀 Aan de Slag

### Installatie

```bash
# Clone repository
git clone <repo-url>
cd web-application-2025-group-43

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Database Setup

```bash
# Create health_score table
python3 -m app.scripts.create_health_score_table

# Setup test environment with demo data
python3 -m app.scripts.setup_test_environment
```

### Run Application

```bash
python3 run.py
```

Visit http://127.0.0.1:5000

## 📊 Features

### 1. **Plant Health Scoring**
- Automatische dagelijkse gezondheidsscores (0-100%)
- Gebaseerd op 6 sensortypes: moisture, temperature, humidity, rain, light, CO₂
- Vergelijkt realtime metingen met plantprofieloptimale waarden
- Quadratische penaliteitsformule voor nauwkeurige beoordeling

### 2. **Plant Recommendations**
- Intelligente plantaanbevelingen op basis van huidige omstandigheden
- Analyseert 5-daags gemiddelde van alle sensoren
- Beoordeelt alle 10 beschikbare planten
- Toont top 3 aanbevelingen op dashboard met visuele scorebalken

### 3. **Health Trend Analysis**
- Visualiseer gezondheid trend over periode (7d, 30d, 3m, 1y)
- Dynamische trend berekening (% change vs vorige periode)
- Interactieve Chart.js grafieken
- Real-time API updates zonder pagina refresh

### 4. **Sensor Management**
- Clickable sensor cards op dashboard
- Gedetailleerde sensor historiek
- Real-time sensor value display
- Status indicators (OK, Warning, Critical)

### 5. **Multi-User Gardens**
- User authentication & authorization
- Multiple gardens per user
- Multiple playfields per garden
- Role-based access control

## 🛠️ Utility Scripts

Alle scripts bevinden zich in `app/scripts/` en kunnen worden uitgevoerd als Python modules:

### Create Health Score Table
```bash
python3 -m app.scripts.create_health_score_table
```
Maakt de `health_score` tabel aan in de database.

### Generate Sample Data
```bash
python3 -m app.scripts.generate_sample_data --playfield RZ-001-A --days 5
```
Genereert 5 dagen realistische sensordata voor testen.

### Generate Health Scores
```bash
python3 -m app.scripts.generate_health_scores --playfield RZ-001-A --days 5
```
Berekent dagelijkse gezondheidsscores van afgelopen N dagen.

### Setup Test Environment
```bash
python3 -m app.scripts.setup_test_environment
```
Maakt demo user, garden, en playfield aan.
- Username: `demo`
- Password: `demo1234`

### Test Plant Recommendations
```bash
python3 -m app.scripts.test_plant_recommendation
```
Verifieert dat plant recommendation algoritme correct werkt.

## 📚 API Endpoints

### Dashboard & Health
- `GET /dashboard/<serial_number>` - Main dashboard
- `GET /dashboard/<serial_number>/sensor/<sensor_type>` - Sensor details
- `GET /dashboard/<serial_number>/health-trend-api?period=week|month|quarter|year` - Trend data
- `GET /dashboard/<serial_number>/plant-recommendation-api` - Plant recommendations

### Gardens & Playfields
- `GET /garden/select` - Select garden
- `POST /garden/add` - Create garden
- `GET /playfield/<garden_id>` - Playfield selection
- `POST /playfield/<garden_id>/add` - Create playfield

### Authentication
- `POST /login` - User login
- `POST /register` - User registration
- `GET /logout` - Logout

## 🌱 Plant Recommendation Algorithm

**Formula**:
```
score_per_sensor = max(0, 1 - (|measurement - optimal| / tolerance)²)
final_score = weighted_average(all_sensors) × 100
```

**Sensor Weights**:
- Moisture: 25%
- Temperature: 20%
- Humidity: 15%
- Rain: 15%
- Light: 15%
- CO₂: 10%

**10 Available Plants**:
1. Tomaat
2. Courgette
3. Sla
4. Boontjes
5. Aardbei
6. Wortel
7. Prei
8. Ui / sjalot
9. Paprika / peper
10. Pompoen

## 📖 Documentation

- **[Health Score Implementation](docs/HEALTH_SCORE_IMPLEMENTATION.md)** - Gezondheidsscore berekening
- **[Health Trend Feature](docs/HEALTH_TREND_FEATURE.md)** - Trend analyse feature

## 🔧 Configuration

Edit `app/config.py` for:
- Database connection
- Secret key
- Debug mode
- Session settings

## 📝 Database Models

- **User**: User accounts
- **Garden**: User's gardens
- **RobotZone**: Playfields in gardens
- **Sensor**: Sensor definitions
- **Measurement**: Sensor readings
- **PlantProfile**: Plant optimal values (10 plants)
- **HealthScore**: Daily health scores

## 🐛 Troubleshooting

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

## 📄 License

[Your License Here]

## 👥 Team

[Your Team Info Here]
