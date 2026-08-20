import socket
import sys
import threading

HOST, PORT = "127.0.0.1", 5001

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# ATENCAO: no Windows, SO_REUSEADDR NAO significa o mesmo que no Linux.
# Aqui ele permite que VARIOS processos escutem a MESMA porta ao mesmo tempo,
# entao um servidor antigo esquecido rodando continua roubando as conexoes e
# o servidor novo sobe "com sucesso" sem nunca receber ninguem.
# SO_EXCLUSIVEADDRUSE garante bind exclusivo: se a porta ja estiver em uso, falha.
if hasattr(socket, "SO_EXCLUSIVEADDRUSE"):
    s.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
else:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

try:
    s.bind((HOST, PORT))
except OSError as erro:
    print(f"[servidor] porta {PORT} ja esta em uso: {erro}", flush=True)
    print("[servidor] feche o servidor antigo ou troque a PORT.", flush=True)
    sys.exit(1)

s.listen()

print(f"[servidor] ouvindo em {HOST}:{PORT}", flush=True)


def atender_cliente(conexao, endereco):
    print(f"[servidor] cliente conectado: {endereco}", flush=True)

    while True:
        dado = conexao.recv(1024)

        if not dado:
            break

        print(
            f"[servidor] {endereco} enviou: {dado.decode()}",
            flush=True
        )

        # ECO
        conexao.sendall(dado)

    print(f"[servidor] cliente saiu: {endereco}", flush=True)
    conexao.close()


while True:
    conexao, endereco = s.accept()

    thread = threading.Thread(
        target=atender_cliente,
        args=(conexao, endereco)
    ).start()
