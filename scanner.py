"""
Scanner - A simple port scanner utility.
"""

import socket
import concurrent.futures
from typing import List


def scan_port(host: str, port: int, timeout: float = 1.0) -> bool:
    """Check if a single port is open on the given host.

    Args:
        host: The hostname or IP address to scan.
        port: The port number to check.
        timeout: Connection timeout in seconds.

    Returns:
        True if the port is open, False otherwise.
    """
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False


def scan_ports(host: str, ports: List[int], timeout: float = 1.0, max_workers: int = 100) -> dict:
    """Scan multiple ports on the given host concurrently.

    Args:
        host: The hostname or IP address to scan.
        ports: A list of port numbers to scan.
        timeout: Connection timeout in seconds for each port.
        max_workers: Maximum number of concurrent threads.

    Returns:
        A dictionary mapping port numbers to their open/closed status.
    """
    results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_port = {
            executor.submit(scan_port, host, port, timeout): port
            for port in ports
        }
        for future in concurrent.futures.as_completed(future_to_port):
            port = future_to_port[future]
            results[port] = future.result()
    return results


def get_open_ports(host: str, ports: List[int], timeout: float = 1.0, max_workers: int = 100) -> List[int]:
    """Return a sorted list of open ports on the given host.

    Args:
        host: The hostname or IP address to scan.
        ports: A list of port numbers to scan.
        timeout: Connection timeout in seconds for each port.
        max_workers: Maximum number of concurrent threads.

    Returns:
        A sorted list of open port numbers.
    """
    results = scan_ports(host, ports, timeout=timeout, max_workers=max_workers)
    return sorted(port for port, is_open in results.items() if is_open)


if __name__ == "__main__":
    import sys

    host = sys.argv[1] if len(sys.argv) > 1 else "localhost"
    ports = list(range(1, 1025))

    print(f"Scanning {host} for open ports (1-1024)...")
    open_ports = get_open_ports(host, ports)

    if open_ports:
        print(f"Open ports: {open_ports}")
    else:
        print("No open ports found.")
