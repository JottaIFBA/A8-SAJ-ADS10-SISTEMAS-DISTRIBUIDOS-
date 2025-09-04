import socket

def post_message(node_host, node_port, username, password, message):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((node_host, node_port))
    s.send(f"POST:{username}:{password}:{message}".encode())
    resp = s.recv(1024).decode()
    print(resp)
    s.close()

def read_messages(node_host, node_port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((node_host, node_port))
    s.send("GET".encode())
    resp = s.recv(4096).decode()
    msgs = resp.split("|")
    print("=== Mural ===")
    for m in msgs:
        print(m)
    s.close()

if name == "__main__":
    host = "127.0.0.1"
    port = int(input("Informe porta do nó (5001/5002/5003): "))
    while True:
        print("\n1- Ler mensagens\n2- Postar mensagem\n3- Sair")
        opt = input("Escolha: ")
        if opt == "1":
            read_messages(host, port)
        elif opt == "2":
            user = input("Usuário: ")
            pwd = input("Senha: ")
            msg = input("Mensagem: ")
            post_message(host, port, user, pwd, msg)
        elif opt == "3":
            break
