import os
import time

def check_downloads():
    while True:
        if not os.listdir('/path/to/downloads'):
            print("Shutting down...")
            os.system("shutdown /s /t 1")
        time.sleep(60)

check_downloads()