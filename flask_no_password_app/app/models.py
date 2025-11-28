from .config import db
from sqlalchemy.dialects.postgresql import UUID
import uuid

# ==========================================================
# User
# ==========================================================
class User(db.Model):
    __tablename__ = "user"

    uemail = db.Column(db.String, primary_key=True)
    uname = db.Column(db.String, nullable=False)
    phone = db.Column(db.String)
    adress = db.Column(db.String)
    password = db.Column(db.String, nullable=False)

    gardens = db.relationship("Garden", backref="user", cascade="all, delete-orphan")


# ==========================================================
# Garden
# ==========================================================
class Garden(db.Model):
    __tablename__ = "garden"

    garden_id = db.Column(UUID(as_uuid=True),
                          primary_key=True,
                          default=uuid.uuid4)
    garden_name = db.Column(db.String, nullable=False)
    adress_garden = db.Column(db.String)
    area_garden = db.Column(db.Numeric)
    user_email = db.Column(db.String, db.ForeignKey("user.uemail", ondelete="CASCADE"))

    robot_zones = db.relationship("RobotZone", backref="garden", cascade="all, delete-orphan")


# ==========================================================
# Robot Zone
# ==========================================================
class RobotZone(db.Model):
    __tablename__ = "robot_zone"

    serial_number = db.Column(db.String, primary_key=True)
    area_playfield = db.Column(db.Numeric)
    robot_name = db.Column(db.String)
    garden_id = db.Column(UUID(as_uuid=True), db.ForeignKey("garden.garden_id", ondelete="CASCADE"))

    sensors = db.relationship("Sensor", backref="robot_zone", cascade="all, delete-orphan")
    feedback = db.relationship("Feedback", backref="robot_zone", cascade="all, delete-orphan")
    conclusions = db.relationship("Conclusion", backref="robot_zone", cascade="all, delete-orphan")


# ==========================================================
# Sensor
# ==========================================================
class Sensor(db.Model):
    __tablename__ = "sensor"

    srnr_sensor = db.Column(db.String, primary_key=True)
    sensor_type = db.Column(db.String, nullable=False)
    unit = db.Column(db.String)
    serial_number = db.Column(db.String, db.ForeignKey("robot_zone.serial_number", ondelete="CASCADE"))

    measurements = db.relationship("Measurement", backref="sensor", cascade="all, delete-orphan")


# ==========================================================
# Measurement
# ==========================================================
class Measurement(db.Model):
    __tablename__ = "measurement"

    mid = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    value = db.Column(db.Numeric, nullable=False)
    time_m = db.Column(db.DateTime(timezone=True))

    srnr_sensor = db.Column(db.String, db.ForeignKey("sensor.srnr_sensor", ondelete="CASCADE"))


# ==========================================================
# Feedback
# ==========================================================
class Feedback(db.Model):
    __tablename__ = "feedback"

    fid = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    f_text = db.Column(db.String, nullable=False)
    serial_number = db.Column(db.String, db.ForeignKey("robot_zone.serial_number", ondelete="CASCADE"))


# ==========================================================
# Conclusion
# ==========================================================
class Conclusion(db.Model):
    __tablename__ = "conclusion"

    cid = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    concl_score = db.Column(db.Numeric)
    calc_time = db.Column(db.DateTime(timezone=True))
    serial_number = db.Column(db.String, db.ForeignKey("robot_zone.serial_number", ondelete="CASCADE"))
