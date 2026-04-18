"""Tests for the scanner module."""

import socket
import socketserver
import threading
import unittest
from unittest.mock import patch, MagicMock

from scanner import scan_port, scan_ports, get_open_ports


class TestScanPort(unittest.TestCase):
    """Tests for scan_port function."""

    def test_open_port_returns_true(self):
        """scan_port should return True for an open port."""
        # Start a simple TCP server on an ephemeral port
        server = socketserver.TCPServer(("127.0.0.1", 0), socketserver.BaseRequestHandler)
        port = server.server_address[1]
        thread = threading.Thread(target=server.handle_request)
        thread.daemon = True
        thread.start()
        try:
            result = scan_port("127.0.0.1", port, timeout=2.0)
            self.assertTrue(result)
        finally:
            server.server_close()

    def test_closed_port_returns_false(self):
        """scan_port should return False for a closed port."""
        # Port 1 is almost certainly closed and requires no privileges to check
        result = scan_port("127.0.0.1", 1, timeout=0.5)
        self.assertFalse(result)

    def test_unreachable_host_returns_false(self):
        """scan_port should return False for an unreachable host."""
        # 192.0.2.0/24 is reserved (TEST-NET-1) and should not be reachable
        result = scan_port("192.0.2.1", 80, timeout=0.1)
        self.assertFalse(result)


class TestScanPorts(unittest.TestCase):
    """Tests for scan_ports function."""

    def test_returns_dict_with_all_ports(self):
        """scan_ports should return a result entry for every requested port."""
        ports = [1, 2, 3]
        with patch("scanner.scan_port", return_value=False):
            results = scan_ports("127.0.0.1", ports, timeout=0.1)
        self.assertEqual(set(results.keys()), set(ports))

    def test_open_ports_marked_true(self):
        """scan_ports should mark open ports as True."""
        def fake_scan(host, port, timeout):
            return port == 80

        with patch("scanner.scan_port", side_effect=fake_scan):
            results = scan_ports("127.0.0.1", [80, 443], timeout=0.1)

        self.assertTrue(results[80])
        self.assertFalse(results[443])

    def test_empty_port_list(self):
        """scan_ports should return an empty dict for an empty port list."""
        results = scan_ports("127.0.0.1", [], timeout=0.1)
        self.assertEqual(results, {})


class TestGetOpenPorts(unittest.TestCase):
    """Tests for get_open_ports function."""

    def test_returns_sorted_open_ports(self):
        """get_open_ports should return a sorted list of open ports."""
        def fake_scan(host, port, timeout):
            return port in {443, 80, 22}

        with patch("scanner.scan_port", side_effect=fake_scan):
            open_ports = get_open_ports("127.0.0.1", [443, 22, 80], timeout=0.1)

        self.assertEqual(open_ports, [22, 80, 443])

    def test_no_open_ports_returns_empty_list(self):
        """get_open_ports should return an empty list when no ports are open."""
        with patch("scanner.scan_port", return_value=False):
            open_ports = get_open_ports("127.0.0.1", [1, 2, 3], timeout=0.1)

        self.assertEqual(open_ports, [])

    def test_all_ports_open(self):
        """get_open_ports should include all ports when all are open."""
        with patch("scanner.scan_port", return_value=True):
            open_ports = get_open_ports("127.0.0.1", [100, 200, 300], timeout=0.1)

        self.assertEqual(open_ports, [100, 200, 300])


if __name__ == "__main__":
    unittest.main()
