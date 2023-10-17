import socket
import threading
import re
from datetime import datetime

class ChatServer:

    def __init__(self, host='127.0.0.1', port=65432):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen()
        print(f"Server listening on {host}:{port}")
        self.active_clients = []
        self.connections = []
        self.run_server = True

    def get_last_sentence(self, text):
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return sentences[-1] if sentences else ""

    def handle_client(self, client_socket):
        try:
            while True:
                data = client_socket.recv(2048)
                if not data:
                    print('Client disconnected')
                    self.run_server = False
                    break
         
                decoded_data = data.decode()
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                log_entry = f"[{timestamp}] MESSAGE: {decoded_data}"

                # Print the timestamp and message
            
                print(log_entry)
                
                # Write to the log file
                with open('chat_log.txt', 'a') as f:
                    f.write(log_entry + '\n')

                # Send only the decoded data (message) back
                client_socket.send(decoded_data.encode())
        except ConnectionAbortedError:
            print('Client closed the connection.')
            self.run_server = False
        except Exception as e:
            print(f'Unexpected error: {e}')
            self.run_server = False
        finally:
            client_socket.close()

    def run(self):
        try:
            while self.run_server:
                conn, addr = self.server.accept()
                print(f"Connected by {addr}")
                client_handler = threading.Thread(target=self.handle_client, args=(conn,))
                self.active_clients.append(client_handler)
                self.connections.append(conn)
                client_handler.start()
        except Exception as e:
            print(f"Error: {e}")
        finally:
            for conn in self.connections:
                conn.close()
            self.server.close()

if __name__ == "__main__":
    server = ChatServer()
    server.run()
