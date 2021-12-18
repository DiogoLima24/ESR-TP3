import socket
import threading
import sys
import MyProtocolParser as pp

PORT = 8080
vizinhos = { } # { ip : conexao }

tabela_rotas = {}  # { FLUXO : ( ORIGEM , METRICA , { DESTINO : ESTADO } ) } }

local_ip = ''

def espera_conexoes():
    global local_ip
    global vizinhos
    print(local_ip)
    # Criar socket para escutar em TCP
    socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    socket_tcp.bind((local_ip, PORT))
    socket_tcp.listen(1)
    threads = []
    while(True):
        conexao, addr = socket_tcp.accept()
        vizinhos[addr] = conexao

        threads.append(threading.Thread(target=worker, args=(addr,)))
        threads[-1].start()

    for th in threads:
        th.join()

def conecta_vizinhos(ips,):
    global PORT
    global vizinhos
    global tabela_rotas
    threads = []
    for ip in ips:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip,PORT))

        msg = pp.criaPacoteTipo1(1,2)
        s.send(msg)

        vizinhos[ip] = s
        threads.append(threading.Thread(target=worker, args=(ip,)))
        threads[-1].start()

    for th in threads:
        th.join()

def worker(ip,):
    conn = vizinhos[ip]
    while(True):
        data = conn.recv(512)
        tipo = pp.getTipo(data)

        if (tipo==1): # Se recebeu caminho mais curto de um vizinho
            fluxo = int(data[1])
            metrica = int(data[2])

            if(tabela_rotas[fluxo][1] > metrica):
                # @TODO: Atualizar tabela e notificar vizinhos
                metrica = metrica + 1
                



def main():
    global PORT
    global local_ip
    sys.argv.pop(0)
    local_ip = sys.argv.pop(0)
    ips_vizinhos = sys.argv

    # Escutar em TCP em paralelo
    thread_tcp = threading.Thread(target=espera_conexoes, args=())
    thread_tcp.start()

    thread_vizinhos = threading.Thread(target=conecta_vizinhos,args=(ips_vizinhos,))
    thread_vizinhos.start()

    thread_tcp.join()
    thread_vizinhos.join()

if __name__ == '__main__':
    main()

