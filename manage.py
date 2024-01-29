# manage.py

import argparse
import sys
import db
import get_config
import utils
import conf
import hosts

parser = argparse.ArgumentParser(
    usage = "test.py [options]",
    description = "--scan - Scan a CIDR for hosts."
)
parser.version = conf.VERSION

# You must choose one of the mutually exclusive options.
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument("--scan", help='Scan an IP address or CIDR for hosts that are alive.')
group.add_argument("--list", action="store_true", help='List all devices in the database.')
group.add_argument("--add", help='Add a device to the database.')
group.add_argument("--remove", type=int, help='Delete a device from the database using the device id.')
group.add_argument("--fetchall", action="store_true", help='Fetch all configs from the database.')
group.add_argument("--clean", action="store_true", help='Clean up running-configs/ directory.')

# end group
parser.add_argument("-hostname", help='Hostname of the device.')
parser.add_argument("-type", help='Type of device.')
parser.add_argument("-v", "--version", action='version', help='Show the version of the program.')

args = parser.parse_args()

if args.scan:
    hosts.scan_cidr(args.scan)
elif args.list:
    if(len(db.list_all_ips()[0])) == 0:
        print("No devices in database.")
    else:
        for ip, device_id in zip(db.list_all_ips()[0], db.list_all_ips()[1]):
            print(f"{device_id} - {ip}")
elif args.add:
    if (args.hostname is not None):
        hostname = args.hostname
    else:
        hostname = ""
        
    if(args.type is None):
        print("You must specify a device type with the -type flag.")
    else:
        db.insert_device(ip=args.add, hostname="", device_type=args.type)
        print("Device added.")
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
