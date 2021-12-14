import socket
import threading
import sys

PORT = 8080
vizinhos = { } # { ip : conexao }

def escuta_tcp(tcp):
    while(True):
        conexao, addr = tcp.accept()
        print(conexao)
        # Extrair os dados dos socket
        data = conexao.recv(512)

        # Converter byte para string
        data = data.decode()
        print(data)
        msg = "recebi"
        conexao.send(msg.encode('ascii'))


def conecta_vizinhos(ips):
    global PORT
    global vizinhos

    for ip in ips:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip,PORT))
        msg = "ola"
        s.send(msg.encode())

        data = s.recv(512)
        print(data.decode())
        print(s)
        # WORKER(S,IP)




def main():
    global PORT
    sys.argv.pop(0)
    local_ip = sys.argv.pop(0)
    ips_vizinhos = sys.argv

    print(local_ip)



    # Criar socket para escutar em TCP
    socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    socket_tcp.bind((local_ip, PORT))
    socket_tcp.listen(1)

    # Escutar em TCP em paralelo
    thread_tcp = threading.Thread(target=escuta_tcp, args=(socket_tcp,))
    thread_tcp.start()

    thread_vizinhos = threading.Thread(target=conecta_vizinhos,args=(ips_vizinhos,))
    thread_vizinhos.start()

    thread_tcp.join()
    thread_vizinhos.join()

if __name__ == '__main__':
    main()

