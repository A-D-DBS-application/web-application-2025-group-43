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
        "view_all": "View all",
        "no_recommendations": "No recommendations available at the moment.",
        "playfield_dashboard": "Playfield Dashboard — Capenta",
        "data_variables": "Data variables",
        "rainfall_water_needs": "Rainfall (Water Needs)",
        "co2_level": "CO₂ Level",
        "back_to_playfields": "Back to playfields",
        "overall_playfield_health": "Overall Playfield Health",
        "top_recommendation": "Top",
        "2nd_recommendation": "2nd",
        "start": "Start",
        "now": "Now",
        "water_plants": "Water Plants",
        "remove_weeds": "Remove Weeds",
        "manual_action": "Manual action",
        "no_data": "no data",
        "ideal_plant_dependent_ppfd": "Ideal: plant profile-dependent (PPFD)",
        "soil_moisture": "Soil Moisture",
        "excellent": "Excellent",
        "good": "Good",
        "fair": "Fair",
        "poor": "Poor",
        "excellent_growth_conditions": "Excellent growth conditions",
        "good_growth_conditions": "Good growth conditions",
        "fair_growth_conditions": "Fair growth conditions",
        "attention_required": "Attention required",
        "higher_than_ideal": "Higher than ideal",
        "lower_than_ideal": "Lower than ideal",
        "deviating_from_ideal": "Deviating from ideal",
        "optimal": "Optimal",
        "slight_deviation": "Slight deviation",
        "strong_deviation": "Strong deviation",
        "no_reference": "No reference",
        
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
        "name": "Name",
        "phone": "Phone Number",
        "address": "Address",
        "fields": "Fields (read only)",
        
        # Login/Auth
        "login": "Login",
        "register": "Register",
        "password": "Password",
        "remember_me": "Remember me",
        "dont_have_account": "Don't have an account?",
        "already_have_account": "Already have an account?",
        "email_address": "Email Address",
        "create_account": "Create Account",
        "sign_in": "Sign In",
        "invalid_credentials": "Invalid email or password",
        "email_already_registered": "Email already registered",
        "account_created_success": "Account created! Please log in.",
        "capenta_autonomous": "Capenta – Autonomous Garden Robot",
        "fill_info": "Fill in the information to start using Capenta.",
        
        # Garden/Playfield selection
        "select_garden": "Select Garden",
        "select_playfield": "Select Playfield",
        "gardens": "Gardens",
        "playfields": "Playfields",
        "add": "Add",
        "edit": "Edit",
        "delete": "Delete",
        "add_garden": "Add Garden",
        "add_playfield": "Add Playfield",
        "garden_name": "Garden Name",
        "location": "Location",
        "edit_garden": "Edit Garden",
        "edit_playfield": "Edit Playfield",
        "playfield_name": "Playfield Name",
        "serial_number": "Serial Number",
        "back_to_gardens": "Back to gardens",
        "welcome_select_garden": "Welcome! Select a garden to get started",
        "gardens_playfields": "Gardens & Playfields",
        "no_gardens_yet": "You don't have any gardens yet. Click on Add Garden to add your first garden.",
        "confirm_delete_garden": "Are you sure you want to delete this garden?",
        "new_garden": "New Garden",
        "garden_details_subtitle": "Enter the details of your garden to get started.",
        "garden_name_placeholder": "e.g. East Garden",
        "address_placeholder": "Street, number, city, country",
        "size_of_garden": "Size of garden",
        "size_placeholder": "e.g. 120",
        "cancel": "Cancel",
        "save_garden": "Save Garden",
        
        "update_garden": "Update Garden",
        "change_details_and_save": "Change the details and save.",
        "update_playfield": "Update Playfield",
        "adjust_details_and_save": "Adjust the details and save.",
        "save_changes": "Save Changes",
        "new_playfield": "New Playfield",
        "playfield_details_subtitle": "Provide the details for your new playfield.",
        "playfield_name_placeholder": "e.g., Robot 1's field",
        "size_of_playfield": "Size of playfield",
        "crop_plants": "Crop / Plants",
        "select_a_crop": "Select a crop",
        "save_playfield": "Save Playfield",

        "no_crop_set": "No crop set",

        # General
        "ideal_plant_dependent": "Ideal: plant profile-dependent",
        "language": "Language",
        "en": "English",
        "nl": "Nederlands",

        # Sensor Detail Page specific
        "chart": "Chart",
        "target_value": "Target value",
        "statistics": "Statistics",
        "status": "Status",
        "everything_running_optimally": "Everything is running optimally!",
        "advice_tips": "Advice & Tips",
        "current_reading": "Current reading",
        "current_value": "Current value",
        "target": "Target",
        "z_score": "Z-Score",
        "playfield": "Playfield", # Added as a general term
        "unknown": "Unknown", # Added for unknown plant profile
        "ideal_values": "Ideal Values", # Added for target values section
        
        # Crops
        "Beans": "Beans",
        "Carrot": "Carrot",
        "Leek": "Leek",
        "Lettuce": "Lettuce",
        "Onion/shallot": "Onion/shallot",
        "Paprika/pepper": "Paprika/pepper",
        "Pumpkin": "Pumpkin",
        "Strawberry": "Strawberry",
        "Tomato": "Tomato",
        "Zucchini": "Zucchini",
        "Plant": "Plant",

        # Tips (Moisture)
        "tip_moisture_drip_irrigation": "Check if drip irrigation works correctly",
        "tip_moisture_good_drainage": "Ensure good drainage in the plant bed",
        "tip_moisture_increase_watering_dry": "Increase watering in dry periods",
        "tip_moisture_decrease_watering_rain": "Decrease watering in rainy periods",
        "tip_moisture_soil_compaction": "Soil compaction can hinder water absorption",

        # Tips (Temperature)
        "tip_temp_adjust_ventilation": "Adjust ventilation to regulate temperature",
        "tip_temp_increase_heating_cold_night": "Increase heating in cold nights",
        "tip_temp_good_air_circulation": "Ensure good air circulation",
        "tip_temp_check_greenhouse_insulation": "Check insulation of the greenhouse/conservatory",
        "tip_temp_extreme_fluctuations_harm": "Extreme temperature fluctuations harm plant growth",

        # Tips (Humidity)
        "tip_humidity_increase_misting": "Increase humidity via misting",
        "tip_humidity_improve_ventilation_high": "Improve ventilation if humidity is too high",
        "tip_humidity_diseases_thrive_high": "Diseases thrive in high humidity (>80%)",
        "tip_humidity_low_hinders_growth": "Too low humidity (<40%) hinders growth",
        "tip_humidity_check_hvac": "Check HVAC (Heating, Ventilation, Air Conditioning) system",

        # Tips (Rain)
        "tip_rain_adjust_irrigation_natural": "Adjust irrigation based on natural rainfall",
        "tip_rain_use_rainwater_harvesting": "Use rainwater harvesting systems",
        "tip_rain_check_drainage_heavy_rain": "Check water drainage after heavy rainfall",
        "tip_rain_prevent_stagnation_root_rot": "Prevent water stagnation and root rot",
        "tip_rain_monitor_weather_irrigation": "Monitor weather forecasts for irrigation planning",

        # Tips (Light)
        "tip_light_increase_intensity_grow_lights": "Increase light intensity with extra grow lights",
        "tip_light_ppfd_more_important_duration": "PPFD is more important than duration - intensity primary",
        "tip_light_check_led_height": "Check height of LED lamps",
        "tip_light_clean_reflectors_optimal_output": "Clean lenses/reflectors for optimal light output",
        "tip_light_seasonal_change_natural_light": "Seasonal change affects natural light incidence",

        # Tips (CO2)
        "tip_co2_low_growth_limitation": "CO₂ concentration: low (<300) = growth limitation",
        "tip_co2_optimal_range": "Optimal range: 400-1000 ppm (plant type dependent)",
        "tip_co2_improve_ventilation_supplement": "Improve ventilation to supplement CO₂",
        "tip_co2_sources": "CO₂ sources: compost, decomposition, CO₂ generators",
        "tip_co2_high_negative_without_light": "High CO₂ (>1500 ppm) can be negative without more light",
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
        "logout": "Uitloggen",
        "view_details": "Details bekijken",
        "view_all": "Bekijk alles",
        "no_recommendations": "Geen aanbevelingen beschikbaar op dit moment.",
        "playfield_dashboard": "Speelveld Dashboard — Capenta",
        "data_variables": "Data variabelen",
        "rainfall_water_needs": "Neerslag (Waterbehoefte)",
        "co2_level": "CO₂ Niveau",
        "back_to_playfields": "Terug naar speelvelden",
        "overall_playfield_health": "Algehele Speelveld Gezondheid",
        "top_recommendation": "Top",
        "2nd_recommendation": "2e",
        "start": "Start",
        "now": "Nu",
        "water_plants": "Planten water geven",
        "remove_weeds": "Onkruid wieden",
        "manual_action": "Handmatige actie",
        "no_data": "geen data",
        "ideal_plant_dependent_ppfd": "Ideaal: plantprofiel-afhankelijk (PPFD)",
        "soil_moisture": "Bodemvochtigheid",
        "excellent": "Uitstekend",
        "good": "Goed",
        "fair": "Redelijk",
        "poor": "Slecht",
        "excellent_growth_conditions": "Uitstekende groeiomstandigheden",
        "good_growth_conditions": "Goede groeiomstandigheden",
        "fair_growth_conditions": "Matige groeiomstandigheden",
        "attention_required": "Aandacht vereist",
        "higher_than_ideal": "Hoger dan ideaal",
        "lower_than_ideal": "Lager dan ideaal",
        "deviating_from_ideal": "Afwijkend van ideaal",
        "optimal": "Optimaal",
        "slight_deviation": "Lichte afwijking",
        "strong_deviation": "Sterke afwijking",
        "no_reference": "Geen referentie",

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
        "name": "Naam",
        "phone": "Telefoonnummer",
        "address": "Adres",
        "fields": "Velden (alleen-lezen)",
        
        # Login/Auth
        "login": "Inloggen",
        "register": "Registreren",
        "password": "Wachtwoord",
        "remember_me": "Onthoud mij",
        "dont_have_account": "Heb je geen account?",
        "already_have_account": "Heb je al een account?",
        "email_address": "E-mailadres",
        "create_account": "Account aanmaken",
        "sign_in": "Inloggen",
        "invalid_credentials": "Ongeldig e-mailadres of wachtwoord",
        "email_already_registered": "E-mailadres al geregistreerd",
        "account_created_success": "Account aangemaakt! Log alstublieft in.",
        "capenta_autonomous": "Capenta – Autonome Tuinrobot",
        "fill_info": "Vul de informatie in om Capenta te gebruiken.",
        
        # Garden/Playfield selection
        "select_garden": "Tuin selecteren",
        "select_playfield": "Speelveld selecteren",
        "gardens": "Tuinen",
        "playfields": "Speelvelden",
        "add": "Toevoegen",
        "edit": "Bewerken",
        "delete": "Verwijderen",
        "add_garden": "Tuin toevoegen",
        "add_playfield": "Speelveld toevoegen",
        "garden_name": "Tuinnaam",
        "location": "Locatie",
        "edit_garden": "Tuin bewerken",
        "edit_playfield": "Speelveld bewerken",
        "playfield_name": "Speelveldnaam",
        "serial_number": "Serienummer",
        "back_to_gardens": "Terug naar tuinen",
        "welcome_select_garden": "Welkom! Selecteer een tuin om te beginnen",
        "gardens_playfields": "Tuinen & Speelvelden",
        "no_gardens_yet": "Je hebt nog geen tuinen. Klik op Tuin toevoegen om je eerste tuin toe te voegen.",
        "confirm_delete_garden": "Weet je zeker dat je deze tuin wilt verwijderen?",
        "new_garden": "Nieuwe Tuin",
        "garden_details_subtitle": "Voer de details van je tuin in om te beginnen.",
        "garden_name_placeholder": "bv. Oost-tuin",
        "address_placeholder": "Straat, nummer, stad, land",
        "size_of_garden": "Grootte van de tuin",
        "size_placeholder": "bv. 120",
        "cancel": "Annuleren",
        "save_garden": "Tuin Opslaan",

        "update_garden": "Tuin bijwerken",
        "change_details_and_save": "Wijzig de details en sla op.",
        "update_playfield": "Speelveld bijwerken",
        "adjust_details_and_save": "Pas de details aan en sla op.",
        "save_changes": "Wijzigingen opslaan",
        "new_playfield": "Nieuw speelveld",
        "playfield_details_subtitle": "Geef de details voor je nieuwe speelveld op.",
        "playfield_name_placeholder": "bv. Robot 1's veld",
        "size_of_playfield": "Grootte van speelveld",
        "crop_plants": "Gewas / Planten",
        "select_a_crop": "Selecteer een gewas",
        "save_playfield": "Speelveld opslaan",
        
        "no_crop_set": "Geen gewas ingesteld",

        # General
        "ideal_plant_dependent": "Ideaal: plantprofiel-afhankelijk",
        "language": "Taal",
        "en": "English",
        "nl": "Nederlands",

        # Sensor Detail Page specific
        "chart": "Grafiek",
        "target_value": "Doelwaarde",
        "statistics": "Statistieken",
        "status": "Status",
        "everything_running_optimally": "Alles draait optimaal!",
        "advice_tips": "Advies & Tips",
        "current_reading": "Huidige meting",
        "current_value": "Huidige waarde",
        "target": "Doel",
        "z_score": "Z-Score",
        "playfield": "Speelveld", # Added as a general term
        "unknown": "Onbekend", # Added for unknown plant profile
        "ideal_values": "Ideale waarden", # Added for target values section

        # Crops
        "Beans": "Bonen",
        "Carrot": "Wortel",
        "Leek": "Prei",
        "Lettuce": "Sla",
        "Onion/shallot": "Ui/sjalot",
        "Paprika/pepper": "Paprika/peper",
        "Pumpkin": "Pompoen",
        "Strawberry": "Aardbei",
        "Tomato": "Tomaat",
        "Zucchini": "Courgette",
        "Plant": "Plant",
        
        # Tips (Moisture)
        "tip_moisture_drip_irrigation": "Controleer of de druppelirrigatie correct werkt",
        "tip_moisture_good_drainage": "Zorg voor goede drainage in het plantbed",
        "tip_moisture_increase_watering_dry": "Verhoog watergift in droge periodes",
        "tip_moisture_decrease_watering_rain": "Verlaag watergift in regenperiodes",
        "tip_moisture_soil_compaction": "Compactie in de grond kan wateropname belemmeren",

        # Tips (Temperature)
        "tip_temp_adjust_ventilation": "Pas ventilatie aan om temperatuur te reguleren",
        "tip_temp_increase_heating_cold_night": "Toename in verwarming in koude nacht",
        "tip_temp_good_air_circulation": "Zorg voor goede luchtcirculatie",
        "tip_temp_check_greenhouse_insulation": "Controleer isolatie van de kas/serre",
        "tip_temp_extreme_fluctuations_harm": "Extreme temperatuurschommelingen schaden plantgroei",

        # Tips (Humidity)
        "tip_humidity_increase_misting": "Verhoog luchtvochtigheid via vernevelingen",
        "tip_humidity_improve_ventilation_high": "Verbeter ventilatie als luchtvochtigheid te hoog",
        "tip_humidity_diseases_thrive_high": "Ziekten gedijen bij hoge luchtvochtigheid (>80%)",
        "tip_humidity_low_hinders_growth": "Te lage luchtvochtigheid (<40%) belemmert groei",
        "tip_humidity_check_hvac": "Controleer HVAC (Heating, Ventilation, Air Conditioning) systeem",

        # Tips (Rain)
        "tip_rain_adjust_irrigation_natural": "Pas irrigatie aan op basis van natuurlijke regenval",
        "tip_rain_use_rainwater_harvesting": "Gebruik regenwater harvesting systems",
        "tip_rain_check_drainage_heavy_rain": "Controleer waterafvoer na zware regenval",
        "tip_rain_prevent_stagnation_root_rot": "Voorkom waterstagnatie en wortelrot",
        "tip_rain_monitor_weather_irrigation": "Monitor weersverwachtingen voor irrigatieplanning",

        # Tips (Light)
        "tip_light_increase_intensity_grow_lights": "Verhoog lichtintensiteit met extra grow lights",
        "tip_light_ppfd_more_important_duration": "PPFD is belangrijker dan duur - intensiteit primair",
        "tip_light_check_led_height": "Controleer hoogte van LED-lampen",
        "tip_light_clean_reflectors_optimal_output": "Reinig lensen/reflectoren voor optimale lichtopbrengst",
        "tip_light_seasonal_change_natural_light": "Seizoensverandering beïnvloedt natuurlijke lichtinval",

        # Tips (CO2)
        "tip_co2_low_growth_limitation": "CO₂ concentratie: laag (<300) = groeibeperking",
        "tip_co2_optimal_range": "Optimaal bereik: 400-1000 ppm (planttype afhankelijk)",
        "tip_co2_improve_ventilation_supplement": "Verbeter ventilatie om CO₂ aan te vullen",
        "tip_co2_sources": "CO₂ bronnen: compost, decomposeren, CO₂ generatoren",
        "tip_co2_high_negative_without_light": "Hoge CO₂ (>1500 ppm) kan negatief zijn zonder meer licht",
    }
}

def get_translation(key: str, language: str = "en") -> str:
    """Get translated string for given key and language"""
    if language not in TRANSLATIONS:
        language = "en"

    # First, check in the main categories
    if key in TRANSLATIONS[language]:
        return TRANSLATIONS[language][key]

    # Fallback to English crops if the key exists there
    if key in TRANSLATIONS["en"]:
        return TRANSLATIONS[language].get(key, key)

    return key

def get_all_translations(language: str = "en") -> dict:
    """Get all translations for a language"""
    if language not in TRANSLATIONS:
        language = "en"
    return TRANSLATIONS[language]
