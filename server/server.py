import sys
import socket
import threading


class ServerNode:

    def __init__(self, fernet):
        self.node = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        port_and_ip = ('127.0.0.1', 12345)
        self.fernet = fernet
        self.node.bind(port_and_ip)
        self.node.listen(4)
        self.clients = []
        self.lock = threading.Lock()
        print("Waiting for connections...")

    def broadcast(self, message, conn=None):
        encrypted_message = self.fernet.encrypt(message.encode())
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
                message = self.fernet.decrypt(data).decode()
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

