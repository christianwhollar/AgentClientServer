import subprocess
import time

def main():
    server = subprocess.Popen(["python", "server.py"])
    time.sleep(2)  # Give the server some time to start

    sultan = subprocess.Popen(["python", "sultan_client.py"])
    sultan.communicate()  # Wait for Sultan to finish
    
    christian = subprocess.Popen(["python", "christian_client.py"])
    christian.communicate()

    server.communicate()

if __name__ == "__main__":
    main()
