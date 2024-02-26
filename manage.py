# manage.py

import argparse
import sys
import db
import get_config
import utils
import conf
import hosts
import device
import get_hostname

parser = argparse.ArgumentParser(
    usage="test.py [options]", description="Switch management tool."
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
# end group

# Optional arguments
parser.add_argument("-type", help="Type of device.")
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
    alive_hosts = hosts.scan_cidr(args.scan)
    alive_hosts_filtered = []
    if args.add is not None:
        if args.skip is not None:
            skip_hosts = args.skip.split(",")
            skip_hosts = [value.strip() for value in skip_hosts]
            alive_hosts_filtered = [x for x in alive_hosts if x not in set(skip_hosts)]
        else:
            alive_hosts_filtered = alive_hosts

        for device_ip in alive_hosts_filtered:
            device_type = device.detect_device(device_ip)
            hostname = get_hostname.get_hostname(
                device_ip=device_ip, device_type=device_type
            )
            print(f"Processing {device_ip} ...")
            if (
                db.insert_device(
                    ip=device_ip, hostname=hostname, device_type=device_type
                )
                == 0
            ):
                print(f"{device_ip} already exists in the database.")
            else:
                print(f"{device_ip} has been added to the database.")
elif args.list:
    if (len(db.list_all_ips()[0])) == 0:
        print("No devices in database.")
    else:
        for device_id, device_ip, device_hostname, device_type in zip(
            db.list_all_ips_with_type()[0],
            db.list_all_ips_with_type()[1],
            db.list_all_ips_with_type()[2],
            db.list_all_ips_with_type()[3],
        ):
            print(f"{device_id} : {device_ip} : {device_hostname} : {device_type}")
elif args.add:
    hostname = device.get_hostname(device_ip=args.add, device_type=args.type)

    if args.type is None:
        print("You must specify a device type with the -type flag.")
    else:
        if db.insert_device(ip=args.add, hostname=hostname, device_type=args.type) == 0:
            print(f"{args.add} already exists in the database.")
        else:
            print(f"{args.add} has been added to the database.")
elif args.remove:
    if db.delete_device(id=args.remove) == 1:
        print("Device removed.")
    else:
        print("Device ID does not exist.")
elif args.fetchall:
    get_config.fetch_all_configs()
elif args.clean:
    print("Cleaning up running-configs/ directory.")
    utils.del_oldest_configs(conf.MAX_CONFIGS)
