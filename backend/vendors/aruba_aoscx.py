import re
import netmiko
import get_config

def get_running_config(
    device_username, device_password, device_ip, device_type, enable_password
):
    """
    Get the command to get the running config.

    Args:
        device_username: The username to authenticate with.
        device_password: The password to authenticate with.
        device_ip: The IP address of the device.
        device_type: The device parameters.
        enable_password: The enable password to authenticate with.

    Returns:
        String: The running configuration of the device.
        String: The error message if the device could not be connected to.
    """

    try:
        device = {
            "device_type": device_type,
            "host": device_ip,
            "username": device_username,
            "password": device_password,
            # wait a little longer for the device to respond
            "fast_cli": False,
            "global_delay_factor": 2,
            "secret": enable_password,
        }

        with netmiko.ConnectHandler(**device) as connection:
            # Get the running configuration
            config = connection.send_command("show running-config")

        # Close the connection
        connection.disconnect()

        # Return the configuration
        return config
    except Exception as e:
        return (
            f"Error: Could not connect to {device_ip} with the following error: \n{e}"
        )


def get_hostname(
    device_username, device_password, device_ip, device_type, enable_password
):
    """
    Get the hostname of a device.

    Args:
        device_username: The username to authenticate with.
        device_password: The password to authenticate with.
        device_ip: The IP address of the device.
        device_type: The device parameters.
        enable_password: The enable password to authenticate with.

    Returns:
        String: The hostname of the device.
    """
    # Get the running configuration
    config = get_config.get_config(
        device_username, device_password, device_ip, device_type, enable_password
    )

    # Get the hostname
    hostname = re.search(r"hostname (\S+)", config).group(1).replace('"', "")

    # Return the hostname
    return hostname
