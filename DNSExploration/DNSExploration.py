"""
DNSExploration.py

Simple DNS exploration utility:
- Resolve A records for a domain
- Attempt reverse DNS (PTR) on each discovered IP
- Brute-force subdomains from a wordlist
- Optionally append numeric suffixes 0-9 to each wordlist entry
  (e.g. api1. api2)

Design notes:
* Keep core actions small and composable (resolve_a, reverse_dns,
  probe, iterate_wordlist).
* Fail quietly on expected DNS failures (NXDOMAIN, NoAnswwer,
  timeouts) to keep scans readable.
* Provide a -- timeout knob to avoid long waits on unresponsive
  nameservers.
* Add an optional -- verbose flag to help with troubleshooting/
  resolver insight

Ethics:
- Only use against domains you own or have explicit permission to test
"""

import argparse
import logging
import socket
from typing import List

import dns.resolver
import dns.exception


def setup_logging(verbose: bool) -> None:
    """
    Initialise logging.

    Verbose logs include resolver timing, branching decisions, and suppressed
    exceptions. Using logging (instead of prints) makes it easy to integrate
    with other tools or CI.
    """
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(message)s"
    )


def reverse_dns(ip: str) -> str:
    """
    Attempt to obtain a PTR hostname for an IPV4 address.

    Returns:
        Hostname string (if present), or '' if no PTR or lookup fails.

    Why use socket.gethostbyaddr?
    - It's a simple, stdlib way to perform a reverse lookup.
    - If you need timeout control or v6 support later, consider dnspython's
      resolver for PTR as
    """
    try:
        host, _, _ = socket.gethostbyaddr(ip)
        logging.debug(f"[debug] PTR lookup for {ip} -> {host}")
        return host
    except Exception as e:
        # PTR records are optional; lots of IPs wont have them. Avoid noisy
        # tracebacks by default
        logging.debug(f"[debug] PTR lookup failed for {ip}: {e}")
        return ""


def resolve_a(domain: str, timeout: float = 3.0) -> List[str]:
    """
    Resolve A records for a FQDN

    Args:
        domain: The domain to resolve (e.g.,'example.com' or 'api.example.com')
        timeout: Resolver lifetime + single-query timeout (seconds)

    Returns:
        List of IPv4 addresses as strings. Empty list on NXDOMAIN, NoAnswer,
        Timeout, or resolver
    """
    try:
        # Create a fresh resolver so per-call timeouts are reliable.
        resolver = dns.resolver.Resolver()
        resolver.lifetime = timeout     # overall operation budget
        resolver.timeout = timeout      # per-try budget
        # NOTE: You can set resolver.nameservers = ['8.8.8.8', '1.1.1.1'] to 
        # override system DNS.
        answers = resolver.resolve(domain, "A")
        ips = [a.to_text() for a in answers]
        logging.debug(f"[debug] A lookup for {domain} -> {ips}")
        return ips
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer) as e:
        logging.debug(
            f"[debug] No A record for {domain}: {e.__class__.__name__}"
        )
        return []
    except dns.resolver.NoNameservers as e:
        logging.debug(f"[debug] No nameservers responded for {domain}: {e}")
        return []
    except dns.exception.Timeout:
        logging.debug(f"[debug] Timeout resolving {domain} (>{timeout}s)")
        return []


def probe(domain: str, timeout: float = 3.0) -> None:
    """
    Resolve a domain and print human-friendly output for A + PTR.

    This is intentionally side-effect-y (prints) to keep CLI simple.
    If you want to export JSON/CSV later, split printing form data collection
    """
    ips = resolve_a(domain, timeout=timeout)
    if not ips:
        return

    for ip in ips:
        print(f"[+] A: {domain} -> {ip}")
        ptr = reverse_dns(ip)
        if ptr:
            print(f"  PTR: {ptr}")


def iterate_wordlist(domain: str, words: List[str], add_numeric: bool, timeout: float) -> None:
    """
    Brute-force subdomains using a list of words.
    Optionally try word + digits [0-9] (e.g., 'api1.example.com)

    Args:
        domain: Base domain (example.com)
        words: List of candidate subdomain labels (e.g.,
            ['www', 'api', 'staging'])
        add_numeric: Whether to also try suffixes 0-9 for each word
        timeout: DNS timeout
    """
    for raw in words:
        word = raw.strip()
        # Skip empty lines and commented rows to tolerate common wordlists.
        if not word or word.startswith("#"):
            continue

        # Try the plain work first (www.example.com)
        sub = f"{word}.{domain}"
        probe(sub, timeout=timeout)

        # Optionally try numeric suffixes (api0..api9)
        if add_numeric:
            for i in range(10):
                sub_n = f"{word}{i}.{domain}"
                probe(sub_n, timeout=timeout)


def main() -> None:
    """
    Parse CLI args and orchestrate the exploration.
    """
    parser = argparse.ArgumentParser(
        description="DNS exploration (A lookups, reverse DNS, subdomain "
                    "brute-force)."
    )
    parser.add_argument("-d", "--domain", required=True,
                        help="Target domain (e.g., example.com)")
    parser.add_argument("-w", "--wordlist",
                        help="Subdomain wordlist file (one per line)")
    parser.add_argument("-n", "--numeric", action="store_true",
                        help="Also try numeric suffixes 0-9 for each word")
    parser.add_argument("--timeout", type=float, default=3.0,
                        help="DNS resolver timeout (seconds)")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Enable verbose debug logs")
    args = parser.parse_args()

    setup_logging(args.verbose)

    # Always probe the root domain first
    probe(args.domain, timeout=args.timeout)

    if args.wordlist:
        try:
            with open(args.wordlist, "r", encoding="utf-8") as f:
                words = f.read().splitlines()
            logging.debug(
                f"[debug] loaded {len(words)} words from {args.wordlist}"
            )
        except FileNotFoundError:
            print(f"[!] Wordlist not found: {args.wordlist}")
            return
        iterate_wordlist(
            args.domain,
            words,
            args.numeric,
            timeout=args.timeout
        )


if __name__ == "__main__":
    main()
