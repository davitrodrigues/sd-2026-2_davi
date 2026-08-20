import os
import socket
import threading
import time
from datetime import datetime

HOST, PORT = "127.0.0.1", 5001

qtd_test = [10, 50, 100]
MSGS_POR_CLIENTE = 3

# grava sempre ao lado deste script, nao importa de onde ele seja executado
ARQUIVO_MD = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "resultados.md"
)

tempos = []
resultados = []

def cliente(id):
    inicio = time.time()
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(10)
        s.connect((HOST, PORT))
        for i in range(MSGS_POR_CLIENTE):
            msg = f"cliente: {id} - mensagem {i + 1}"
            s.sendall(msg.encode())
            resp = s.recv(1024)
            if not resp:
                print(f"Cliente {id}: servidor fechou a conexão")
                break
        s.close()
        fim = time.time()
        tempos.append(fim - inicio)
    except Exception as e:
        print(f"Erro - cliente {id} - {e}")
def testar(quantidade):
    global tempos
    tempos = []
    threads = []
    print(f"\nTestando com: {quantidade}")
    inicio_total = time.time()
    for i in range(quantidade):
        thread = threading.Thread(
            target=cliente,
            args=(i + 1,)
        )
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()
    fim_total = time.time()
    tempo_total = fim_total - inicio_total
    if len(tempos) > 0:
        tempo_medio = sum(tempos) / len(tempos)
        tempo_min = min(tempos)
        tempo_max = max(tempos)
    else:
        tempo_medio = 0
        tempo_min = 0
        tempo_max = 0
    print(f"Clientes concluídos: {len(tempos)}/{quantidade}")
    print(f"Tempo total: {tempo_total:.4f} segundos")
    print(f"Tempo médio por cliente: {tempo_medio:.4f} segundos")
    resultados.append({
        "quantidade": quantidade,
        "concluidos": len(tempos),
        "falhas": quantidade - len(tempos),
        "tempo_total": tempo_total,
        "tempo_medio": tempo_medio,
        "tempo_min": tempo_min,
        "tempo_max": tempo_max
    })
def gravar_md():
    agora = datetime.now().strftime("%d/%m/%Y às %H:%M:%S")
    linhas = []
    linhas.append(f"## Execução de {agora}")
    linhas.append("")
    linhas.append(f"- Servidor: `{HOST}:{PORT}`")
    linhas.append(f"- Mensagens por cliente: {MSGS_POR_CLIENTE}")
    linhas.append("")
    linhas.append(
        "| Clientes | Concluídos | Falhas | Tempo total (s) "
        "| Tempo médio (s) | Mínimo (s) | Máximo (s) |"
    )
    linhas.append("| ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
    for r in resultados:
        linhas.append(
            f"| {r['quantidade']} "
            f"| {r['concluidos']} "
            f"| {r['falhas']} "
            f"| {r['tempo_total']:.4f} "
            f"| {r['tempo_medio']:.4f} "
            f"| {r['tempo_min']:.4f} "
            f"| {r['tempo_max']:.4f} |"
        )
    linhas.append("")

    # abre em modo append: cada execução vira uma seção nova, nada é perdido
    primeira_vez = not os.path.exists(ARQUIVO_MD)
    with open(ARQUIVO_MD, "a", encoding="utf-8") as arquivo:
        if primeira_vez:
            arquivo.write("# Resultados do teste de carga\n\n")
        arquivo.write("\n".join(linhas) + "\n")
    print(f"\nResultados gravados em: {ARQUIVO_MD}")
for quantidade in qtd_test:
    testar(quantidade)
gravar_md()
