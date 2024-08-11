import sys
import signal
import typer
from curses import wrapper
from cryptography.fernet import Fernet
from client.client import ClientNode
from utils.utils import print_cli_welcome_text, clear_console


def signal_handler(sig, frame):
    client.close_connection()
    sys.exit(0)


if __name__ == "__main__":
    print_cli_welcome_text()

    username = typer.prompt("Enter your username")
    ip_address = typer.prompt("Enter Server IP address", default="127.0.0.1")
    server_port = typer.prompt("Enter server port", default=12345, type=int)
    shared_secret = typer.prompt("Enter shared secret")

    fernet = Fernet(shared_secret)

    clear_console()

    client = ClientNode(ip_address, server_port, username, fernet)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    wrapper(client.main)
