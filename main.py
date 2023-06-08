# Description: This script will connect to a device and get the configuration
from datetime import date
import os
import get_config
import my_secrets
import conf


def main():
    config, device_ip = get_config.get_config(my_secrets.USERNAME, my_secrets.PASSWORD)
    print(config)
    filename = str(date.today()) + "_" + device_ip + ".txt"
    dir_complete_path_1 = os.path.abspath(conf.STORE_DIR)
    device_complete_path = os.path.join(dir_complete_path_1, device_ip)
    file_complete_path = os.path.abspath(os.path.join(device_complete_path, filename))

    # Check if /running-configs dir exists, if not, create it
    if not os.path.exists(dir_complete_path_1):
        os.mkdir(dir_complete_path_1)

    # Check if device dir exists, if not, create it
    if not os.path.exists(device_complete_path):
        os.mkdir(device_complete_path)

    # Write the configuration to a file
    with open(file_complete_path, "w", encoding="utf-8") as f_config:
        f_config.write(config)


if __name__ == "__main__":
    main()
