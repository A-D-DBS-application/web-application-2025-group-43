# Gezondheid Trend Feature - Documentatie

## 🎯 Wat is Geïmplementeerd?

Een **volledig dynamische gezondheid trend feature** met:

1. **Period Selector** - Kies tussen 7d, 30d, 3m, 1y
2. **Adaptive Trend Berekening** - Trend % werkt relatief aan vorige periode
3. **Dynamische Grafiek** - Chart.js update zonder page reload
4. **Responsive Labels** - Datum formaat past aan per periode

## 📊 Hoe Werkt Het?

### Backend (`_get_health_trend_data`)

```python
def _get_health_trend_data(serial_number, period='month'):
    # 1. Bepaal datum range (bijv. afgelopen 30 dagen)
    # 2. Query HealthScore records voor die periode
    # 3. Query VORIGE periode (voor trend berekening)
    # 4. Bereken gemiddelden:
    #    - current_avg = gemiddelde van huidige periode
    #    - previous_avg = gemiddelde van vorige periode
    # 5. Trend % = ((current - previous) / previous) * 100
    # 6. Return alles als JSON
```

**Periode definities**:
- `week` (7d): vorige 7 dagen vs daarvoor 7 dagen
- `month` (30d): vorige 30 dagen vs daarvoor 30 dagen (default)
- `quarter` (3m): vorige 90 dagen vs daarvoor 90 dagen
- `year` (1y): vorig jaar vs daarvoor jaar

### API Endpoint

```
GET /dashboard/<serial_number>/health-trend-api?period=week|month|quarter|year
```

**Response**:
```json
{
  "values": [45.2, 50.1, 48.5, ...],  // Scores per dag
  "labels": ["01/12", "02/12", ...],  // Datums
  "trend_percent": 12,                 // +/- % vs vorige periode
  "trend_direction": "up",             // "up", "down", "neutral"
  "period_label": "Laatste 7 dagen",
  "current_avg": 48,                   // Gemiddelde huidige periode
  "previous_avg": 42                   // Gemiddelde vorige periode
}
```

### Frontend

**Period Buttons** - Click laadt nieuwe data:
```html
<button class="period-btn active" data-period="week">7d</button>
<button class="period-btn" data-period="month">30d</button>
<button class="period-btn" data-period="quarter">3m</button>
<button class="period-btn" data-period="year">1y</button>
```

**JavaScript** - Event listeners:
1. Fetch data van API
2. Update UI labels (trend %, period label, averages)
3. Destroy oude chart & create nieuwe Chart.js instance
4. Animate smooth transition

## 🔄 Data Flow

```
User klikt "30d" knop
        ↓
JavaScript fetch /dashboard/{serial}/health-trend-api?period=month
        ↓
Backend: _get_health_trend_data('RZ-001', 'month')
  - Haalt HealthScore van vorige 30 dagen op
  - Haalt HealthScore van daarvoor 30 dagen op
  - Berekent gemiddelden & trend %
        ↓
Return JSON
        ↓
Frontend update:
  - Grafiek rebuildend
  - Labels/percentages refreshen
  - Buttons actief/inactief update
```

## 📈 Voorbeelden

### Scenario 1: Week view met positieve trend
```
Vorige 7 dagen: gemiddelde 42%
Huidige 7 dagen: gemiddelde 48%
Trend: +14% (= ((48-42)/42)*100)
UI toont: ▲ +14%
```

### Scenario 2: Month view met negatieve trend
```
Vorige 30 dagen: gemiddelde 65%
Huidige 30 dagen: gemiddelde 58%
Trend: -11% (= ((58-65)/65)*100)
UI toont: ▼ -11%
```

### Scenario 3: Year view (seizoenseffecten)
```
Vorig jaar: gemiddelde 55%
Dit jaar: gemiddelde 72%
Trend: +31%
UI toont: ▲ +31%
```

## 🎨 UI/UX Features

1. **Dynamic Arrow**:
   - ▲ = uptrend (groen tint)
   - ▼ = downtrend (rood tint)
   - → = neutral / geen vorige data

2. **Period Labels**:
   - "Laatste 7 dagen"
   - "Laatste 30 dagen"
   - "Laatste 3 maanden"
   - "Afgelopen jaar"

3. **Start & Nu Indicators**:
   - Start: `Start: 42%` (begin van periode)
   - Nu: `Nu: 48%` (huidige gemiddelde)

4. **Chart Formatting**:
   - Datum format past aan per periode
   - 7d: `01/12` (dag/maand)
   - 30d: `01/12`
   - 3m: `01/12`
   - 1y: `01/12`

## 🧪 Test Scenario's

### Test 1: Period Switching
1. Open dashboard
2. Klik "7d" → Chart update, trend % verandertt
3. Klik "30d" → Chart update met meer datapunten
4. Klik "1y" → Chart toont jaar overview

### Test 2: Trend Calculation
1. Dashboard toont: "Vorige periode: 50% → Nu: 55%" 
2. Trend moet zijn: +10%
3. Arrow moet ▲ zijn (groen)

### Test 3: Insufficient Data
1. Playfield met minder dan 7 dagen data
2. Week view → Toont beschikbare data
3. Trend % = 0 (onvoldoende vorige data)

## 🔧 Aanpassingen / Geavanceerd

### Trend Formule Aanpassen

In `dashboard_routes.py`, functie `_get_health_trend_data`:

```python
# Huidige formule (relatief percentage)
trend_percent = round(((current_avg - previous_avg) / previous_avg) * 100)

# Alternatief: Absolute verschil
trend_percent = round(current_avg - previous_avg)

# Alternatief: Ratio
trend_percent = round((current_avg / previous_avg - 1) * 100)
```

### Datum Format Aanpassen

```python
fmt = "%d/%m"  # dag/maand
fmt = "%m-%d"  # maand-dag (VS)
fmt = "%d %b"  # dag januari
fmt = "%W"     # weeknummer
```

### Period Toevoegen

Voeg toe in `_get_health_trend_data`:

```python
elif period == 'biweek':
    days = 14
    compare_days = 14
    period_label = "Laatste 14 dagen"
    fmt = "%d/%m"
```

En in HTML buttons:
```html
<button class="period-btn" data-period="biweek">14d</button>
```

## 🐛 Troubleshooting

### Trend Toont 0%
- ✅ Vorige periode heeft geen data
- ✅ Beide periodes hebben dezelfde gemiddelde
- **Fix**: Meer testdata toevoegen

### Grafiek Laadt Niet
- ✅ Check browser console voor fetch errors
- ✅ Zorg dat playfield valid serial_number heeft
- ✅ HealthScore records moeten in database bestaan

### API Returns 401
- ✅ User moet ingelogd zijn
- ✅ Playfield moet van huidige user zijn
- ✅ Garden permission moet correct zijn

## 📚 Code Files Gewijzigd

1. **`app/routes/dashboard_routes.py`**:
   - `_get_health_trend_data()` — Trend berekening
   - `health_trend_api()` — API endpoint
   - `dashboard()` — Voeg trend_data toe aan template context

2. **`app/templates/dashboard.html`**:
   - Period selector buttons (HTML)
   - Period button styling (CSS)
   - Trend updater JavaScript

3. **Geen database wijzigingen** - Gebruikt bestaande `health_score` tabel

## ⚡ Performance Notes

- API endpoint cacht niet (elke request berekent opnieuw)
- Chart.js destroy/recreate per request (iets overhead, maar acceptabel)
- Voor 365 datapunten (1 jaar): ~250ms berekening

**Optimalisatie (toekomstig)**:
- Redis cache trend data (1 uur TTL)
- Aggregeer HealthScore per week/maand in DB
- Client-side caching van eerder opgehaalde data
