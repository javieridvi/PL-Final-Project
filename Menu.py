import Utilities
from termcolor import colored
import socket
import sys
import os
import threading


class MenuStateException(Exception):
    INVALID = 'Invalid state, cannot instantiate: '

    def __init__(self, state: str, current_state: str) -> None:
        print(colored('{}{} while current state is: {}.'.format(self.INVALID, state, current_state), 'red'))
        sys.exit(1)


class ConsoleMenu():
    CLIENT = 'client'
    SERVER = 'server'
    UNINITIALIZED = 'uninitialized'
    PROMPT = colored('UserInput', 'cyan') + colored(' --> ', 'magenta')
    PPATH = './resources'

    def __init__(self):
        self.parser = Utilities.Parser()
        self.connection: ServerManager = None
        self.state = 'uninitialized'
        self.parser.set_menu(self)
        self.terminate_connection = False

    def run_menu(self):
        while True:
            try:
                self.greetings_menu()
                self.get_user_input()

                break
            except Exception as e:
                print(e)
                self.invalid_command()
                os._exit(1)

    def create_server(self, host: str, port: str):
        self.verify_state(self.SERVER)
        self.set_state(self.SERVER)
        self.connection = ServerManager(self.SERVER, host, int(port), user_server_input=self.get_user_input)

    def connect_to_server(self, host: str, port: str):
        self.verify_state(self.state)
        self.set_state(self.CLIENT)
        self.connection = ServerManager(self.CLIENT, host, int(port))
        try:
            self.manage_client()
        except:
            print(colored('Server disconected.', 'red'))
            os._exit(1)

    def get_user_input(self):
        msg = self.parser.parse(input(self.PROMPT))
        return msg

    def send_message(self, msg: str) -> None:
        new_msg = 'MESSAGE: ' + msg
        self.print_action('SEND', new_msg)

    def print_action(self, command: str, msg: str) -> None:
        print(colored('Command: ', 'green') + colored(command, 'yellow') + ' ' + colored('msg', 'white'))

    def invalid_command(self) -> None:
        print(colored('That command is invalid in the current state!', 'red'))

    def verify_state(self, t_state: str):
        if self.state != self.UNINITIALIZED:
            raise MenuStateException(t_state, self.state)

    def set_state(self, state: str) -> None:
        self.state = state

    def greetings_menu(self):
        print(colored('Server Manager', 'green') + colored('\nStart a sever or connect to a server?', 'yellow'))

    def quit_program(self):
        print(colored('Program will now exit.', 'yellow'))
        os._exit(1)


    def manage_client(self) -> None:
        while True:
            if self.terminate_connection:
                self.connection.close_connection()
                self.quit_program()

            message = self.get_user_input()
            self.connection.client_send_msg(message)
            self.connection.client_receive_msg()


class ServerManager():
    MAX_BYTES: int = 1024

    def __init__(self, state: str, host: str, port: int, user_server_input=None) -> None:
        self.address: str = host
        self.port: int = port
        self.current_connection = None
        self.user_input_on_server = user_server_input
        self.thread_list = []
        if state == ConsoleMenu.CLIENT:
            self.state: str = ConsoleMenu.CLIENT
            self.create_client(host, port)
            print(colored('Created client', 'cyan'))
        elif state == ConsoleMenu.SERVER:
            self.state: str = ConsoleMenu.SERVER
            print(colored('Created Server', 'cyan'))
            self.create_server(host, port)
        else:
            print(colored('No valid state give.', 'red'))

    def create_server(self, host: str, port: int) -> None:
        self.current_connection: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.current_connection.bind((host, port))
        self.current_connection.listen()
        while True:
            connection, addr = self.current_connection.accept()
            if connection:
                worker = threading.Thread(target=self.attend_server_clients, args=[connection, addr])
                self.thread_list.append(worker)
                worker.start()

    def create_client(self, host: str, port: int) -> None:
        self.current_connection: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.current_connection.connect((host, port))

    def client_send_msg(self, msg: str) -> None:
        message = colored(f'Message from {self.address} --> ', 'blue') + msg
        self.current_connection.sendall(message.encode())

    def client_receive_msg(self) -> str:
        print(colored('Waiting to receive', 'yellow'))
        while True:
            data = self.current_connection.recv(self.MAX_BYTES)
            if data:
                print(data.decode())
                break

    def close_connection(self):
        self.current_connection.close()

    def get_connection(self) -> socket.socket:
        return self.current_connection

    def server_receive_msg(self, sock: socket.socket, address: str) -> str:
        print(colored(f'Waiting response from {address}', 'yellow'))
        while True:
            try:
                data = sock.recv(ServerManager.MAX_BYTES)
                if data:
                    print(data.decode())
                    break
            except:
                print(colored('Shutdown Server', 'red'))
                os._exit(1)

    def server_send_msg(self, sock: socket.socket, message: str) -> None:
        try:
            msg = colored(f'Message from server --> ', 'green') + message
            msg = msg.encode()
            sock.sendall(msg)
        except:
            sock.sendall(colored('Server is disconnecting...', 'red').encode())

    def attend_server_clients(self, sock: socket.socket, addr: str) -> None:
        print(colored(f'Conected to {addr}', 'blue'))
        while True:
            self.server_receive_msg(sock, addr)
            user_msg = self.user_input_on_server()
            self.server_send_msg(sock, user_msg)


