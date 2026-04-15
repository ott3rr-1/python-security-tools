import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
from datetime import datetime
import os

# ============================================================
# WEB CRAWLER - by 0tt3rr
# Politely crawls a website and maps all discoverable links
# ============================================================

# Storage
visited = set()      # Pages we've already crawled
found_links = []     # All unique links discovered
lock_out = False     # Emergency stop flag

# Keywords that indicate potentially interesting endpoints
INTERESTING_KEYWORDS = [
    "/admin", "/login", "/api", "/upload", "/config",
    "/backup", "/debug", "/test", "/dev", "/secret",
    "/password", "/passwd", "/user", "/account", "/dashboard",
    "?id=", "?file=", "?path=", "?redirect=", "?search=", "?url="
]

# Storage for interesting findings
interesting_found = []

def is_same_domain(url, base_domain):
    """Make sure we only crawl the target domain, not the whole internet!"""
    return urlparse(url).netloc == base_domain

def crawl(start_url, base_domain, max_pages, delay, flag_interesting=False):
    """Crawl using a queue instead of recursion — much more controlled"""
    
    # Queue holds pages waiting to be crawled — starts with just the target URL
    # This is like a to-do list — we add pages as we discover them
    queue = [start_url]

    # Keep going as long as there are pages to crawl AND we haven't hit the limit
    while queue and len(visited) < max_pages:
        
        # Grab the next page from the front of the queue
        url = queue.pop(0)

        # Skip if we've already visited this page (prevents loops)
        if url in visited:
            continue

        try:
            # Mark as visited BEFORE requesting so other threads don't duplicate it
            visited.add(url)

            # Send polite request with honest user agent so the server knows who we are
            headers = {"User-Agent": "0tt3rr-crawler/1.0 (educational security tool)"}
            response = requests.get(url, headers=headers, timeout=5)

            # Skip non-HTML pages (images, PDFs, etc) — nothing useful to crawl there
            if "text/html" not in response.headers.get("Content-Type", ""):
                continue

            print(f"  [🕷️  CRAWLING] {url} → {response.status_code}")

            # Parse the page HTML looking for all <a href="..."> link tags
            soup = BeautifulSoup(response.text, "html.parser")
            for tag in soup.find_all("a", href=True):
                
                # Build full URL from relative links (e.g. /about → https://site.com/about)
                # Also strip #fragments since they're just page sections, not new pages
                full_url = urljoin(url, tag["href"]).split("#")[0]

                # Only add links that are on the same domain — we don't want to
                # crawl the whole internet! Also skip already visited pages
                if is_same_domain(full_url, base_domain) and full_url not in visited:
                    
                    # Add to our master links list if not already there
                    if full_url not in found_links:
                        found_links.append(full_url)

                    # Check if this URL contains any interesting keywords
                    if flag_interesting:
                        if any(keyword in full_url.lower() for keyword in INTERESTING_KEYWORDS):
                             if full_url not in interesting_found:
                                interesting_found.append(full_url)
                                print(f"  [🎯 INTERESTING] {full_url}")
                    
                    # Add to the queue so we crawl it next — this is what makes
                    # it recursive in behavior without actually using recursion
                    if full_url not in queue:
                        queue.append(full_url)

            # Polite delay between requests — be a good citizen on the internet!
            time.sleep(delay)

        except KeyboardInterrupt:
            # User hit Ctrl+C — stop cleanly
            print("\n⚠️  Crawl stopped by user!")
            break
        except Exception:
            # Skip any pages that error out and keep going
            pass

def save_report(target):
    """Save results to file"""
    os.makedirs("crawler_reports", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    domain = urlparse(target).netloc
    filename = f"crawler_reports/crawl_{domain}_{timestamp}.txt"

    with open(filename, "w") as f:
        f.write(f"WEB CRAWLER REPORT\n")
        f.write(f"Target: {target}\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Pages crawled: {len(visited)}\n")
        f.write(f"Links found: {len(found_links)}\n")
        f.write("=" * 40 + "\n\n")
        f.write("CRAWLED PAGES:\n")
        for v in visited:
            f.write(f"  {v}\n")
        f.write(f"\nALL DISCOVERED LINKS:\n")
        for link in found_links:
            f.write(f"  {link}\n")

    if interesting_found:
        f.write(f"\n🎯 INTERESTING ENDPOINTS ({len(interesting_found)} found):\n")
        for link in interesting_found:
            f.write(f"  {link}\n")

    print(f"\n📄 Report saved to: {filename}")

# ============================================================
# MAIN
# ============================================================
print("=" * 50)
print("        🕷️  WEB CRAWLER by 0tt3rr")
print("=" * 50)

print("\n⚠️  Only crawl sites you own or have permission to scan.")
print("   This tool sends real HTTP requests to the target.\n")

target = input("Enter target URL (e.g. https://example.com): ").strip()

# Make sure URL has http/https
if not target.startswith("http"):
    target = "https://" + target

base_domain = urlparse(target).netloc

max_pages = input("\nMax pages to crawl (default 20): ").strip()
max_pages = int(max_pages) if max_pages.isdigit() else 20

delay = input("Delay between requests in seconds (default 1): ").strip()
delay = float(delay) if delay.replace(".", "").isdigit() else 1.0

flag_input = input("Flag interesting endpoints? (y/n): ").strip().lower()
flag_interesting = flag_input == "y"

print(f"\n🕷️  Starting crawl of {target}")
print(f"📋 Max pages: {max_pages} | Delay: {delay}s | Flag interesting: {'Yes 🎯' if flag_interesting else 'No'}")
print(f"⏹️  Press Ctrl+C to stop early\n")

start = datetime.now()
crawl(target, base_domain, max_pages, delay, flag_interesting)
end = datetime.now()

print(f"\n{'=' * 50}")
print(f"✅ Crawl complete in {(end - start).seconds} seconds")
print(f"🕷️  Pages crawled: {len(visited)}")
print(f"🔗 Links discovered: {len(found_links)}")
print("=" * 50)

if visited:
    save = input("\nSave report? (y/n): ")
    if save.lower() == "y":
        save_report(target)
