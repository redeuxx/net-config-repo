# utils.py

import os
import conf
import getpass
import db


def del_oldest_configs(amount=None, db_session=None):
    """
    Deletes the oldest configs in the database if they exceed the maximum allowed amount.

    Args:
        amount: Number of configs to keep. If None, retrieves from Settings table.
        db_session: Optional database session.

    Returns:
        None
    """
    close_session = False
    if db_session is None:
        db_session = db.SessionLocal()
        close_session = True

    try:
        if amount is None:
            setting = db_session.query(db.Settings).filter_by(key="max_configs_per_device").first()
            amount = int(setting.value) if setting else conf.MAX_CONFIGS

        devices = db_session.query(db.Devices).all()
        for device in devices:
            # Get all configs for device ordered by timestamp descending
            configs = db_session.query(db.ConfigVersions).filter_by(device_id=device.id).order_by(db.ConfigVersions.timestamp.desc()).all()
            
            if len(configs) > amount:
                # Delete configs beyond the maximum amount
                configs_to_delete = configs[amount:]
                for config in configs_to_delete:
                    print(f"Removing config {config.id} for device {device.ip}.")
                    db_session.delete(config)
        
        db_session.commit()
    finally:
        if close_session:
            db_session.close()


def log_message(db_session, level, message, details=""):
    """
    Save a log message to the database.
    """
    try:
        new_log = db.Logs(level=level, message=message, details=details)
        db_session.add(new_log)
        db_session.commit()
    except Exception as e:
        print(f"Failed to log message: {e}")

def get_credentials(db_session=None):
    """
    Get user input for username, password and enable password.
    If db_session is provided, read from Settings table instead to prevent blocking the web server.

    Args:
        db_session: Optional database session.

    Returns:
        A dictionary with the username, password and enable password.
    """
    if db_session:
        setting_user = db_session.query(db.Settings).filter_by(key="default_username").first()
        setting_pass = db_session.query(db.Settings).filter_by(key="default_password").first()
        setting_en = db_session.query(db.Settings).filter_by(key="default_enable_password").first()

        return {
            "username": setting_user.value if setting_user else "",
            "password": setting_pass.value if setting_pass else "",
            "enable_password": setting_en.value if setting_en else "",
        }

    username = input("Enter the username to authenticate with: ")
    password = getpass.getpass("Enter the password to authenticate with: ")
    enable_password = getpass.getpass(
        "Enter the enable password to authenticate with \n(Press Enter if it is the same as previous password): "
    )

    return {
        "username": username,
        "password": password,
        "enable_password": enable_password,
    }

