# get_hostname.py

import my_secrets


def get_hostname(device_ip, device_type):
    """
    Get the hostname of a device.

    Args:
        device_ip: The IP address of the device.
        device_type: The type of device.

    Returns:
        hostname: The hostname of the device in a string.
    """

    # Import module named device_type, pass device type to get_running_config, return to string
    hostname = __import__(f"vendors.{device_type}", fromlist=[""]).get_hostname(
        my_secrets.USERNAME, my_secrets.PASSWORD, device_ip, device_type
    )

    # Return hostname
    return hostname
