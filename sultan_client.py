from client_fsm import ClientFSM

if __name__ == "__main__":
    sultan = ClientFSM("Sultan", "Christian", initial_state='Speak')
    sultan.run()
