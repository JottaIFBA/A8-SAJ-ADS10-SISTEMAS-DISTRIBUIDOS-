from node import Node
import threading
import time

# Configuração dos nós
nodes_info = [
    ("Node1", "127.0.0.1", 5001),
    ("Node2", "127.0.0.1", 5002),
    ("Node3", "127.0.0.1", 5003)
]

# Criar instâncias de nós com referência aos outros nós
nodes = []
for i, (nid, host, port) in enumerate(nodes_info):
    others = [(h, p) for j, (_, h, p) in enumerate(nodes_info) if j != i]
    node = Node(nid, host, port, others)
    nodes.append(node)

# Iniciar servidores
for node in nodes:
    threading.Thread(target=node.start_server, daemon=True).start()

print("Todos os nós iniciados. Pressione Ctrl+C para parar.")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    for node in nodes:
        node.stop()
