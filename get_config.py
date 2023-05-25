import netmiko


def get_config(device_username):
    # Define the device parameters
    device_ip = "10.192.0.200"
    device_username = device_username
    device_password = "security"
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

    print(config)

    # Write the configuration to a file
    with open("running-configs/" + device_ip + ".txt", "w", encoding="utf-8") as f:
        f.write(config)

    # Close the connection
    connection.disconnect()
