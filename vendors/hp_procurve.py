import netmiko


def get_running_config(
    action, device_username, device_password, device_ip, device_type
):
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

    match action:
        case "get-running-config":  # get running config for hp_procurve
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

        case _:  # default
            return ""  # default
