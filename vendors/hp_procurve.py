import netmiko
import get_config
import re


def get_running_config(device_username, device_password, device_ip, device_type):
    """
    Get the command to get the running config.

    Args:
        action: The action to perform.
        username: The username to authenticate with.
        password: The password to authenticate with.
        device_ip: The IP address of the device.
        device_type: The device parameters.

    Returns:
        The running configuration of the device.

    """

    # Create a connection object
    connection = netmiko.ConnectHandler(
        ip=device_ip,
        username=device_username,
        password=device_password,
        device_type=device_type,
    )

    # Get the running configuration
    config = connection.send_command("show running-config")

    # Close the connection
    connection.disconnect()

    # Return the configuration
    return config


def get_hostname(device_username, device_password, device_ip, device_type):
    """
    Get the hostname of a device.

    Args:
        username: The username to authenticate with.
        password: The password to authenticate with.
        device_ip: The IP address of the device.
        device_type: The device parameters.

    Returns:
        The hostname of the device.
    """
    # Get the running configuration
    config = get_config.get_config(
        device_username, device_password, device_ip, device_type
    )

    # Get the hostname
    hostname = re.search(r"hostname (\S+)", config).group(1).replace('"', "")

    # Return the hostname
    return hostname
