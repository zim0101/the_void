import os
import sys
import base64


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


def clear_console():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')


def generate_key():
    key = base64.urlsafe_b64encode(os.urandom(32))
    return key.decode('utf-8')
