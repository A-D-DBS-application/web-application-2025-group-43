# Dagelijkse Gezondheidsscore Implementatie

## 📊 Wat is Geïmplementeerd?

De dagelijkse gezondheidsscore wordt nu **automatisch berekend** wanneer je het dashboard bekijkt. De score volgt deze formule:

$$HealthScore = round\left(100 \cdot \frac{\sum_{v} w_v \cdot \max(0, 1 - \left(\frac{|m_v - opt_v|}{dev_v}\right)^2)}{\sum_v w_v}\right)$$

### Waar Wordt Dit Gebruikt?

- ✅ **Cirkel rechtsboven** in het dashboard toont de dagelijkse score (0-100)
- ✅ **Gezondheid Trend grafiek** toont de score trend van afgelopen 30 dagen
- ✅ **Status label** ("Uitstekende groeiomstandigheden" tot "Aandacht vereist") wordt bepaald door de score

### Hoe Werkt De Berekening?

Voor **elke plant sensor** (moisture, temperature, humidity, rain, light, CO₂):

1. **Meetwaarde (m_v)**: 
   - Voor hourly sensoren (vocht, temp, luchtvochtigheid, CO₂): gemiddelde van de dag
   - Voor daily sensoren (licht, regen): laatste dagwaarde

2. **Optimale waarde (opt_v) & tolerantie (dev_v)**:
   - Komt uit het geselecteerde **PlantProfile** (bv. Tomaat, Sla, etc.)
   - `opt_v` = ideale waarde voor die plant
   - `dev_v` = hoeveel mag afwijken voor het slecht wordt

3. **Genormaliseerde afwijking (x_v)**:
   ```
   d_v = |m_v - opt_v|        (afstand tot ideaal)
   x_v = d_v / dev_v          (genormaliseerd)
   ```

4. **Score per variabele (s_v)** met quadratische straf:
   ```
   s_v = max(0, 1 - x_v²)
   ```
   - Perfect (x_v=0) → s_v=1.0 (100%)
   - Net aan grens (x_v=1) → s_v=0 (0%)
   - Verder uit grens → s_v blij 0

5. **Eindresultaat**: Gemiddelde van alle 6 variabelen × 100

## 📁 Bestanden Die Zijn Gewijzigd

### Backend
- **`app/models.py`**: Voegde `HealthScore` model toe (dagelijkse scores opslaan)
- **`app/routes/dashboard_routes.py`**: 
  - Voegde `_calculate_daily_health_score()` functie toe
  - Werkt deze functies in de dashboard route
  - Slaat dagelijkse scores op in database
  - Gebruikt HealthScore records voor trend grafiek

### Database
- **`health_score` tabel**: Slaat dagelijkse scores op
  - `hid` (ID)
  - `score` (0-100)
  - `score_date` (datum)
  - `calculated_at` (wanneer berekend)
  - `serial_number` (FK naar playfield)

### Frontend
- ✅ Geen wijzigingen nodig! Dashboard toont automatisch de berekende score

## 🚀 Setup Instructies

### 1. Database Migratie (Eenmalig)

**Optie A: Python script (aanbevolen)**
```bash
python3 -m app.scripts.create_health_score_table
```

**Optie B: Handmatig SQL (in Supabase SQL Editor)**
```sql
-- Kopieert inhoud van: migrations/add_health_score_table.sql
```

### 2. App Herstarten
```bash
python3 run.py
```

Dat's het! De health score wordt nu **elke keer** berekend als je het dashboard bekijkt.

## 📈 Hoe Kijk Je De Scores?

1. **Rechtsboven in dashboard**: Cirkel met vandaag's score (0-100)
2. **Gezondheid Trend grafiek**: Onderaan rechts, toont trend van afgelopen 30 dagen
3. **Status label**: Onder de score, bv. "Goede groeiomstandigheden"

## ⚙️ Gewichten Aanpassen (Geavanceerd)

In `_calculate_daily_health_score()` staan alle gewichten op `1.0`. Wil je bv. bodemvochtigheid dubbel zo belangrijk?

```python
# In dashboard_routes.py, regel ~140:
weight = {
    'moisture': 2.0,    # 2x zo belangrijk
    'temperature': 1.0,
    'humidity': 1.0,
    'rain': 1.0,
    'light': 1.0,
    'co2': 1.0,
}.get(key, 1.0)
```

## 🔍 Troubleshooting

### Score blijft 0 staan
- ✅ Is een PlantProfile geselecteerd voor het playfield?
- ✅ Heeft het playfield sensor metingen van vandaag?
- ✅ Zijn de mean/std waarden ingevuld in PlantProfile?

### Geen trend grafiek
- ✅ Moeten minstens 2 dagen data zijn om trend te tonen
- ✅ Zorg dat sensor metingen daily worden opgeslagen

## 📝 Test Data

Om snel te testen met dezelfde plant:
1. Maak playfield aan en kies bv. "Tomaat" als plant
2. Zorg dat alle 6 sensors actief zijn met metingen
3. Bezoek dashboard → Health score wordt berekend en opgeslagen
4. Volgende dag → Trend grafiek toont beide scores
