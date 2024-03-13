# get_hostname.py

import my_secrets


def get_hostname(device_ip, device_type, username, password, enable_password):
    """
    Get the hostname of a device.

    Args:
        device_ip: The IP address of the device.
        device_type: The type of device.
        username: The username to authenticate with.
        password: The password to authenticate with.
        enable_password: The enable password to authenticate with.

    Returns:
        hostname: The hostname of the device in a string.
    """

    # Import module named device_type, pass device type to get_running_config, return to string
    hostname = __import__(f"vendors.{device_type}", fromlist=[""]).get_hostname(
        username, password, device_ip, device_type, enable_password
    )

    # Return hostname
    return hostname
