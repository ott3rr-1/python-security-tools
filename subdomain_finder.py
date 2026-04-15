import dns.resolver
import threading
import requests
import os
from datetime import datetime

# ============================================================
# SUBDOMAIN FINDER - by 0tt3rr
# Uses DNS resolution to find valid subdomains on a target
# ============================================================

# Results storage and thread lock (same pattern as port scanner)
found_subdomains = []
lock = threading.Lock()

# Common subdomains wordlist
WORDLIST = [
    "www", "mail", "ftp", "dev", "staging", "api", "admin", "portal",
    "vpn", "remote", "test", "beta", "app", "shop", "blog", "forum",
    "support", "help", "docs", "cdn", "static", "media", "images",
    "login", "auth", "secure", "dashboard", "panel", "manage",
    "git", "gitlab", "github", "jenkins", "jira", "confluence",
    "smtp", "pop", "imap", "webmail", "mx", "ns1", "ns2",
    "internal", "intranet", "corp", "office", "backup", "old",
    "v2", "v1", "new", "mobile", "m", "wap", "status", "monitor"
]

def check_subdomain(domain, subdomain, http_check=False):
    full_domain = f"{subdomain}.{domain}"
    try:
        dns.resolver.resolve(full_domain, "A")
        if http_check:
            http_status = check_http(full_domain)
            result = f"{full_domain} → {http_status}"
        else:
            result = full_domain
        with lock:
            found_subdomains.append(result)
            print(f"  [✅ FOUND] {result}")
    except:
        pass  # Doesn't exist, move on silently

def check_http(subdomain):
    """Check if a found subdomain has a live website"""
    for protocol in ["https", "http"]:
        try:
            url = f"{protocol}://{subdomain}"
            response = requests.get(url, timeout=3, allow_redirects=True)
            return f"{protocol.upper()} {response.status_code}"
        except:
            pass
    return "No web server"

def run_scan(domain, http_check=False):
    """Launch all subdomain checks using threads"""
    print(f"\n🔍 Scanning subdomains for: {domain}")
    print(f"📋 Checking {len(WORDLIST)} possible subdomains...")
    if http_check:
        print(f"🌐 HTTP checking enabled — requests will be sent to found subdomains")
    else:
        print(f"🔒 HTTP checking disabled — DNS only, passive scan")
    print()

    threads = []
    for subdomain in WORDLIST:
        t = threading.Thread(target=check_subdomain, args=(domain, subdomain, http_check))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

def save_report(domain):
    """Save results to a subdomain_reports folder"""

    # Create folder if it doesn't exist
    os.makedirs("subdomain_reports", exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"subdomain_reports/subdomain_{domain}_{timestamp}.txt"

    with open(filename, "w") as f:
        f.write(f"SUBDOMAIN SCAN REPORT\n")
        f.write(f"Target: {domain}\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Found: {len(found_subdomains)} subdomains\n")
        f.write("=" * 40 + "\n\n")
        for sub in found_subdomains:
            f.write(f"{sub}\n")

    print(f"\n📄 Report saved to: {filename}")

# ============================================================
# MAIN
# ============================================================
print("=" * 50)
print("     🔍 SUBDOMAIN FINDER by 0tt3rr")
print("=" * 50)

domain = input("\nEnter target domain (e.g. google.com): ").strip()

print("\n⚠️  HTTP checking sends real requests to found subdomains.")
print("   DNS only is passive and leaves no logs on the target.\n")
http_input = input("Enable HTTP checking? (y/n): ").strip().lower()
http_check = http_input == "y"

start = datetime.now()
run_scan(domain, http_check)
end = datetime.now()

print(f"\n{'=' * 50}")
print(f"✅ Scan complete in {(end - start).seconds} seconds")
print(f"🎯 Found {len(found_subdomains)} subdomains")
print("=" * 50)

if found_subdomains:
    save = input("\nSave report? (y/n): ")
    if save.lower() == "y":
        save_report(domain)
