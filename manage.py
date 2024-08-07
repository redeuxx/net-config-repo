# manage.py

import argparse
import db
import get_config
import utils
import conf
import hosts
import device
import get_hostname
import time

start_time = time.perf_counter()


# Class to hold device information to be sent to the db
class Item:
    def __init__(
        self, d_ip, d_hostname, d_type, d_username, d_password, d_enable_password
    ):
        self.ip = d_ip
        self.hostname = d_hostname
        self.device_type = d_type
        self.username = d_username
        self.password = d_password
        self.enable_password = d_enable_password


# initialize the parser
parser = argparse.ArgumentParser(
    usage="manage.py [options]", description="Switch management tool."
)
parser.version = conf.VERSION

# You must choose one of the mutually exclusive options.
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument(
    "--scan", help="Scan an IP address or CIDR for hosts that are alive."
)
group.add_argument(
    "--list", action="store_true", help="List all devices in the database."
)
group.add_argument("--add", help="Add a device to the database.")
group.add_argument(
    "--remove", type=int, help="Delete a device from the database using the device id."
)
group.add_argument(
    "--fetchall", action="store_true", help="Fetch all configs from the database."
)
group.add_argument(
    "--clean", action="store_true", help="Clean up running-configs/ directory."
)
group.add_argument("--search", help="Search for a device in the database.")
# end group

# Optional arguments
parser.add_argument(
    "-add", action="store_true", help="Add discovered device/s to the database."
)
parser.add_argument(
    "-v", "--version", action="version", help="Show the version of the program."
)
parser.add_argument(
    "-skip",
    help="Skip adding device to the database when using the -add flag. Use a comma separated list of IPs.",
)

args = parser.parse_args()

if args.scan:
    credentials = utils.get_credentials()
    username = credentials["username"]
    password = credentials["password"]
    enable_password = credentials["enable_password"]
    alive_hosts = hosts.scan_cidr(args.scan)
    alive_hosts_filtered = []
    alive_hosts_final = []
    if args.add is not None:
        # If -skip flag is used, remove the IPs from the list.
        if args.skip is not None:
            skip_hosts = args.skip.split(",")
            skip_hosts = [value.strip() for value in skip_hosts]
            alive_hosts_filtered = [x for x in alive_hosts if x not in set(skip_hosts)]
        else:
            alive_hosts_filtered = alive_hosts

        # check if device already exists in the database
        for device_ip in alive_hosts_filtered:
            if db.is_device_in_db(device_ip) is False:
                alive_hosts_final.append(device_ip)
            else:
                print(f"Device with ip {device_ip} already exists in the database.")

        devices_object = []

        # get device type and hostname for each device, then add to the database
        if len(alive_hosts_final) != 0:
            if enable_password == "":
                enable_password = password

            for device_ip in alive_hosts_final:
                device_type = device.detect_device(
                    device_ip,
                    username,
                    password,
                    enable_password,
                )
                if device_type is not False:
                    print(f"Detecting {device_ip} device type ...")
                    hostname = get_hostname.get_hostname(
                        device_ip,
                        device_type,
                        username,
                        password,
                        enable_password,
                    )
                    print(f"Getting hostname for {device_ip} ...")
                    single_device = Item(
                        device_ip,
                        hostname,
                        device_type,
                        username,
                        password,
                        enable_password,
                    )
                    devices_object.append(single_device)
                else:
                    print(f"Could not connect to {device_ip}.")
                    continue
            db.insert_device_bulk(devices_object)
        else:
            print("No devices to add to the database.")

elif args.list:
    devices = db.list_all_ips_with_type()
    if len(devices) == 0:
        print("No devices in the database.")
    else:
        print(f"{'ID':^6} | {'IP':^14} | {'Hostname':^27} | {'Device Type':^10}")
        for device in devices:
            print(
                f"{device.id:6} | {device.ip:14} | {device.hostname:27} | {device.device_type:10}"
            )

elif args.add:
    if db.is_device_in_db(args.add) is False:
        credentials = utils.get_credentials()
        username = credentials["username"]
        password = credentials["password"]
        enable_password = credentials["enable_password"]

        if enable_password == "":
            enable_password = password
        if hosts.is_alive(args.add) is True:
            print(f"Detecting {args.add} device type ...")
            device_type = device.detect_device(
                args.add, username, password, enable_password
            )
            if device_type is not False:
                hostname = get_hostname.get_hostname(
                    device_ip=args.add,
                    device_type=device_type,
                    username=username,
                    password=password,
                    enable_password=enable_password,
                )
                print(f"Getting hostname for {args.add} ...")

                if (
                    db.insert_device(
                        args.add,
                        hostname,
                        device_type,
                        username,
                        password,
                        enable_password,
                    )
                    is True
                ):
                    print(f"Device with ip {args.add} has been added to the database.")
                else:
                    print(f"Device with ip {args.add} already exists in the database.")
            else:
                print(f"Could not connect to {args.add}.")
        else:
            print(f"Device with ip {args.add} is not reachable.")
    else:
        print(f"Device with ip {args.add} already exists in the database.")

elif args.remove:
    if db.remove_device(args.remove) is True:
        print(f"Device with id {args.remove} has been removed from the database.")
    else:
        print(f"Device with id {args.remove} does not exist in the database.")

elif args.fetchall:
    get_config.fetch_all_configs()

elif args.search:
    search_results = db.search(args.search)
    if len(search_results) > 0:
        print(f"{'ID':^6} | {'IP':^14} | {'Hostname':^27} | {'Device Type':^10}")
    for device in search_results:
        print(
            f"{device.id:6} | {device.ip:14} | {device.hostname:27} | {device.device_type:10}"
        )
    print(f"{len(search_results)} devices found.")

elif args.clean:
    print("Cleaning up running-configs/ directory.")
    utils.del_oldest_configs(conf.MAX_CONFIGS)

end_time = time.perf_counter()
elapsed_time = end_time - start_time
print("Execution time:", elapsed_time, "seconds")
