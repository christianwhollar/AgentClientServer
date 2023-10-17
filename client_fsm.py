import socket
import os
import requests
from dotenv import load_dotenv
from huggingface_hub import login
import re
from contextlib import redirect_stdout

load_dotenv()
HUGGINGFACE_API_TOKEN = os.getenv('HUGGINGFACE_API_TOKEN')

class NullDevice():
    def write(self, s): pass

with redirect_stdout(NullDevice()):
    login(token=HUGGINGFACE_API_TOKEN, add_to_git_credential=True)

HOST = '127.0.0.1'
PORT = 65432

class ClientFSM:
    def __init__(self, name, recipient, initial_state='Listen'):
        self.name = name
        self.recipient = recipient
        self.state = initial_state
        self.turns = 5
        self.history = f'[{self.name}] My name is {self.name}. Your name is {self.recipient}. [{self.name}]'

    def extract_message(self, text):
        # Matches the pattern [timestamp] MESSAGE: Actual Message
        match = re.search(r'\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\] MESSAGE: (.+)', text)
        return match.group(1) if match else None
    
    def query(self, payload):
        API_URL = "https://api-inference.huggingface.co/models/meta-llama/Llama-2-70b-chat-hf"
        headers = {"Authorization": f"Bearer {HUGGINGFACE_API_TOKEN}"}
        response = requests.post(API_URL, headers=headers, json=payload)
        return response.json()

    def mock_chatgpt_response(self):
        output = self.query({
            "inputs": self.history,
        })
        try:
            generated_text = output[0].get('generated_text', '')
            if 'User: ' in generated_text:
                response = generated_text.split('User: ')[-1]
            else:
                response = generated_text  # or some default value or error handling
        except IndexError:
            response = "Error: Unexpected output format."

        return response

    def speak(self, client_socket):
        msg = self.mock_chatgpt_response()
        client_socket.sendall(msg.encode())

    def listen(self, client_socket):
        try:
            data = client_socket.recv(1024)
            if data:
                received_msg = data.decode()
                return received_msg
            else:
                print("Connection closed by server.")
                return None  # or handle it in another way
        except socket.error:
            return None  # or handle it in another way

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((HOST, PORT))
            
            if self.name == "Sultan":
                initial_message = f"{self.name} says: Hi {self.recipient}!"
                self.history += f'[{self.name}] {initial_message}'
                client_socket.sendall(initial_message.encode())
            
            while self.turns > 0:
                
                received_msg = self.listen(client_socket)
                if received_msg is None:
                    break
                elif 'MESSAGE:' in received_msg: 
                    received_msg = received_msg.split('MESSAGE:')[-1]
                if received_msg:
                    self.history += f'[{self.recipient}] {received_msg}'
                    self.speak(client_socket)
                    self.turns -= 1

