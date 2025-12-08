"""Translation system for English/Dutch support"""

TRANSLATIONS = {
    "en": {
        # Dashboard
        "recommended_plants": "Recommended Plants",
        "alerts": "Alerts",
        "no_active_alerts": "No active alerts. All variables are close to optimal.",
        "critical": "Critical",
        "warning": "Warning",
        "click_for_details": "Click for details →",
        "alerts_heading": "Alerts",
        "health_score": "Health Score",
        "health_trend": "Health Trend",
        "7d": "7 Days",
        "30d": "30 Days",
        "3m": "3 Months",
        "1y": "1 Year",
        "profile_settings": "Profile & Settings",
        "logout": "Logout",
        "view_details": "View details",
        
        # Sensor names
        "moisture": "Moisture",
        "temperature": "Temperature",
        "humidity": "Humidity",
        "rain": "Rain",
        "light": "Light",
        "co2": "CO2",
        
        # Sensor detail
        "average": "Average",
        "minimum": "Minimum",
        "maximum": "Maximum",
        "ideal": "Ideal",
        "tolerance": "Tolerance",
        "back_to_dashboard": "Back to Dashboard",
        "warnings": "Warnings",
        "sensor_data": "Sensor Data",
        
        # Profile
        "profile": "Profile",
        "email": "Email",
        "username": "Username",
        "back": "Back",
        
        # Login/Auth
        "login": "Login",
        "register": "Register",
        "password": "Password",
        "remember_me": "Remember me",
        "dont_have_account": "Don't have an account?",
        "already_have_account": "Already have an account?",
        
        # Garden/Playfield selection
        "select_garden": "Select Garden",
        "select_playfield": "Select Playfield",
        "gardens": "Gardens",
        "playfields": "Playfields",
        "add": "Add",
        "edit": "Edit",
        "delete": "Delete",
        
        # General
        "ideal_plant_dependent": "Ideal: plant profile-dependent",
        "language": "Language",
    },
    "nl": {
        # Dashboard
        "recommended_plants": "Aanbevolen planten",
        "alerts": "Alerts",
        "no_active_alerts": "Geen actieve alerts. Alle variabelen liggen dicht bij het optimum.",
        "critical": "Kritiek",
        "warning": "Waarschuwing",
        "click_for_details": "Klik voor details →",
        "alerts_heading": "Alerts",
        "health_score": "Gezondheidsscores",
        "health_trend": "Gezondheidstrend",
        "7d": "7 Dagen",
        "30d": "30 Dagen",
        "3m": "3 Maanden",
        "1y": "1 Jaar",
        "profile_settings": "Profiel & Instellingen",
        "logout": "Afmelden",
        "view_details": "Details bekijken",
        
        # Sensor names
        "moisture": "Vochtigheid",
        "temperature": "Temperatuur",
        "humidity": "Luchtvochtigheid",
        "rain": "Regen",
        "light": "Licht",
        "co2": "CO₂",
        
        # Sensor detail
        "average": "Gemiddelde",
        "minimum": "Minimum",
        "maximum": "Maximum",
        "ideal": "Ideaal",
        "tolerance": "Tolerantie",
        "back_to_dashboard": "Terug naar Dashboard",
        "warnings": "Waarschuwingen",
        "sensor_data": "Sensorgegevens",
        
        # Profile
        "profile": "Profiel",
        "email": "E-mailadres",
        "username": "Gebruikersnaam",
        "back": "Terug",
        
        # Login/Auth
        "login": "Inloggen",
        "register": "Registreren",
        "password": "Wachtwoord",
        "remember_me": "Onthoud mij",
        "dont_have_account": "Heb je geen account?",
        "already_have_account": "Heb je al een account?",
        
        # Garden/Playfield selection
        "select_garden": "Tuin selecteren",
        "select_playfield": "Speelveld selecteren",
        "gardens": "Tuinen",
        "playfields": "Speelvelden",
        "add": "Toevoegen",
        "edit": "Bewerken",
        "delete": "Verwijderen",
        
        # General
        "ideal_plant_dependent": "Ideaal: plantprofiel-afhankelijk",
        "language": "Taal",
    }
}

def get_translation(key: str, language: str = "en") -> str:
    """Get translated string for given key and language"""
    if language not in TRANSLATIONS:
        language = "en"
    return TRANSLATIONS[language].get(key, key)

def get_all_translations(language: str = "en") -> dict:
    """Get all translations for a language"""
    if language not in TRANSLATIONS:
        language = "en"
    return TRANSLATIONS[language]
