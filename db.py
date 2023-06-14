from datetime import datetime
import peewee


db = peewee.SqliteDatabase("devices.db")


class Device(peewee.Model):
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
    # insert a device into the database
    device = Device(ip=ip, hostname=hostname, device_type=device_type)
    device.save()


def list_all_ips():
    # list all the IPs with device IDs in the database
    device = []
    device_id = []
    for device_ip in Device.select():
        device.append(device_ip.ip)
        device_id.append(device_ip.id)
    return device, device_id


def list_all_ips_with_type():
    # list all the IPs in the database
    device = []
    device_type = []
    for device_ip in Device.select():
        device.append(device_ip.ip)
        device_type.append(device_ip.device_type)
    return device, device_type


def delete_device(id):
    # delete record by id
    device = Device.delete_by_id(id)
    return device


# insert_device("10.192.0.200", "R1", "hp_procurve")
# list_all_ips()
# delete_device(2)
