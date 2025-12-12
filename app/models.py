from . import db
from sqlalchemy.dialects.postgresql import UUID
import uuid


# ==========================================================
# PlantProfile (optimale waarden per plant)
# ==========================================================
class PlantProfile(db.Model):
    __tablename__ = "plant_profiles"

    id = db.Column(db.BigInteger, primary_key=True)
    key = db.Column(db.String, unique=True, nullable=False)
    display_name = db.Column(db.String, nullable=False)

    temperature_mean = db.Column(db.Float)
    temperature_std = db.Column(db.Float)

    soil_moisture_mean = db.Column(db.Float)
    soil_moisture_std = db.Column(db.Float)

    humidity_mean = db.Column(db.Float)
    humidity_std = db.Column(db.Float)

    rain_mm_week_mean = db.Column(db.Float)
    rain_mm_week_std = db.Column(db.Float)

    ppfd_mean = db.Column(db.Float)
    ppfd_std = db.Column(db.Float)

    co2_mean = db.Column(db.Float)
    co2_std = db.Column(db.Float)

    robot_zones = db.relationship(
        "RobotZone",
        back_populates="plant_profile"
    )

    def __repr__(self):
        return f"<PlantProfile {self.display_name} ({self.key})>"


# ==========================================================
# User  ✅ PASSWORD VERWIJDERD
# ==========================================================
class User(db.Model):
    __tablename__ = "user"

    uemail = db.Column(db.String, primary_key=True)
    uname = db.Column(db.String, nullable=False)
    phone = db.Column(db.String)
    adress = db.Column(db.String)

    gardens = db.relationship(
        "Garden",
        backref="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<User {self.uemail}>"


# ==========================================================
# Garden
# ==========================================================
class Garden(db.Model):
    __tablename__ = "garden"

    garden_id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    garden_name = db.Column(db.String, nullable=False)
    adress_garden = db.Column(db.String)
    area_garden = db.Column(db.Numeric)

    user_email = db.Column(
        db.String,
        db.ForeignKey("user.uemail", ondelete="CASCADE"),
    )

    robot_zones = db.relationship(
        "RobotZone",
        backref="garden",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Garden {self.garden_name} ({self.garden_id})>"


# ==========================================================
# Robot Zone (playfield)
# ==========================================================
class RobotZone(db.Model):
    __tablename__ = "robot_zone"

    serial_number = db.Column(db.String, primary_key=True)
    area_playfield = db.Column(db.Numeric)
    robot_name = db.Column(db.String)

    garden_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("garden.garden_id", ondelete="CASCADE"),
    )

    # ⚠️ BELANGRIJK: deze kolom MOET bestaan in Supabase
    plant_name = db.Column(
        db.BigInteger,
        db.ForeignKey("plant_profiles.id", ondelete="SET NULL"),
        nullable=True,
    )

    plant_profile = db.relationship(
        "PlantProfile",
        back_populates="robot_zones",
    )

    sensors = db.relationship(
        "Sensor",
        backref="robot_zone",
        cascade="all, delete-orphan",
    )

    feedback = db.relationship(
        "Feedback",
        backref="robot_zone",
        cascade="all, delete-orphan",
    )

    health_scores = db.relationship(
        "HealthScore",
        backref="robot_zone",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<RobotZone {self.serial_number} ({self.robot_name})>"


# ==========================================================
# Sensor
# ==========================================================
class Sensor(db.Model):
    __tablename__ = "sensor"

    srnr_sensor = db.Column(db.String, primary_key=True)
    sensor_type = db.Column(db.String, nullable=False)
    unit = db.Column(db.String)

    serial_number = db.Column(
        db.String,
        db.ForeignKey("robot_zone.serial_number", ondelete="CASCADE"),
    )

    measurements = db.relationship(
        "Measurement",
        backref="sensor",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Sensor {self.srnr_sensor} ({self.sensor_type})>"


# ==========================================================
# Measurement
# ==========================================================
class Measurement(db.Model):
    __tablename__ = "measurement"

    mid = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    value = db.Column(db.Numeric, nullable=False)
    time_m = db.Column(db.DateTime(timezone=True))

    srnr_sensor = db.Column(
        db.String,
        db.ForeignKey("sensor.srnr_sensor", ondelete="CASCADE"),
    )

    def __repr__(self):
        return f"<Measurement {self.mid} sensor={self.srnr_sensor}>"


# ==========================================================
# Feedback
# ==========================================================
class Feedback(db.Model):
    __tablename__ = "feedback"

    fid = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    f_text = db.Column(db.String, nullable=False)

    serial_number = db.Column(
        db.String,
        db.ForeignKey("robot_zone.serial_number", ondelete="CASCADE"),
    )

    def __repr__(self):
        return f"<Feedback {self.fid} for {self.serial_number}>"


# ==========================================================
# HealthScore
# ==========================================================
class HealthScore(db.Model):
    __tablename__ = "health_score"

    hid = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    score = db.Column(db.Float, nullable=False)
    score_date = db.Column(db.Date, nullable=False)
    calculated_at = db.Column(db.DateTime(timezone=True), nullable=False)

    serial_number = db.Column(
        db.String,
        db.ForeignKey("robot_zone.serial_number", ondelete="CASCADE"),
    )

    def __repr__(self):
        return f"<HealthScore {self.serial_number} {self.score_date}: {self.score}>"
