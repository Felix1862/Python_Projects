# PortScan.py

A simple Python script using [Scapy](https://scapy.net/) to perform:

**TCP SYN scans** on common ports  
**UDP DNS scan** to see if the target responds as a DNS server

---

## Features

- Scans typical ports: `25, 80, 53, 443, 445, 8080, 8443`
- Quickly identifies open TCP ports via SYN packets
- Checks if a host responds to DNS queries on port 53
- Clean CLI interface using `argparse`
- Runs on Windows (with Npcap) or Linux (with libpcap)

---

## Requirements

- Python 3.7+
- [Scapy](https://scapy.net/)

Install with:

```bash
pip install scapy
```

- On Linux, ensure tcpdump or libpcap is installed.
- On Windows, install Npcap (check “WinPcap API-compatible mode”).

## Usage
```bash
python3 portscan.py --host <target_ip_or_domain>
```
### Example
```bash
python3 portscan.py --host 8.8.8.8
```
 ## How it works
### TCP SYN Scan
- Crafts IP packets with TCP SYN flags to common ports.
- If a SYN-ACK is received, the port is considered open.

### DNS UDP Scan
- Sends a DNS query for google.com to UDP port 53.
- If a response comes back, indicates a DNS server is running.

## Contributing
If you find ways to extend it (like adding port ranges, JSON output, or banner grabbing), feel free to fork and submit a pull request.

# License
This project is open-source — use it, modify it, learn from it.

Consider adding an explicit MIT, GPL, or similar license in your repo.

# 🔍 PortScan.py

[![Python](https://img.shields.io/badge/Python-3.7%2B-blue.svg)](https://www.python.org/)
[![Scapy](https://img.shields.io/badge/Library-Scapy-yellow)](https://scapy.net/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Made with ❤️ by Felix1862](https://img.shields.io/badge/Made%20by-Felix1862-red)](https://github.com/Felix1862)

