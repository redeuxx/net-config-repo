# get_config.py

from datetime import date, datetime
import db


def get_config(
    device_username, device_password, device_ip, device_type, enable_password
):
    """
    Get the running configuration of a device.

    Args:
        device_username: The username to authenticate with.
        device_password: The password to authenticate with.
        device_ip: The IP address of the device.
        device_type: The device parameters.
        enable_password: The enable password to authenticate with.

    Returns:
        The configuration of the device.
    """

    # Import module named device_type, pass device type to get_running_config, return to string
    config = __import__(f"vendors.{device_type}", fromlist=[""]).get_running_config(
        device_username,
        device_password,
        device_ip,
        device_type,
        enable_password,
    )

    return config


import concurrent.futures
import threading
import time
import utils

def fetch_all_configs(db_session=None):
    """
    Fetch the running configuration of all devices in the database and save them to the database concurrently.
    """
    close_session = False
    if db_session is None:
        db_session = db.SessionLocal()
        close_session = True

    db_lock = threading.Lock()

    try:
        devices = db_session.query(db.Devices).all()
        
        def fetch_host_config(device):
            print(f"Fetching config for {device.ip} ...")
            
            config = "Error: Connection failed"
            # Initial attempt + 10 retries
            for attempt in range(11):
                config = get_config(
                    device.username,
                    device.password,
                    device.ip,
                    device.device_type,
                    device.enable_password,
                )
                if "Error:" not in config:
                    break
                if attempt < 10:
                    print(f"Attempt {attempt + 1}/11 failed for {device.ip}. Retrying...")
                    time.sleep(1)

            if "Error:" not in config:
                new_config = db.ConfigVersions(
                    device_id=device.id,
                    config_text=config.strip()
                )
                with db_lock:
                    db_session.add(new_config)
            else:
                with db_lock:
                    print(config.strip())
                    utils.log_message(db_session, "ERROR", f"Config fetch failed for {device.ip}", config.strip())

        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            executor.map(fetch_host_config, devices)
            
        db_session.commit()
    finally:
        if close_session:
            db_session.close()
