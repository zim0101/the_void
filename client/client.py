# -*- coding: utf-8 -*-

import os
import socket
import threading
import signal
import sys
import curses
import typer
from cryptography.fernet import Fernet


def print_cli_welcome_text():
    print("""
        ████████╗██╗░░██╗███████╗ ██╗░░░██╗░█████╗░██╗██████╗░
        ╚══██╔══╝██║░░██║██╔════╝ ██║░░░██║██╔══██╗██║██╔══██╗
        ░░░██║░░░███████║█████╗░░ ╚██╗░██╔╝██║░░██║██║██║░░██║
        ░░░██║░░░██╔══██║██╔══╝░░ ░╚████╔╝░██║░░██║██║██║░░██║
        ░░░██║░░░██║░░██║███████╗ ░░╚██╔╝░░╚█████╔╝██║██████╔╝
        ░░░╚═╝░░░╚═╝░░╚═╝╚══════╝ ░░░╚═╝░░░░╚════╝░╚═╝╚═════╝░

        WELCOME TO THE VOID, WHERE EVERYONE IS ANONYMOUS!!
        """)


def clear_console():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')


def signal_handler(sig, frame):
    client.close_connection()
    sys.exit(0)


class ClientNode:

    def __init__(self, ip, port):
        self.node = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        port_and_ip = (ip, port)
        try:
            self.node.connect(port_and_ip)
            self.messages = []
        except Exception as e:
            sys.exit(1)

    def send_sms(self, sms):
        try:
            message = f"{username}: {sms}"
            self.node.send(fernet.encrypt(message.encode()))
        except Exception as e:
            self.messages.append(f"Error sending message: {e}")

    def receive_sms(self, chat_win):
        while True:
            try:
                data = self.node.recv(1024)
                if not data:
                    break
                self.messages.append(fernet.decrypt(data).decode())
                self.display_messages(chat_win)
            except Exception as e:
                self.messages.append(f"Error receiving message: {e}")
                break

    def display_messages(self, chat_win):
        chat_win.clear()
        chat_win.box()
        height, width = chat_win.getmaxyx()

        start_index = max(0, len(self.messages) - (height - 2))

        for idx, msg in enumerate(self.messages[start_index:], start=1):
            if idx >= height - 1:
                break
            chat_win.addstr(idx, 1, msg[:width - 2])

        chat_win.refresh()

    def close_connection(self):
        try:
            if self.node:
                self.node.close()
            self.messages.append("Connection closed.")
        except Exception as e:
            self.messages.append(f"Error closing connection: {e}")

    def main(self, stdscr):
        curses.curs_set(1)
        curses.start_color()

        # Define a color pair (pair number 1) with white text on black background
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)

        # Set background color to black for the whole screen
        stdscr.bkgd(' ', curses.color_pair(1))
        stdscr.clear()
        stdscr.refresh()

        # Set up initial screen size
        height, width = stdscr.getmaxyx()
        chat_win = curses.newwin(height - 6, width, 0, 0)
        input_win = curses.newwin(6, width, height - 6, 0)

        # Apply the black background color to the chat and input windows
        chat_win.bkgd(' ', curses.color_pair(1))
        input_win.bkgd(' ', curses.color_pair(1))

        chat_win.scrollok(True)
        chat_win.idlok(True)

        # Start the receiving thread
        always_receive = threading.Thread(target=self.receive_sms, args=(chat_win,))
        always_receive.daemon = True
        always_receive.start()

        input_lines = []
        scroll_pos = 1

        while True:
            # Check if the terminal was resized
            new_height, new_width = stdscr.getmaxyx()
            if height != new_height or width != new_width:
                height, width = new_height, new_width
                curses.resizeterm(height, width)

                # Resize windows to fit the new terminal size
                chat_win.resize(height - 6, width)
                input_win.resize(6, width)
                input_win.mvwin(height - 6, 0)

                # Redisplay messages after resizing
                self.display_messages(chat_win)

            input_win.clear()
            input_win.box()

            # Display the current visible input lines
            start_line = max(0, len(input_lines) - (height - 3) + scroll_pos)
            for idx, line in enumerate(input_lines[start_line:start_line + height - 3], start=1):
                truncated_line = line[:width - 2]  # Truncate line if it's too long
                input_win.addstr(idx, 1, truncated_line)

            input_win.refresh()

            key = input_win.getch()

            if key == curses.KEY_BACKSPACE or key == 127:
                if input_lines and input_lines[-1]:
                    input_lines[-1] = input_lines[-1][:-1]
                elif input_lines:
                    input_lines.pop()
                    scroll_pos = max(0, scroll_pos - 1)
            elif key == curses.KEY_ENTER or key == 10:
                message = "\n".join(input_lines)
                if message.lower() == 'exit':
                    self.close_connection()
                    break
                elif message.lower() == '//':
                    chat_win.clear()
                    chat_win.refresh()
                    self.send_sms(message)
                elif message.lower() == '/':
                    self.close_connection()
                    break
                else:
                    self.send_sms(message)
                    self.messages.append(f"{username}: {message}")
                    self.display_messages(chat_win)
                    input_lines.clear()
                    scroll_pos = 0
            elif key == curses.KEY_DOWN:
                if scroll_pos > 0:
                    scroll_pos -= 1
            elif key == curses.KEY_UP:
                if len(input_lines) - scroll_pos > height - 3:
                    scroll_pos += 1
            elif key != curses.ERR:
                if not input_lines or len(input_lines[-1]) >= width - 2:
                    input_lines.append("")
                    if len(input_lines) > height - 3:
                        scroll_pos += 1
                input_lines[-1] += chr(key)


if __name__ == "__main__":
    print_cli_welcome_text()

    username = typer.prompt("Enter your username: ", default="Anonymous")
    ip_address = typer.prompt("Enter Server IP address: ", default="127.0.0.1")
    server_port = typer.prompt("Enter server port: ", default=12345, type=int)
    shared_secret = typer.prompt("Enter shared secret: ", default="7pVvuz6F8K_6swmuHOfvZ-sZhNPfTsinImRGcukIjng=")
    fernet = Fernet(shared_secret)

    clear_console()

    client = ClientNode(ip_address, server_port)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    curses.wrapper(client.main)
