import sys
import db
import get_config
import utils
import conf

if len(sys.argv) < 2:
    OPTION = "default"
else:
    OPTION = sys.argv[1]

match OPTION:
    case "list":
        # iterate through db.list_all_ips() and list 0 and 1 indexes of the list
        for ip, device_id in zip(db.list_all_ips()[0], db.list_all_ips()[1]):
            print(f"{device_id} - {ip}")
    case "add":
        # add device to db. Takes 2 arguments: ip, device_type
        # TODO: there really needs to be syntax checking here
        db.insert_device(ip=sys.argv[2], hostname="", device_type=sys.argv[3])
    case "del":
        # delete device by id
        if db.delete_device(id=sys.argv[2]) == 1:
            print("Device deleted.")
        else:
            print("Device ID does not exist.")
    case "fetchall":
        # fetch all configs
        get_config.fetch_all_configs()
    case "clean":
        # clean up running-configs/ directory
        print("Cleaning up running-configs/ directory.")
        utils.del_oldest_configs(conf.MAX_CONFIGS)
    case _:  # default
        print("Valid options are: list, add, del, fetchall, clean")
