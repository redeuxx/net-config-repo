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
group.add_argument("-s", "--scan", help='Scan an IP address or CIDR for hosts that are alive.')
group.add_argument("-l", "--list", help='List all devices in the database.')
group.add_argument("-a", "--add", help='Add a device to the database.')
# end group

parser.add_argument("-v", "--version", action='version', help='Show the version of the program.')
args = parser.parse_args()

if args.scan:
    hosts.scan_cidr(args.scan)
elif args.list:
    for ip, device_id in zip(db.list_all_ips()[0], db.list_all_ips()[1]):
        print(f"{device_id} - {ip}")
elif args.add:
    db.insert_device(ip=args.add, hostname="", device_type="")

# TODO: convert this to argparse
# if len(sys.argv) < 2:
#     OPTION = "default"
# else:
#     OPTION = sys.argv[1]

# match OPTION:
#     case "list":
#         # iterate through db.list_all_ips() and list 0 and 1 indexes of the list
#         for ip, device_id in zip(db.list_all_ips()[0], db.list_all_ips()[1]):
#             print(f"{device_id} - {ip}")
#     case "add":
#         # add device to db. Takes 2 arguments: ip, device_type
#         # TODO: there really needs to be syntax checking here
#         db.insert_device(ip=sys.argv[2], hostname="", device_type=sys.argv[3])
#     case "del":
#         # delete device by id
#         if db.delete_device(id=sys.argv[2]) == 1:
#             print("Device deleted.")
#         else:
#             print("Device ID does not exist.")
#     case "fetchall":
#         # fetch all configs
#         get_config.fetch_all_configs()
#     case "clean":
#         # clean up running-configs/ directory
#         print("Cleaning up running-configs/ directory.")
#         utils.del_oldest_configs(conf.MAX_CONFIGS)
#     case _:  # default
#         print("Valid options are: list, add, del, fetchall, clean")
