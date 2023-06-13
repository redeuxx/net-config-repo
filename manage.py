import sys
import db

if len(sys.argv) < 2:
    OPTION = "default"
else:
    OPTION = sys.argv[1]

match OPTION:
    case "list":
        pass
        # TODO: list all the devices in the database
    case "add":
        db.insert_device(ip=sys.argv[2], hostname="", device_type=sys.argv[3])
    case _:  # default
        print("Valid options are: list")
