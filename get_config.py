import netmiko


def get_config(device_username, device_password):
    # Define the device parameters
    device_ip = "10.192.0.1"
    device_type = "hp_procurve"

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
    return config, device_ip
