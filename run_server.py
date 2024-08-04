import sys
import signal
import threading
from cryptography.fernet import Fernet
from utils.utils import generate_key, print_cli_welcome_text
from server.server import ServerNode


def signal_handler(sig, frame):
    print('Closing connection...')
    server.close_connection()
    sys.exit(0)


if __name__ == "__main__":
    print_cli_welcome_text()

    shared_secret = generate_key()
    print(f"Shared secret: {shared_secret}")
    fernet = Fernet(shared_secret)

    server = ServerNode(fernet)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    server_thread = threading.Thread(target=server.start)
    server_thread.daemon = True
    server_thread.start()

    server.main()
