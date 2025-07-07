"""

    PortScan.py
    ------------
    A simple Python script using Scapy to perform:
    1. TCP SYN scans on common
    2. A UDP DNS scan to see if the target is responding to DNS requests.

    Author: Felix1862

"""

import argparse
from scapy.all import IP, TCP, UDP, DNS, DNSQR, sr


# List of common ports to scan
ports = [25, 80, 53, 443, 445, 8080, 8443]


def SynScan(host):
    """
    Performs a TCP SYN scan on the specified host over the ports list.

    Args:
        host (str): The target IP address.

    """
    print(f"[*] Starting SYN scan on {host}")
    # Craft IP and TCP packets with SYN flag set to scan ports
    ans, unans = sr(
        IP(dst=host) / TCP(sport=5555, dport=ports, flags="S"),
        timeout=2,
        verbose=0
    )

    open_ports = []
    for sent, received in ans:
        # If we get a SYN-ACK back, means the port is open
        if sent[TCP].dport == received[TCP].sport:
            open_ports.append(sent[TCP].dport)

    if open_ports:
        print(f"[+] Open ports at {host}: {open_ports}")
    else:
        print(f"[-] No open ports found on {host}.")


def DNSScan(host):
    """
    Sends a DNS query over UDP to port 53 to see if the target as a DNS

    Args:
        host (str): The target IP address

    """
    print(f"[*] Starting DNS scan on {host}")
    # Craft UDP packet with DNS query for 'google.com'
    ans, unans = sr(
        IP(dst=host) / UDP(sport=5555, dport=53) /
        DNS(rd=1, qd=DNSQR(qname="google.com")),
        timeout=2,
        verbose=0
    )

    if ans:
        print(f"[+] DNS server found at {host}")
    else:
        print(f"[-] No DNS response from {host}")


if __name__ == "__main__":
    # Create the argument parser with a description
    parser = argparse.ArgumentParser(
        description="Simple TCP SYN and DNS scanner using Scapy"
        )

    # Add required argument --host to specify the target IP or Domain
    parser.add_argument(
        "--host",
        type=str,
        required=True,
        help="Target IP address or domain to scan"
    )

    # Parse the command-line arguments
    args = parser.parse_args()

    # Extract the host value
    host = args.host

    # Run the scans on the provided host
    print(f"[*] Starting scans on {host}")
    SynScan(host)
    DNSScan(host)
