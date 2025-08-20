# DNSExploration

A small Python tool for exploring DNS:
- Resolve A records for a domain
- Attempt reverse DNS on resulting IPs (PTR)
- Brute-force subdomains from a wordlist
- Optional numeric suffixes (e.g., `api1.example.com` … `api9.example.com`)

Built with **dnspython**. Works on Linux, macOS, and Windows.

---

## Features
- **A record lookups** for a given domain
- **Reverse DNS** attempts (PTR) for each discovered IP
- **Subdomain brute-force** from a wordlist
- **Numeric suffix mode** with `-n`

---

## Install

```bash
python3 -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
pip install dnspython
```


## Usage
python DNSExploration.py -h

usage: DNSExploration.py [-h] -d DOMAIN [-w WORDLIST] [-n] [--timeout TIMEOUT] [-v]

DNS exploration (A lookups, reverse DNS, subdomain brute-force).

options:
  -d, --domain    Target domain (e.g., example.com)  [required]
  -w, --wordlist  Subdomain wordlist file (one per line)
  -n, --numeric   Also try numeric suffixes 0–9 for each word
  --timeout       DNS resolver timeout in seconds (default: 3.0)
  -v, --verbose   Enable verbose debug logs


## Examples
# Resolve only the root domain and reverse DNS on its IPs
python DNSExploration.py -d example.com

# Brute-force subdomains from a wordlist
python DNSExploration.py -d example.com -w subdomains.txt

# Add numeric suffixes (api0..api9.example.com)
python DNSExploration.py -d example.com -w subdomains.txt -n

## Sample Output
[+] A: example.com -> 93.184.216.34
    ↳ PTR: 93.184.216.34

[+] A: www.example.com -> 93.184.216.34
    ↳ PTR: 93.184.216.34

## Notes & Ethics
Only probe domains you own or have permission to test.
DNS results change frequently; timeouts and no-answer cases are normal.

### Roadmap
Concurrency with --workers
Output to JSON/CSV
Support AAAA/MX/TXT/CNAME


### Tiny extras (optional, nice-to-have):
- Add a `requirements.txt` with `dnspython>=2.6.1` and change Install to `pip install -r requirements.txt`.
- Add a `subdomains.txt` sample and reference it in the README.
