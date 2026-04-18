# Scanner

A lightweight Python port scanner that checks which TCP ports are open on a given host.

## Features

- Scan a single port or a list of ports
- Concurrent scanning for fast results
- Simple API and command-line interface

## Usage

### Command Line

```bash
python scanner.py <host>
```

Scans ports 1–1024 on the given host. Defaults to `localhost` when no host is provided.

```bash
python scanner.py example.com
```

### Python API

```python
from scanner import scan_port, scan_ports, get_open_ports

# Check a single port
is_open = scan_port("example.com", 80)

# Scan multiple ports (returns dict {port: bool})
results = scan_ports("example.com", [22, 80, 443])

# Get a sorted list of open ports
open_ports = get_open_ports("example.com", range(1, 1025))
```

## Running Tests

```bash
python -m unittest discover tests/
```