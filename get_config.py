# get_config.py

from datetime import date, datetime
from pathlib import Path
import my_secrets
import conf
import db


def get_config(device_username, device_password, device_ip, device_type):
    """
    Get the running configuration of a device.

    Args:
        device_username: The username to authenticate with.
        device_password: The password to authenticate with.
        device_ip: The IP address of the device.
        device_type: The device parameters.

    Returns:
        The configuration of the device.
    """

    # Set module_name to device_type
    module_name = device_type

    # Import module named device_type, pass device type to get_running_config, return to string
    config = __import__(f"vendors.{module_name}", fromlist=[""]).get_running_config(
        device_username, device_password, device_ip, device_type
    )

    # Return the configuration or error
    return config


def fetch_all_configs():
    """
    Fetch the running configuration of all devices in the database and write them to a file.

    Args:
        No arguments.

    Returns:
        Does not return anything.
    """

    for device in db.list_all_ips_with_type():
        config = get_config(
            my_secrets.USERNAME, my_secrets.PASSWORD, device.ip, device.device_type
        )

        print(f"Fetching config for {device.ip} ...")

        if "Error:" not in config:
            now = datetime.now()
            filename = (
                str(date.today())
                + "_"
                + now.strftime("%H-%M-%S")
                + "_"
                + device.ip
                + ".txt"
            )

            device_complete_path = Path(conf.STORE_DIR / device.ip)
            device_complete_path_filename = Path(device_complete_path / filename)

            # Check if conf.STORE_DIR exists, if not, create it
            if not Path(conf.STORE_DIR).is_dir():
                Path(conf.STORE_DIR).mkdir()

            # Check if device dir exists, if not, create it
            if not Path(device_complete_path).is_dir():
                Path(device_complete_path).mkdir()

            # Write the configuration to a file
            with open(device_complete_path_filename, "w", encoding="utf-8") as f_config:
                f_config.write(config.strip())
        else:
            print(config.strip())
