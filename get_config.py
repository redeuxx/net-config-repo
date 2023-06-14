from datetime import date, datetime
import os
import netmiko
import my_secrets
import conf
import db


def get_config(device_username, device_password, device_ip, device_type):
    # Define the device parameters
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
    return config


def fetch_all_configs():
    # get all IPs from the database and fetch all configs
    for device_ip, device_type in zip(
        db.list_all_ips_with_type()[0], db.list_all_ips_with_type()[1]
    ):
        config = get_config(
            my_secrets.USERNAME, my_secrets.PASSWORD, device_ip, device_type
        )
        print(f"Fetching config for {device_ip}...")
        now = datetime.now()
        filename = (
            str(date.today())
            + "_"
            + now.strftime("%H-%M-%S")
            + "_"
            + device_ip
            + ".txt"
        )
        dir_complete_path_1 = os.path.abspath(conf.STORE_DIR)
        device_complete_path = os.path.join(dir_complete_path_1, device_ip)
        file_complete_path = os.path.abspath(
            os.path.join(device_complete_path, filename)
        )

        # Check if /running-configs dir exists, if not, create it
        if not os.path.exists(dir_complete_path_1):
            os.mkdir(dir_complete_path_1)

        # Check if device dir exists, if not, create it
        if not os.path.exists(device_complete_path):
            os.mkdir(device_complete_path)

        # Write the configuration to a file
        with open(file_complete_path, "w", encoding="utf-8") as f_config:
            f_config.write(config)
