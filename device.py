import my_secrets
import get_config
import re
from netmiko import SSHDetect, ConnectHandler
from getpass import getpass

def detect_device(ip):
    """

    Args:
        ip: IP of the device to detect.

    Returns:
        best_match: The best match for the device type.
    """
    
    device = {
        "device_type": "autodetect",
        "host": ip,
        "username": my_secrets.USERNAME,
        "password": my_secrets.PASSWORD,
    }

    guesser = SSHDetect(**device)
    best_match = guesser.autodetect()

    return best_match

def get_hostname(device_ip, device_type):
    """_summary_

    Args:
        ip: The IP of the device.

    Returns:
        hostname: The hostname of the device.
    """
    config = get_config.get_config(device_username=my_secrets.USERNAME, device_password=my_secrets.PASSWORD, device_ip=device_ip, device_type=device_type)
    hostname = re.search(r"hostname (\S+)", config).group(1).replace("\"", "")
    
    return hostname