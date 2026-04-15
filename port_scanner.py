import socket
import datetime
import threading

# Store results
open_ports = []
lock = threading.Lock()

def scan_port(host, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.3)  # faster timeout
        result = sock.connect_ex((host, port))
        sock.close()
        if result == 0:
            with lock:
                service = get_service(port)
                open_ports.append({"port": port, "service": service})
                print(f"✅ Port {port:5} OPEN  →  {service}")
    except:
        pass

def get_service(port):
    services = {
        21: "FTP", 22: "SSH", 23: "Telnet",
        25: "SMTP", 53: "DNS", 80: "HTTP",
        110: "POP3", 143: "IMAP", 443: "HTTPS",
        445: "SMB", 631: "CUPS", 3306: "MySQL",
        3389: "RDP", 5432: "PostgreSQL",
        8080: "HTTP-Alt", 8443: "HTTPS-Alt",
    }
    return services.get(port, "Unknown")

def scan_target(host, start_port, end_port):
    global open_ports
    open_ports = []
    start_time = datetime.datetime.now()
    
    print(f"""
╔══════════════════════════════════════╗
║         🦦 OTT3RR PORT SCANNER       ║
╚══════════════════════════════════════╝
Target:     {host}
Port Range: {start_port} - {end_port}
Started:    {start_time.strftime("%Y-%m-%d %H:%M:%S")}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")

    threads = []
    for port in range(start_port, end_port + 1):
        t = threading.Thread(target=scan_port, args=(host, port))
        threads.append(t)
        t.start()
        if len(threads) >= 100:
            for t in threads:
                t.join()
            threads = []
    for t in threads:
        t.join()

    end_time = datetime.datetime.now()
    duration = (end_time - start_time).seconds

    print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Scan Complete!
Open Ports Found: {len(open_ports)}
Duration:         {duration} seconds
Finished:         {end_time.strftime("%Y-%m-%d %H:%M:%S")}
""")
    save_report(host, start_port, end_port, start_time, end_time, duration)

def save_report(host, start_port, end_port, start_time, end_time, duration):
    # Create reports folder if it doesn't exist
    import os
    if not os.path.exists("scan_reports"):
        os.makedirs("scan_reports")

    # Create filename with timestamp
    filename = f"scan_reports/{host}_{start_time.strftime('%Y%m%d_%H%M%S')}.txt"

    with open(filename, "w") as f:
        f.write("╔══════════════════════════════════════╗\n")
        f.write("║       🦦 OTT3RR PORT SCANNER REPORT   ║\n")
        f.write("╚══════════════════════════════════════╝\n\n")
        f.write(f"Target:     {host}\n")
        f.write(f"Port Range: {start_port} - {end_port}\n")
        f.write(f"Started:    {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Finished:   {end_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Duration:   {duration} seconds\n")
        f.write(f"Open Ports: {len(open_ports)}\n")
        f.write("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
        f.write("OPEN PORTS:\n")
        f.write("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n")

        if len(open_ports) == 0:
            f.write("No open ports found.\n")
        else:
            for p in sorted(open_ports, key=lambda x: x["port"]):
                f.write(f"[OPEN] Port {p['port']:5} → {p['service']}\n")

        f.write("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
        f.write("RECOMMENDATIONS:\n")
        f.write("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n")

        for p in sorted(open_ports, key=lambda x: x["port"]):
            if p["service"] == "FTP":
                f.write(f"⚠️  Port {p['port']} FTP - Consider using SFTP instead\n")
            elif p["service"] == "Telnet":
                f.write(f"🚨 Port {p['port']} Telnet - INSECURE! Use SSH instead\n")
            elif p["service"] == "SSH":
                f.write(f"✅ Port {p['port']} SSH - Ensure key auth only, disable password auth\n")
            elif p["service"] == "HTTP":
                f.write(f"⚠️  Port {p['port']} HTTP - Consider redirecting to HTTPS\n")
            elif p["service"] == "SMB":
                f.write(f"🚨 Port {p['port']} SMB - High risk! Ensure patched against EternalBlue\n")
            elif p["service"] == "RDP":
                f.write(f"🚨 Port {p['port']} RDP - High risk! Use VPN + NLA authentication\n")
            elif p["service"] == "CUPS":
                f.write(f"ℹ️  Port {p['port']} CUPS - Printer service, ensure localhost only\n")
            else:
                f.write(f"ℹ️  Port {p['port']} {p['service']} - Review if this service is needed\n")

    print(f"📄 Report saved to: {filename}")

# Main program
try:
    print("🦦 Welcome to Ott3rr Port Scanner!")
    print("⚠️  Only scan targets you have permission to scan!")
    print("💡 Press Ctrl+C at any time to quit\n")

    host = input("Enter target (hostname or IP): ")
    start = int(input("Start port (e.g. 1): "))
    end = int(input("End port (e.g. 1024): "))

    scan_target(host, start, end)

except KeyboardInterrupt:
    print("\n\n⛔ Scan cancelled by user!")
    print(f"✅ Open ports found so far: {len(open_ports)}")
    for p in open_ports:
        print(f"   Port {p['port']} → {p['service']}")
        