import os
import socket
import threading
import base64
import signal
import sys
from cryptography.fernet import Fernet


def generate_key():
    key = base64.urlsafe_b64encode(os.urandom(32))
    return key.decode('utf-8')


def play_sound():
    try:
        if sys.platform.startswith('win'):
            import winsound
            for i in range(3):
                winsound.MessageBeep()
        elif sys.platform.startswith('darwin'):
            import subprocess
            for i in range(3):
                subprocess.call(['afplay', '/System/Library/Sounds/Glass.aiff'])
        else:
            import subprocess
            for i in range(3):
                subprocess.call(['paplay', '/usr/share/sounds/freedesktop/stereo/message.oga'])
    except Exception as e:
        print(f"Error playing sound: {e}")


class ServerNode:

    def __init__(self):
        self.node = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        port_and_ip = ('127.0.0.1', 12345)
        self.node.bind(port_and_ip)
        self.node.listen(4)
        self.clients = []
        self.lock = threading.Lock()
        print("Waiting for connections...")

    def broadcast(self, message, conn=None):
        encrypted_message = fernet.encrypt(message.encode())
        with self.lock:
            for client in self.clients:
                if client != conn:
                    try:
                        client.send(encrypted_message)
                    except Exception as e:
                        print(f"Error sending message to a client: {e}")

    def handle_client(self, conn, addr):
        with self.lock:
            self.clients.append(conn)
        print(f"Connected by {addr}")
        try:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                message = fernet.decrypt(data).decode()
                print(message)
                play_sound()
                self.broadcast(message, conn)
        except Exception as e:
            print(f"Error receiving message: {e}")
        finally:
            with self.lock:
                self.clients.remove(conn)
            conn.close()

    def start(self):
        try:
            while True:
                conn, addr = self.node.accept()
                client_thread = threading.Thread(target=self.handle_client, args=(conn, addr))
                client_thread.daemon = True
                client_thread.start()
        except Exception as e:
            print(f"Error: {e}")
        finally:
            self.close_connection()

    def send_sms(self, sms):
        try:
            message = f"Server: {sms}"
            self.broadcast(message)
        except Exception as e:
            print(f"Error sending message: {e}")

    def close_connection(self):
        with self.lock:
            for client in self.clients:
                client.close()
            self.node.close()
        print("Connection closed.")

    def main(self):
        try:
            while True:
                message = input()
                if message.lower() == 'exit':
                    self.close_connection()
                    break
                self.send_sms(message)
        except KeyboardInterrupt:
            self.close_connection()
            sys.exit(0)
        except Exception as e:
            print(f"Error: {e}")
            self.close_connection()


def signal_handler(sig, frame):
    print('Closing connection...')
    server.close_connection()
    sys.exit(0)


if __name__ == "__main__":
    shared_secret = generate_key()
    print(f"Shared secret: {shared_secret}")
    fernet = Fernet(shared_secret)

    server = ServerNode()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    server_thread = threading.Thread(target=server.start)
    server_thread.daemon = True
    server_thread.start()

    server.main()
