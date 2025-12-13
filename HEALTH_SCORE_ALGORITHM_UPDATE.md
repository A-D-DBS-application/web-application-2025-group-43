# Health Score Algorithm - Update

## 🎯 Probleem
Het algoritme gebruikte `calculated_at` (het timestamp van wanneer de score werd berekend) in plaats van `score_date` (de datum waarop de metingen plaatsvonden) om te controleren of een health score al bestond. Dit leidde tot problemen:

- Als de app op 14/12 werd gerund met data van 12/12, zou de score een `calculated_at` van 14/12 krijgen
- Dit zou meerdere scores per dag kunnen veroorzaken
- De datums en scores zouden niet met elkaar overeenkomen

## ✅ Oplossing

Het algoritme is nu aangepast zodat:

### 1. **Datumcontrole op `score_date`** 
   - De functie `_get_or_create_daily_health_score()` controleert nu of er al een score voor die **specifieke DATUM** van de meting bestaat
   - Gebruikt `HealthScore.score_date` in plaats van `func.date(HealthScore.calculated_at)`

### 2. **Juiste datum opslaan**
   - Bij het aanmaken van een new HealthScore: `score_date = measurement_date`
   - Dit is de datum waarop de metingen plaatsvonden, NIET de huidige datum
   - `calculated_at` wordt ingesteld op dezelfde dag (midnight), maar dit is alleen voor audit/tracking

### 3. **Trend-queries aangepast**
   - `_get_health_trend_data()` gebruikt nu `HealthScore.score_date` voor filtering in plaats van `calculated_at`
   - Dit zorgt ervoor dat de trend-grafiek altijd de juiste datums toont

### 4. **Database schema**
   - HealthScore model in `models.py` nu met `score_date` kolom
   - Migratiescript voegt `score_date` toe aan bestaande tabellen (als nodig)
   - UNIQUE constraint op `(serial_number, score_date)` voorkomt duplicaten per dag

## 📋 Gewijzigde Bestanden

1. **`app/models.py`**
   - Toegevoegd: `score_date = db.Column(db.Date, nullable=False)` aan HealthScore model
   - Updated: `__repr__` om `score_date` te tonen

2. **`app/routes/dashboard_routes.py`**
   - `_get_or_create_daily_health_score()`: Nu controleert op `score_date` en vult `score_date` in
   - `_get_health_trend_data()`: Queries gebruiken `score_date` filter
   - `dashboard()`: health_trend_labels uses `score_date.strftime()` in plaats van `calculated_at`

3. **`migrations/add_health_score_table.sql`**
   - Enhanced: Voegt `score_date` kolom toe aan bestaande tabellen
   - Bevat migration logic om oude data in te vullen

## 🔄 Hoe Het Nu Werkt

**Voorbeeld: App runnen op 14/12 met data van 12/12**

```
1. Algoritme vindt laatst meting op 12/12
2. Controleert: Is er al een score voor 12/12?
3. Check: SELECT * FROM health_score WHERE serial_number='RZ-001-A' AND score_date='2024-12-12'
4. GEEN match? Bereken score en sla op:
   - score_date = 2024-12-12
   - calculated_at = 2024-12-12 00:00:00
   - (Niet 2024-12-14!)
5. Volgende run op 14/12 met zelfde data? 
   - Ziet de bestaande score voor 12/12
   - Doet niets (idempotent)
```

## ⚙️ Setup

Run de migratie:
```bash
# In Supabase SQL Editor:
-- Copy contents van migrations/add_health_score_table.sql

# Of als je psql hebt:
psql -f migrations/add_health_score_table.sql
```

Dan herstarten:
```bash
python3 run.py
```

## ✨ Voordelen

✅ Datums zijn consistent tussen metingen en scores
✅ Geen duplicaten per dag
✅ Idempotent: Meerdere runs geven hetzelfde resultaat
✅ Juiste trend-grafieken (geen verwarrende datums)
✅ Future-proof: Werkt ook als data achteraf wordt ingevuld
