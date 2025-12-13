# app/models.py
from . import db
from sqlalchemy.dialects.postgresql import UUID
import uuid


# ==========================================================
# PlantProfile (optimale waarden per plant)
# ==========================================================
class PlantProfile(db.Model):
    __tablename__ = "plant_profiles"

    # Supabase: plant_profiles.plant_name (text) = PK
    plant_name = db.Column(db.String, primary_key=True, nullable=False)
    display_name = db.Column(db.String, nullable=False)

    temperature_mean = db.Column(db.Numeric)
    temperature_std = db.Column(db.Numeric)

    soil_moisture_mean = db.Column(db.Numeric)
    soil_moisture_std = db.Column(db.Numeric)

    humidity_mean = db.Column(db.Numeric)
    humidity_std = db.Column(db.Numeric)

    rain_mm_week_mean = db.Column(db.Numeric)
    rain_mm_week_std = db.Column(db.Numeric)

    ppfd_mean = db.Column(db.Numeric)
    ppfd_std = db.Column(db.Numeric)

    co2_mean = db.Column(db.Numeric)
    co2_std = db.Column(db.Numeric)

    robot_zones = db.relationship("RobotZone", back_populates="plant_profile")

    def __repr__(self):
        return f"<PlantProfile {self.display_name} ({self.plant_name})>"


# ==========================================================
# User (Supabase: uemail, uname, phone, adress)
# ==========================================================
class User(db.Model):
    __tablename__ = "user"

    uemail = db.Column(db.String, primary_key=True, nullable=False)
    uname = db.Column(db.String, nullable=False)
    phone = db.Column(db.String)
    adress = db.Column(db.String)

    gardens = db.relationship(
        "Garden",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<User {self.uemail}>"


# ==========================================================
# Garden (Supabase: garden_id, garden_name, adress_garden, area_garden, user_email)
# ==========================================================
class Garden(db.Model):
    __tablename__ = "garden"

    garden_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    garden_name = db.Column(db.String, nullable=False)
    adress_garden = db.Column(db.String)
    area_garden = db.Column(db.Numeric)

    user_email = db.Column(
        db.String,
        db.ForeignKey("user.uemail", ondelete="CASCADE"),
        nullable=True,
    )

    user = db.relationship("User", back_populates="gardens")

    robot_zones = db.relationship(
        "RobotZone",
        back_populates="garden",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Garden {self.garden_name} ({self.garden_id})>"


# ==========================================================
# Robot Zone (Supabase: serial_number, area_playfield, robot_name, garden_id, plant_name)
# ==========================================================
class RobotZone(db.Model):
    __tablename__ = "robot_zone"

    serial_number = db.Column(db.String, primary_key=True, nullable=False)
    area_playfield = db.Column(db.Numeric)
    robot_name = db.Column(db.String)

    garden_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("garden.garden_id", ondelete="CASCADE"),
        nullable=True,
    )

    # FK naar plant_profiles.plant_name (Supabase heeft plant_name kolom)
    plant_name = db.Column(
        db.String,
        db.ForeignKey("plant_profiles.plant_name", ondelete="SET NULL"),
        nullable=True,
    )

    garden = db.relationship("Garden", back_populates="robot_zones")
    plant_profile = db.relationship("PlantProfile", back_populates="robot_zones")

    sensors = db.relationship(
        "Sensor",
        back_populates="robot_zone",
        cascade="all, delete-orphan",
    )

    health_scores = db.relationship(
        "HealthScore",
        back_populates="robot_zone",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<RobotZone {self.serial_number} ({self.robot_name})>"


# ==========================================================
# Sensor (Supabase: srnr_sensor, sensor_type, unit, serial_number)
# ==========================================================
class Sensor(db.Model):
    __tablename__ = "sensor"

    srnr_sensor = db.Column(db.String, primary_key=True, nullable=False)
    sensor_type = db.Column(db.String, nullable=False)
    unit = db.Column(db.String)

    serial_number = db.Column(
        db.String,
        db.ForeignKey("robot_zone.serial_number", ondelete="CASCADE"),
        nullable=True,
    )

    robot_zone = db.relationship("RobotZone", back_populates="sensors")

    measurements = db.relationship(
        "Measurement",
        back_populates="sensor",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Sensor {self.srnr_sensor} ({self.sensor_type})>"


# ==========================================================
# Measurement (Supabase: mid, value, time_m, srnr_sensor)
# ==========================================================
class Measurement(db.Model):
    __tablename__ = "measurement"

    mid = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    value = db.Column(db.Numeric, nullable=False)
    time_m = db.Column(db.DateTime(timezone=True))

    srnr_sensor = db.Column(
        db.String,
        db.ForeignKey("sensor.srnr_sensor", ondelete="CASCADE"),
        nullable=True,
    )

    sensor = db.relationship("Sensor", back_populates="measurements")

    def __repr__(self):
        return f"<Measurement {self.mid} sensor={self.srnr_sensor}>"


# ==========================================================
# HealthScore (Supabase: hid, score, calculated_at, serial_number)
# ==========================================================
class HealthScore(db.Model):
    __tablename__ = "health_score"

    hid = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    score = db.Column(db.Float, nullable=False)
    score_date = db.Column(db.Date, nullable=False)
    calculated_at = db.Column(db.DateTime(timezone=True))
    serial_number = db.Column(
        db.String,
        db.ForeignKey("robot_zone.serial_number", ondelete="CASCADE"),
        nullable=True,
    )

    robot_zone = db.relationship("RobotZone", back_populates="health_scores")

    def __repr__(self):
        return f"<HealthScore {self.serial_number} {self.score_date}: {self.score}>"
