from datetime import datetime
import peewee


db = peewee.SqliteDatabase("devices.db")


class Device(peewee.Model):
    """
    Database model for devices.

    Args:
        peewee.Model: The base model class that other models will inherit from.

    Returns:
        None
    """

    id = peewee.IntegerField(primary_key=True)
    ip = peewee.IPField()
    hostname = peewee.TextField()
    date_added = peewee.DateTimeField(default=datetime.now)
    device_type = peewee.CharField()

    class Meta:
        database = db  # This model uses the "devices.db" database.


db.connect()
db.create_tables([Device])


def insert_device(ip, hostname, device_type):
    """
    Insert a device into the database.

    Args:
        ip: The IP address of the device.
        hostname: The hostname of the device.
        device_type: The device type.

    Returns:
        None
    """

    device = Device(ip=ip, hostname=hostname, device_type=device_type)
    device.save()


def list_all_ips():
    """
    List all the IPs in the database.

    Args:
        None

    Returns:
        A list of all the IPs in the database with their device IDs.
    """

    device = []
    device_id = []
    for device_ip in Device.select():
        device.append(device_ip.ip)
        device_id.append(device_ip.id)
    return device, device_id


def list_all_ips_with_type():
    """
    List all the IPs in the database with their device types.

    Args:
        None


    Returns:
        A list of all the IPs in the database with their device types.
    """

    device = []
    device_type = []
    for device_ip in Device.select():
        device.append(device_ip.ip)
        device_type.append(device_ip.device_type)
    return device, device_type


def delete_device(id):
    """
    Delete a device from the database.

    Args:
        id: The ID of the device.

    Returns:
        1 if the device was deleted, 0 if the device was not deleted.
    """
    device = Device.delete_by_id(id)
    return device
