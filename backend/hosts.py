# hosts.py

import ipaddress
from tqdm import tqdm
from icmplib import ping, multiping


def get_cidr_hosts(ip):
    """
    Get hosts given an ip address or CIDR.

    Args:
        ip: The ip address/CIDR to check.

    Returns:
        The ip address or addresses
    """

    try:
        hosts = ipaddress.ip_network(ip, strict=False).hosts()
        return hosts
    except ValueError:
        raise ValueError(f"Invalid IP address or CIDR: {ip}")


def is_alive(ip):
    """
    Sends ICMP ping to host to determine if host is alive.

    Args:
        ip: IP of host to ping.

    Returns: True or False
    """

    return ping(ip, count=2, timeout=1).is_alive


def scan_cidr(ip, print_fn=None):
    """
    Scans a CIDR for hosts.

    Args:
        ip: The CIDR or IP to scan
        print_fn: Optional function to call with progress messages

    Returns:
        alive_hosts: A list of alive hosts.
    """

    hosts = [str(h) for h in get_cidr_hosts(ip)]
    total_hosts = len(hosts)
    alive_hosts = []

    msg = f"Scanning {total_hosts} hosts ..."
    if print_fn: print_fn(msg)
    else: print(msg)

    batch_size = 50
    for i in range(0, total_hosts, batch_size):
        batch = hosts[i:i+batch_size]
        batch_msg = f"Pinging hosts {i+1} to {min(i+batch_size, total_hosts)} of {total_hosts}..."
        if print_fn: print_fn(batch_msg)
        else: print(batch_msg)
        
        responses = multiping(batch, count=2, timeout=1, concurrent_tasks=50)
        
        batch_alive = [host.address for host in responses if host.is_alive]
        alive_hosts.extend(batch_alive)

    num_alive = len(alive_hosts)
    final_msg = f"{num_alive} hosts are alive."
    if print_fn: print_fn(final_msg)
    else: print(final_msg)

    return alive_hosts
