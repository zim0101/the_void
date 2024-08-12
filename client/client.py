# -*- coding: utf-8 -*-

import sys
import socket
import threading
import curses
from utils.utils import play_sound


class ChatUI:

    def __init__(self, stdscr):
        self.input_win = None
        self.chat_win = None
        self.stdscr = stdscr
        self.initiate_ui()

    def initiate_ui(self):
        curses.curs_set(1)
        curses.start_color()
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
        self.stdscr.bkgd(' ', curses.color_pair(1))
        self.stdscr.clear()
        self.stdscr.refresh()

        height, width = self.stdscr.getmaxyx()
        self.chat_win = curses.newwin(height - 6, width, 0, 0)
        self.input_win = curses.newwin(6, width, height - 6, 0)

        self.chat_win.bkgd(' ', curses.color_pair(1))
        self.input_win.bkgd(' ', curses.color_pair(1))

        self.chat_win.scrollok(True)
        self.chat_win.idlok(True)

    def redraw_chat_window(self, messages):
        self.chat_win.clear()
        self.chat_win.box()
        height, width = self.chat_win.getmaxyx()
        start_index = max(0, len(messages) - (height - 2))

        for idx, msg in enumerate(messages[start_index:], start=1):
            if idx >= height - 1:
                break
            self.chat_win.addstr(idx, 1, msg[:width - 2])

        self.chat_win.refresh()

    def redraw_input_window(self, input_lines, scroll_pos):
        self.input_win.clear()
        self.input_win.box()

        height, width = self.input_win.getmaxyx()
        start_line = max(0, len(input_lines) - (height - 3) + scroll_pos)
        for idx, line in enumerate(input_lines[start_line:start_line + height - 3], start=1):
            truncated_line = line[:width - 2]
            self.input_win.addstr(idx, 1, truncated_line)

        self.input_win.refresh()

    def resize_windows(self):
        new_height, new_width = self.stdscr.getmaxyx()
        curses.resizeterm(new_height, new_width)
        self.chat_win.resize(new_height - 6, new_width)
        self.input_win.resize(6, new_width)
        self.input_win.mvwin(new_height - 6, 0)
        self.stdscr.refresh()


class ClientNode:

    def __init__(self, ip, port, username, fernet):
        port_and_ip = (ip, port)

        self.username = username
        self.fernet = fernet
        self.node = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

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

    def receive_sms(self, chat_ui):
        while True:
            try:
                data = self.node.recv(1024)
                if not data:
                    break
                decrypted_message = self.fernet.decrypt(data).decode()
                if decrypted_message == "__clear__":
                    self.messages.clear()
                    chat_ui.initiate_ui()
                else:
                    self.messages.append(decrypted_message)
                    chat_ui.redraw_chat_window(self.messages)
                    play_sound()
            except Exception as e:
                self.messages.append(f"Error receiving message: {e}")
                break

    def close_connection(self):
        try:
            if self.node:
                self.node.close()
            self.messages.append("Connection closed.")
        except Exception as e:
            self.messages.append(f"Error closing connection: {e}")

    def main(self, stdscr):
        chat_ui = ChatUI(stdscr)

        always_receive = threading.Thread(target=self.receive_sms, args=(chat_ui,))
        always_receive.daemon = True
        always_receive.start()

        input_lines = []
        scroll_pos = 1

        while True:
            new_height, new_width = stdscr.getmaxyx()
            if chat_ui.chat_win.getmaxyx() != (new_height - 6, new_width):
                chat_ui.resize_windows()
                chat_ui.redraw_chat_window(self.messages)

            chat_ui.redraw_input_window(input_lines, scroll_pos)

            key = chat_ui.input_win.getch()

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
                    chat_ui.redraw_chat_window(self.messages)
                    input_lines.clear()
                    scroll_pos = 0
            elif key == curses.KEY_DOWN:
                if scroll_pos > 0:
                    scroll_pos -= 1
            elif key == curses.KEY_UP:
                if len(input_lines) - scroll_pos > chat_ui.input_win.getmaxyx()[0] - 3:
                    scroll_pos += 1
            elif key != curses.ERR:
                if not input_lines or len(input_lines[-1]) >= chat_ui.input_win.getmaxyx()[1] - 2:
                    input_lines.append("")
                    if len(input_lines) > chat_ui.input_win.getmaxyx()[0] - 3:
                        scroll_pos += 1
                input_lines[-1] += chr(key)
