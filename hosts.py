import ipaddress
from tqdm import tqdm
from icmplib import ping


def get_cidr_hosts(ip):
    """
    Get hosts given an ip address or CIDR.

    Args:
        ip_address: The ip address/CIDR to check.

    Returns:
        The ip address or addresses
    """
    return ipaddress.ip_network(ip).hosts()


def is_alive(ip):
    """
    Sends ICMP ping to host to determine if host is alive.

    Args:
        ip: IP of host to ping.

    Returns: True or False
    """
    return ping(ip, count=2, timeout=1).is_alive


def scan_cidr(ip):
    """
    Scans a CIDR for hosts.

    Args:
        ip: The CIDR or IP to scan

    Returns:
        True or False
    """
    total_hosts = len(list(get_cidr_hosts(ip)))
    hosts = get_cidr_hosts(ip)
    print(f"Scanning {total_hosts} hosts ...")

    for host in tqdm(hosts, total=total_hosts):
        is_alive(str(host))
