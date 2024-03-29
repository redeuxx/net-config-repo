# db.py

from datetime import datetime
from sqlalchemy import create_engine, String, Integer, Column, DateTime, or_
from sqlalchemy.orm import declarative_base, sessionmaker
import sqlalchemy.exc

# Create a new database engine, in this case, a sqlite database
engine = create_engine("sqlite:///devices.db")
# Create a new table with a name, count, amount, and valid column
Base = declarative_base()


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


# Create the table
Base.metadata.create_all(engine)
# Create a session to use the tables, bound to above engine
Session = sessionmaker(bind=engine)
# Create a session
session = Session()


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
