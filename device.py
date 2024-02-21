import my_secrets
import get_config
import re
from netmiko import SSHDetect, ConnectHandler
from getpass import getpass


def detect_device(ip):
    """
    Get device type

    Args:
        ip: IP of the device to detect.

    Returns:
        best_match: The best match for the device type.
    """

    device = {
        "device_type": "autodetect",
        "host": ip,
        "username": my_secrets.USERNAME,
        "password": my_secrets.PASSWORD,
        "global_delay_factor": 4,
    }

    guesser = SSHDetect(**device)
    best_match = guesser.autodetect()

    return best_match


def get_hostname(device_ip, device_type):
    """
    Get hostname of device

    Args:
        ip: The IP of the device.

    Returns:
        hostname: The hostname of the device.
    """
    device = {
        "device_type": device_type,
        "host": device_ip,
        "username": my_secrets.USERNAME,
        "password": my_secrets.PASSWORD,
    }
    config = get_config.get_config(
        device_username=my_secrets.USERNAME,
        device_password=my_secrets.PASSWORD,
        device_ip=device_ip,
        device_type=device_type,
    )
    hostname = re.search(r"hostname (\S+)", config).group(1).replace('"', "")

    return hostname
