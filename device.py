# device.py

from netmiko import SSHDetect, exceptions


def detect_device(ip, username, password, enable_password):
    """
    Get device type

    Args:
        ip: IP of the device to detect.
        username: Username to authenticate with.
        password: Password to authenticate with.
        enable_password: Enable password to authenticate with.

    Returns:
        best_match: The best match for the device type.
    """

    try:
        device = {
            "device_type": "autodetect",
            "host": ip,
            "username": username,
            "password": password,
            "global_delay_factor": 4,
            "banner_timeout": 1000,
            "conn_timeout": 1000,
            "secret": enable_password,
        }

        guesser = SSHDetect(**device)
        best_match = guesser.autodetect()

        return best_match
    except exceptions.NetmikoAuthenticationException as e:
        return False
