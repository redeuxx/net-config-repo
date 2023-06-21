from datetime import date, datetime
import os
import my_secrets
import conf
import db


def get_config(device_username, device_password, device_ip, device_type):
    """
    Get the running configuration of a device.

    Args:
        username: The username to authenticate with.
        password: The password to authenticate with.
        device_ip: The IP address of the device.
        device_type: The device parameters.

    Returns:
        The configuration of the device.
    """
    # Set module_name to device_type
    module_name = device_type

    # Import module named device_type, pass device type to get_running_config, return to string
    config = __import__(f"vendors.{module_name}", fromlist=[""]).get_running_config(
        "get-running-config", device_username, device_password, device_ip, device_type
    )

    return config


def fetch_all_configs():
    """
    Fetch the running configuration of all devices in the database and write them to a file.

    Args:
        None

    Returns:
        None
    """
    for device_ip, device_type in zip(
        db.list_all_ips_with_type()[0], db.list_all_ips_with_type()[1]
    ):
        config = get_config(
            my_secrets.USERNAME, my_secrets.PASSWORD, device_ip, device_type
        )
        print(f"Fetching config for {device_ip} ...")
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
