import os
import sys
import signal
import typer
from curses import wrapper
from cryptography.fernet import Fernet
from urllib.parse import urlparse
from client.client import ClientNode
from utils.utils import print_cli_welcome_text, clear_console


def signal_handler(sig, frame):
    client.close_connection()
    sys.exit(0)


if __name__ == "__main__":
    print_cli_welcome_text()

    username = typer.prompt("Enter your anonymous username")
    tcp_url = typer.prompt("Enter TCP server URL (e.g. tcp://<ip>:<port>)")
    shared_secret = typer.prompt("Enter shared secret")

    parsed_url = urlparse(tcp_url)
    ip_address = parsed_url.hostname
    server_port = parsed_url.port

    fernet = Fernet(shared_secret)

    clear_console()

    client = ClientNode(ip_address, server_port, username, fernet)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    wrapper(client.main)
