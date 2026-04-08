# db.py

from datetime import datetime
from sqlalchemy import create_engine, String, Integer, Column, DateTime, or_, ForeignKey, Text
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
import sqlalchemy.exc

import os

# Create a new database engine, in this case, a sqlite database
db_path = os.getenv("DATABASE_URL", "sqlite:///devices.db")
engine = create_engine(db_path)
# Create a new table with a name, count, amount, and valid column
Base = declarative_base()

class Settings(Base):
    """
    Table to store global settings.
    """
    __tablename__ = "settings"
    key = Column(String, primary_key=True)
    value = Column(String, nullable=False)


class Logs(Base):
    """
    Table to store backend application logs.
    """
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.now)
    level = Column(String, nullable=False)
    message = Column(String, nullable=False)
    details = Column(Text, nullable=True)

class ScanJobs(Base):
    """
    Table to store network scan job states.
    """
    __tablename__ = "scan_jobs"
    id = Column(Integer, primary_key=True)
    cidr = Column(String, nullable=False)
    status = Column(String, nullable=False, default="RUNNING")
    message = Column(String, nullable=True)
    detailed_log = Column(Text, default="")
    progress_current = Column(Integer, default=0)
    progress_total = Column(Integer, default=0)
    started_at = Column(DateTime, default=datetime.now)
    completed_at = Column(DateTime, nullable=True)


class FetchJobs(Base):
    """
    Table to store config fetch job states.
    """
    __tablename__ = "fetch_jobs"
    id = Column(Integer, primary_key=True)
    status = Column(String, nullable=False, default="RUNNING")
    message = Column(String, nullable=True)
    detailed_log = Column(Text, default="")
    progress_current = Column(Integer, default=0)
    progress_total = Column(Integer, default=0)
    started_at = Column(DateTime, default=datetime.now)
    completed_at = Column(DateTime, nullable=True)


class ConfigVersions(Base):
    """
    Table to store configuration versions for devices.
    """
    __tablename__ = "config_versions"
    id = Column(Integer, primary_key=True)
    device_id = Column(Integer, ForeignKey("devices.id", ondelete="CASCADE"), nullable=False)
    config_text = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.now)

    device = relationship("Devices", back_populates="configs")


class Devices(Base):
    """
    The Devices class is a table that stores information about devices.

    Attributes:
        id: The id of the device.
        ip: The IP address of the device.
        hostname: The hostname of the device.
        device_type: The device type.
        date_updated: The date the device was updated.
    """

    __tablename__ = "devices"
    id = Column(Integer, primary_key=True)
    ip = Column(String, unique=True, nullable=False)
    hostname = Column(String, nullable=False)
    device_type = Column(String, nullable=False)
    date_updated = Column(DateTime, default=datetime.now(), onupdate=datetime.now())
    username = Column(String)
    password = Column(String)
    enable_password = Column(String)

    configs = relationship("ConfigVersions", back_populates="device", cascade="all, delete-orphan")


# Create a session to use the tables, bound to above engine
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Create a session for backwards compatibility with existing CLI
session = SessionLocal()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def insert_device(ip, hostname, device_type, username, password, enable_password):
    """
    Insert a device into the database.

    Args:
        ip: The IP address of the device.
        hostname: The hostname of the device.
        device_type: The device type.
        username: The username to authenticate with.
        password: The password to authenticate with.
        enable_password: The enable password to authenticate with.

    Returns:
        Boolean: True if the device was added, False if the device already exists.
    """

    try:
        device = Devices(
            ip=ip,
            hostname=hostname,
            device_type=device_type,
            username=username,
            password=password,
            enable_password=enable_password,
        )
        session.add(device)
        session.commit()
    except sqlalchemy.exc.IntegrityError:
        return False
    else:
        return True


def insert_device_bulk(devices_object):
    """
    Insert multiple device into the database.

    Args:
        devices_object: an object containing the devices to be added.

    Returns:
        None
    """

    final_list = []
    print("Checking for duplicate devices in the database ...")
    for xx in devices_object:
        xx = Devices(
            ip=xx.ip,
            hostname=xx.hostname,
            device_type=xx.device_type,
            username=xx.username,
            password=xx.password,
            enable_password=xx.enable_password,
        )
        final_list.append(xx)

    print("Adding devices to the database.")
    session.add_all(final_list)
    # Commit the changes
    session.commit()


def list_all_ips_with_type():
    """
    List all the IPs in the database with their device types.

    Returns:
        devices[]: A list of all the IPs in the database with their device types.
    """

    devices = session.query(Devices).all()
    return devices


def remove_device(device_id):
    """
    Remove a device from the database.

    Args:
        device_id: The id of the device to remove.

    Returns:
        Boolean: True if the device was removed, False if the device was not found.
    """

    try:
        device = session.query(Devices).filter(Devices.id == device_id).one()
        session.delete(device)
        session.commit()
    except sqlalchemy.exc.NoResultFound:
        return False
    else:
        return True


def is_device_in_db(ip):
    """
    Check if a device is in the database.

    Args:
        ip: The IP of the device to check.

    Returns:
        Boolean: True if the device is in the database, False if the device is not in the database.
    """

    device = session.query(Devices).filter(Devices.ip == ip).one_or_none()

    if device is None:
        return False
    else:
        return True


def search(search_string):
    """
    Search for a device in the database.

    Args:
        search_string: The string to search for.

    Returns:
        devices[]: A list of all the devices in the database.
    """

    devices = (
        session.query(Devices)
        .filter(
            or_(
                Devices.ip.like(f"%{search_string}%"),
                Devices.hostname.like(f"%{search_string}%"),
                Devices.device_type.like(f"%{search_string}%"),
            )
        )
        .all()
    )

    return devices
