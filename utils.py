# utils.py

import os
import conf
from dataclasses import dataclass
import getpass


def get_directories(directory):
    """
    Returns a list of all the directories in a directory.

    Args:
        directory: The path to the directory.

    Returns:
        A list of the directories in the directory.
    """

    directories = []
    for dirr in os.listdir(directory):
        if os.path.isdir(os.path.join(directory, dirr)):
            directories.append(os.path.join(conf.STORE_DIR, dirr))

    return directories


def get_oldest_files(directory, amount):
    """
    Returns a list of the oldest files in a directory, not including the newest 10 files and only
    if the directory has more than 10 files.

    Args:
        directory: The path to the directory.
        amount: The number of files to return.

    Returns:
        A list of the oldest files in the directory.
    """

    if len(os.listdir(directory)) <= amount:
        return []

    all_files = []
    for file in os.listdir(directory):
        if os.path.isfile(os.path.join(directory, file)):
            all_files.append(file)

    newest_files = all_files[:amount]

    files_not_in_newest = [file for file in all_files if file not in newest_files]

    return files_not_in_newest


def num_files(directory):
    """
    Returns the number of files in a directory.

    Args:
        directory: The path to the directory.

    Returns:
        The number of files in the directory.
    """

    number_of_files = 0
    for file in os.listdir(directory):
        if os.path.isfile(os.path.join(directory, file)):
            number_of_files += 1

    return number_of_files


def del_oldest_configs(amount):
    """
    Deletes the oldest configs in the store directory.

    Args:
        Number of configs to delete.

    Returns:
        None

    """

    for i in get_directories(conf.STORE_DIR):
        for file in get_oldest_files(i, amount):
            print(f"Removing {os.path.join(i, file)}.")
            os.remove(os.path.join(i, file))


@dataclass
class GetCredentials:
    """
    Class to accept user input for username, password and enable password.
    """

    username: str = input("Enter the username to authenticate with: ")
    password: str = getpass.getpass("Enter the password to authenticate with: ")
    enable_password: str = getpass.getpass(
        "Enter the enable password to authenticate with \n(Press Enter if it is the same as previous password): "
    )
