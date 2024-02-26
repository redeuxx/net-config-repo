import my_secrets
from netmiko import SSHDetect


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
