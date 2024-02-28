# net-config-repo

net-config-repo is a set of tools for network configuration management. It currently only supports hp_procurve devices. Support for more types of devices can be added in the vendors/ folder.

This is an ongoing project to make sure I keep using what little Python skills I have.



## Documentation

To run, use "python manage.py". Current options are:

- -h, --help       show this help message and exit
- --scan SCAN      Scan an IP address or CIDR for hosts that are alive.
- --list           List all devices in the database.
- --add ADD        Add a device to the database.
- --remove REMOVE  Delete a device from the database using the device id.
- --fetchall       Fetch all configs from the database.
- --clean          Clean up running-configs/ directory.
- -add             Add discovered device/s to the database.
- -v, --version    Show the version of the program.
- -skip SKIP       Skip adding device to the database when using the -add flag. Use a comma separated list of IPs.


## Authors

- [@redeuxx](https://www.github.com/redeuxx)
