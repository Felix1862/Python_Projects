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

