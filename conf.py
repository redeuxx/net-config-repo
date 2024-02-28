import pathlib

VERSION = "0.0.1"
# Use pathlib to specify the path to store the running-configs, see https://docs.python.org/3/library/pathlib.html
# This default path will point to the user home directory, under a folder called "running-configs"
# For example, in Windows, the path will be C:\Users\username\running-configs and in Linux,
# /home/username/running-configs
STORE_DIR = pathlib.Path.home() / "running-configs/"
MAX_CONFIGS = 10
