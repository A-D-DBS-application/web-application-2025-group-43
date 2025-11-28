# app/models.py
from datetime import datetime
import uuid

from sqlalchemy.dialects.postgresql import UUID
from . import db


# ==========================================================
# User
# ==========================================================
class User(db.Model):
    __tablename__ = "user"

    # Basisgegevens
    uemail = db.Column(db.String, primary_key=True)
    uname = db.Column(db.String, nullable=False)
    phone = db.Column(db.String)
    adress = db.Column(db.String)
    password = db.Column(db.String, nullable=False)

    # Relaties
    gardens = db.relationship(
        "Garden",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<User {self.uemail} ({self.uname})>"


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

    # eigenaar
    user_email = db.Column(
        db.String,
        db.ForeignKey("user.uemail", ondelete="CASCADE"),
    )

    # relaties
    user = db.relationship("User", back_populates="gardens")
    robot_zones = db.relationship(
        "RobotZone",
        back_populates="garden",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Garden {self.garden_name} ({self.garden_id})>"


# ==========================================================
# Robot Zone (= Playfield)
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

    # relaties
    garden = db.relationship("Garden", back_populates="robot_zones")
    sensors = db.relationship(
        "Sensor",
        back_populates="robot_zone",
        cascade="all, delete-orphan",
    )
    feedback = db.relationship(
        "Feedback",
        back_populates="robot_zone",
        cascade="all, delete-orphan",
    )
    conclusions = db.relationship(
        "Conclusion",
        back_populates="robot_zone",
        cascade="all, delete-orphan",
    )

    @property
    def display_name(self) -> str:
        """Handige naam voor in de UI."""
        return self.robot_name or self.serial_number

    def __repr__(self) -> str:
        return f"<RobotZone {self.serial_number} ({self.robot_name})>"


# ==========================================================
# Sensor
# ==========================================================
class Sensor(db.Model):
    __tablename__ = "sensor"

    srnr_sensor = db.Column(db.String, primary_key=True)
    sensor_type = db.Column(db.String, nullable=False)  # bv. 'moisture', 'temperature', ...
    unit = db.Column(db.String)

    serial_number = db.Column(
        db.String,
        db.ForeignKey("robot_zone.serial_number", ondelete="CASCADE"),
    )

    # relaties
    robot_zone = db.relationship("RobotZone", back_populates="sensors")
    measurements = db.relationship(
        "Measurement",
        back_populates="sensor",
        cascade="all, delete-orphan",
        order_by="Measurement.time_m.desc()",  # nieuwste eerst
    )

    @property
    def latest_measurement(self):
        """Laatste meting, of None als er nog niks is."""
        if not self.measurements:
            return None
        return self.measurements[0]

    def __repr__(self) -> str:
        return f"<Sensor {self.srnr_sensor} ({self.sensor_type})>"


# ==========================================================
# Measurement
# ==========================================================
class Measurement(db.Model):
    __tablename__ = "measurement"

    mid = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    value = db.Column(db.Numeric, nullable=False)
    time_m = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)

    srnr_sensor = db.Column(
        db.String,
        db.ForeignKey("sensor.srnr_sensor", ondelete="CASCADE"),
    )

    # relatie
    sensor = db.relationship("Sensor", back_populates="measurements")

    def __repr__(self) -> str:
        return f"<Measurement {self.mid} sensor={self.srnr_sensor} value={self.value}>"


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

    robot_zone = db.relationship("RobotZone", back_populates="feedback")

    def __repr__(self) -> str:
        return f"<Feedback {self.fid} robot={self.serial_number}>"


# ==========================================================
# Conclusion (health score per robot_zone)
# ==========================================================
class Conclusion(db.Model):
    __tablename__ = "conclusion"

    cid = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    concl_score = db.Column(db.Numeric)  # bv. 0–100 health score
    calc_time = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)

    serial_number = db.Column(
        db.String,
        db.ForeignKey("robot_zone.serial_number", ondelete="CASCADE"),
    )

    robot_zone = db.relationship("RobotZone", back_populates="conclusions")

    def __repr__(self) -> str:
        return f"<Conclusion {self.cid} robot={self.serial_number} score={self.concl_score}>"
