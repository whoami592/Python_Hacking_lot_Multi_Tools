# Cowrie - Advanced SSH & Telnet Honeypot
# Coded by Pakistani White Hat Hacker Mr. Sabaz Ali Khan

import socket
import paramiko
import threading
import time
import logging
from paramiko.py3compat import u

# Banner to display
BANNER = """
************************************************************
*                                                          *
*   Cowrie - Advanced SSH & Telnet Honeypot                *
*   Coded by Pakistani White Hat Hacker Mr. Sabaz Ali Khan *
*                                                          *
************************************************************
"""

# Set up logging
logging.basicConfig(filename='honeypot.log', level=logging.INFO, 
                    format='%(asctime)s - %(message)s')

class FakeServer(paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
        logging.info(f"Login attempt: username={username}, password={password}")
        print(f"Captured login: {username}:{password}")
        return paramiko.AUTH_FAILED

    def get_allowed_auths(self, username):
        return 'password'

    def check_channel_shell_request(self, channel):
        self.event.set()
        return True

    def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight, modes):
        return True

def handle_connection(client, addr):
    print(f"Connection from {addr}")
    transport = paramiko.Transport(client)
    transport.add_server_key(paramiko.RSAKey.generate(2048))  # Generate a temporary key
    server = FakeServer()
    try:
        transport.start_server(server=server)
    except paramiko.SSHException:
        print("SSH negotiation failed.")
        return

    chan = transport.accept(20)
    if chan is None:
        print("No channel.")
        return

    server.event.wait(10)
    if not server.event.is_set():
        print("Client never asked for a shell.")
        chan.close()
        return

    chan.send("Welcome to fake server!\r\n")
    chan.send("Last login: Never\r\n")
    chan.send("$ ")

    while True:
        try:
            command = chan.recv(1024).decode('utf-8').strip()
            if not command:
                break
            logging.info(f"Command from {addr}: {command}")
            print(f"Command: {command}")
            if command.lower() == 'exit':
                break
            chan.send(f"{command}: command not found\r\n$ ")
        except Exception as e:
            print(f"Error: {e}")
            break

    chan.close()
    transport.close()

def start_honeypot(host='0.0.0.0', port=2222):
    print(BANNER)
    print(f"Starting honeypot on {host}:{port}")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(100)

    while True:
        client, addr = server_socket.accept()
        threading.Thread(target=handle_connection, args=(client, addr), daemon=True).start()

# For Telnet, we can add a simple server (basic implementation)
class TelnetHandler:
    def handle(self, client, addr):
        print(f"Telnet connection from {addr}")
        client.send(b"Welcome to fake telnet server!\r\n")
        client.send(b"Login: ")
        username = client.recv(1024).decode('utf-8').strip()
        client.send(b"Password: ")
        password = client.recv(1024).decode('utf-8').strip()
        logging.info(f"Telnet login attempt: username={username}, password={password}")
        print(f"Telnet captured: {username}:{password}")
        client.send(b"Access denied.\r\n")
        client.close()

def start_telnet_honeypot(host='0.0.0.0', port=2323):
    print(f"Starting Telnet honeypot on {host}:{port}")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(100)

    while True:
        client, addr = server_socket.accept()
        handler = TelnetHandler()
        threading.Thread(target=handler.handle, args=(client, addr), daemon=True).start()

if __name__ == "__main__":
    # Start SSH honeypot in a thread
    ssh_thread = threading.Thread(target=start_honeypot, daemon=True)
    ssh_thread.start()
    
    # Start Telnet honeypot
    start_telnet_honeypot()