import socket
import threading
import time

class Node:
    def __init__(self, node_id, host, port, other_nodes):
        """
        Inicializa o nó do mural.
        node_id: ID do nó
        host, port: endereço local
        other_nodes: lista de tuplas (host, port) dos outros nós
        """
        self.node_id = node_id
        self.host = host
        self.port = port
        self.other_nodes = other_nodes  # nós para replicação
        self.messages = []  # cópia local do mural
        self.users = {"alice": "123", "bob": "456"}  # autenticação simples
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.running = True

    def start_server(self):
        """
        Inicializa o servidor TCP para receber mensagens de outros nós e clientes
        """
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"[{self.node_id}] Servidor iniciado em {self.host}:{self.port}")
        threading.Thread(target=self.accept_clients, daemon=True).start()

    def accept_clients(self):
        """
        Aceita conexões de clientes ou nós
        """
        while self.running:
            try:
                client_socket, addr = self.server_socket.accept()
                threading.Thread(target=self.handle_connection, args=(client_socket,), daemon=True).start()
            except:
                continue

    def handle_connection(self, client_socket):
        """
        Trata requisições de envio de mensagem
        """
        try:
            data = client_socket.recv(1024).decode()
            if data.startswith("POST:"):
                # Formato POST:username:senha:mensagem
                parts = data.split(":", 3)
                username, password, msg = parts[1], parts[2], parts[3]
                if self.authenticate(username, password):
                    self.add_message(f"{username}: {msg}")
                    client_socket.send(f"Mensagem postada com sucesso!".encode())
                else:
                    client_socket.send("Falha na autenticação!".encode())
            elif data.startswith("SYNC:"):
                # Recebe lista de mensagens de outro nó
                new_msgs = data[5:].split("|")
                for m in new_msgs:
                    if m not in self.messages:
                        self.messages.append(m)
            elif data.startswith("GET"):
                # Retorna todas as mensagens
                client_socket.send("|".join(self.messages).encode())
        except Exception as e:
            print(f"Erro ao tratar conexão: {e}")
        finally:
            client_socket.close()

    def authenticate(self, username, password):
        return self.users.get(username) == password

    def add_message(self, message):
        """
        Adiciona mensagem localmente e replica para outros nós
        """
        self.messages.append(message)
        threading.Thread(target=self.replicate_message, args=(message,), daemon=True).start()
        print(f"[{self.node_id}] Nova mensagem: {message}")

    def replicate_message(self, message):
        """
        Envia a mensagem para outros nós (consistência eventual)
        """
        for host, port in self.other_nodes:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(2)
                s.connect((host, port))
                s.send(f"SYNC:{message}".encode())
                s.close()
            except:
                # nó temporariamente indisponível, será sincronizado depois
                continue

    def stop(self):
        self.running = False
        self.server_socket.close()
