# device.py

import my_secrets
from netmiko import SSHDetect, exceptions


def detect_device(ip):
    """
    Get device type

    Args:
        ip: IP of the device to detect.

    Returns:
        best_match: The best match for the device type.
    """

    try:
        device = {
            "device_type": "autodetect",
            "host": ip,
            "username": my_secrets.USERNAME,
            "password": my_secrets.PASSWORD,
            "global_delay_factor": 4,
            "banner_timeout": 1000,
            "conn_timeout": 1000,
        }

        guesser = SSHDetect(**device)
        best_match = guesser.autodetect()

        return best_match
    except exceptions.NetmikoAuthenticationException as e:
        return False
