import os
import platform
import subprocess
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
    current_dir = os.path.dirname(__file__)
    sound_file_path = os.path.join(current_dir, '..', 'resources', 'audio', 'notification.wav')

    if platform.system() == 'Windows':
        try:
            import winsound
            winsound.PlaySound(sound_file_path, winsound.SND_FILENAME)
        except ImportError:
            print("Error: winsound module not found. Cannot play sound.")
        except Exception as e:
            print(f"Error playing sound on Windows: {e}")
    elif platform.system() == 'Darwin':  # macOS
        try:
            subprocess.call(['aplay', sound_file_path], stdout=subprocess.DEVNULL)
        except FileNotFoundError:
            print("Error: afplay command not found. Cannot play sound.")
        except subprocess.CalledProcessError as e:
            print(f"Error playing sound on macOS: {e}")
        except Exception as e:
            print(f"Error playing sound on macOS: {e}")
    else:  # Linux
        try:
            subprocess.call(['aplay', sound_file_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except FileNotFoundError:
            print("Error: aplay command not found. Cannot play sound.")
        except subprocess.CalledProcessError as e:
            print(f"Error playing sound on Linux: {e}")
        except Exception as e:
            print(f"Error playing sound on Linux: {e}")


def clear_console():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')


def generate_key():
    key = base64.urlsafe_b64encode(os.urandom(32))
    return key.decode('utf-8')
