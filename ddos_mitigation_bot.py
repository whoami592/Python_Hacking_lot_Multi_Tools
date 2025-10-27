import time
import threading
from collections import defaultdict
import signal
import sys
import logging
from scapy.all import sniff, IP, TCP, UDP
import subprocess

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuration
BLOCK_THRESHOLD = 100  # Number of requests in time window to trigger block
TIME_WINDOW = 10  # Time window in seconds
BLOCK_DURATION = 300  # Duration to block IP in seconds
WHITELIST = {'127.0.0.1'}  # Whitelisted IPs
blocked_ips = set()
traffic_counts = defaultdict(lambda: defaultdict(int))
block_expiry = defaultdict(float)

def block_ip(ip):
    """Block an IP using iptables."""
    if ip not in blocked_ips and ip not in WHITELIST:
        try:
            subprocess.run(['iptables', '-A', 'INPUT', '-s', ip, '-j', 'DROP'], check=True)
            blocked_ips.add(ip)
            block_expiry[ip] = time.time() + BLOCK_DURATION
            logging.info(f"Blocked IP: {ip} for {BLOCK_DURATION} seconds")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to block IP {ip}: {e}")

def unblock_ip(ip):
    """Unblock an IP using iptables."""
    if ip in blocked_ips:
        try:
            subprocess.run(['iptables', '-D', 'INPUT', '-s', ip, '-j', 'DROP'], check=True)
            blocked_ips.remove(ip)
            del block_expiry[ip]
            logging.info(f"Unblocked IP: {ip}")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to unblock IP {ip}: {e}")

def check_block_expiry():
    """Periodically check and unblock IPs whose block duration has expired."""
    while True:
        current_time = time.time()
        for ip in list(block_expiry.keys()):
            if current_time > block_expiry[ip]:
                unblock_ip(ip)
        time.sleep(10)

def analyze_packet(packet):
    """Analyze incoming packets and detect potential DDoS patterns."""
    if IP in packet:
        src_ip = packet[IP].src
        if src_ip in WHITELIST or src_ip in blocked_ips:
            return

        # Increment traffic count for the source IP
        current_time = int(time.time() // TIME_WINDOW) * TIME_WINDOW
        traffic_counts[src_ip][current_time] += 1

        # Check if the IP exceeds the request threshold
        total_requests = sum(traffic_counts[src_ip].values())
        if total_requests > BLOCK_THRESHOLD:
            logging.warning(f"High traffic detected from IP: {src_ip} ({total_requests} requests)")
            block_ip(src_ip)

        # Clean up old traffic counts
        for timestamp in list(traffic_counts[src_ip].keys()):
            if time.time() - timestamp > TIME_WINDOW:
                del traffic_counts[src_ip][timestamp]

def start_sniffing(interface="eth0"):
    """Start sniffing network traffic."""
    logging.info("Starting DDoS mitigation bot...")
    try:
        sniff(iface=interface, prn=analyze_packet, filter="ip", store=False)
    except Exception as e:
        logging.error(f"Error in sniffing: {e}")

def signal_handler(sig, frame):
    """Handle graceful shutdown."""
    logging.info("Shutting down DDoS mitigation bot...")
    for ip in list(blocked_ips):
        unblock_ip(ip)
    sys.exit(0)

def main():
    """Main function to start the DDoS mitigation bot."""
    print("""
    ╔══════════════════════════════════════════════════════╗
    ║         Active DDoS Mitigation Bot                   ║
    ║    Coded by Pakistani White Hat Hacker               ║
    ║         Mr Sabaz Ali Khan                           ║
    ╚══════════════════════════════════════════════════════╝
    """)

    # Start the block expiry checker in a separate thread
    expiry_thread = threading.Thread(target=check_block_expiry, daemon=True)
    expiry_thread.start()

    # Register signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Start sniffing traffic
    start_sniffing()

if __name__ == "__main__":
    main()