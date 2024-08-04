# -*- coding: utf-8 -*-

import sys
import socket
import threading
import curses
from utils.utils import play_sound


class ClientNode:

    def __init__(self, ip, port, username, fernet):
        self.username = username
        self.fernet = fernet
        self.node = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        port_and_ip = (ip, port)
        try:
            self.node.connect(port_and_ip)
            self.messages = []
        except Exception as e:
            sys.exit(1)

    def send_sms(self, sms):
        try:
            message = f"{self.username}: {sms}"
            self.node.send(self.fernet.encrypt(message.encode()))
        except Exception as e:
            self.messages.append(f"Error sending message: {e}")

    def receive_sms(self, chat_win):
        while True:
            try:
                data = self.node.recv(1024)
                if not data:
                    break
                decrypted_message = self.fernet.decrypt(data).decode()
                self.messages.append(decrypted_message)
                self.display_messages(chat_win)
                play_sound()
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

        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)

        stdscr.bkgd(' ', curses.color_pair(1))
        stdscr.clear()
        stdscr.refresh()

        height, width = stdscr.getmaxyx()
        chat_win = curses.newwin(height - 6, width, 0, 0)
        input_win = curses.newwin(6, width, height - 6, 0)

        chat_win.bkgd(' ', curses.color_pair(1))
        input_win.bkgd(' ', curses.color_pair(1))

        chat_win.scrollok(True)
        chat_win.idlok(True)

        always_receive = threading.Thread(target=self.receive_sms, args=(chat_win,))
        always_receive.daemon = True
        always_receive.start()

        input_lines = []
        scroll_pos = 1

        while True:
            new_height, new_width = stdscr.getmaxyx()
            if height != new_height or width != new_width:
                height, width = new_height, new_width
                curses.resizeterm(height, width)

                chat_win.resize(height - 6, width)
                input_win.resize(6, width)
                input_win.mvwin(height - 6, 0)

                self.display_messages(chat_win)

            input_win.clear()
            input_win.box()

            start_line = max(0, len(input_lines) - (height - 3) + scroll_pos)
            for idx, line in enumerate(input_lines[start_line:start_line + height - 3], start=1):
                truncated_line = line[:width - 2]
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
                elif message.lower() == '/':
                    self.send_sms("left the chat!")
                    self.close_connection()
                    break
                else:
                    self.send_sms(message)
                    self.messages.append(f"{self.username}: {message}")
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
