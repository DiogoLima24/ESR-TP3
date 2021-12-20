import socket
import threading
import sys
import MyProtocolParser as pp
import time

# Variaveis Globais
PORT = 8080
vizinhos = { } # { ip : conexao }
tabela_rotas = {}  # { FLUXO : ( ORIGEM , METRICA , { DESTINO : ESTADO } ) } }
local_ip = ''

def espera_conexoes(): # Esperar por que outros nodos se conectem a mim
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

def conecta_vizinhos(ips,): # Conetar aos vizinhos que recebo por argumento
    global PORT
    global vizinhos
    global tabela_rotas
    threads = []
    for ip in ips:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip,PORT))

        msg = pp.criaPacoteTipo0()
        s.send(msg)

        vizinhos[ip] = s
        threads.append(threading.Thread(target=worker, args=(ip,)))
        threads[-1].start()

    for th in threads:
        th.join()

def worker(ip,):
    global local_ip
    global vizinhos
    global tabela_rotas

    conn = vizinhos[ip]
    while(True):
        try:
            data = conn.recv(512)
            tipo = pp.getTipo(data)
            print(tipo)
            if(tipo==0): # Se recebeu pedido de caminho mais curto
                for fluxo in tabela_rotas.keys():
                    msg = pp.criaPacoteTipo1(fluxo,2,local_ip) #@TODO: ALTERAR LINHA QUANDO TIVERMOS O FLOODING A COMEÇAR NO SERVIDOR
                    conn.send(msg)

            elif (tipo==1): # Se recebeu caminho mais curto de um vizinho
                fluxo ,metrica, ip_origem = pp.extraiPacoteTipo1ou2(data)

                if(tabela_rotas[fluxo][1] > metrica): # Se caminho é melhor que o atual
                    msg = pp.criaPacoteTipo2(fluxo,metrica,ip_origem)  # Confirmar que quer rota
                    conn.send(msg)
                    tabela_rotas[fluxo] = (ip_origem,metrica,{}) # Registar Rota

                    for vizinho in vizinhos.keys(): # Avisar outros vizinhos
                        if (vizinho != ip):
                            msg = pp.criaPacoteTipo1(fluxo,metrica+1,local_ip)
                            vizinhos[vizinho].send(msg)

            elif (tipo==2): # Se recebeu confirmação da rota
                fluxo, metrica, ip_origem = pp.extraiPacoteTipo1ou2(data)
                aux = tabela_rotas[fluxo][2]
                aux[ip] = False
                tabela_rotas[fluxo] = (ip_origem,metrica,aux)

        except: # Se vizinho "morreu"
            vizinhos.pop(ip)  # Remover da tabela de vizinhos
            for fluxo in tabela_rotas: # Para cada Fluxo
                if (tabela_rotas[fluxo][0] == ip): # Verificar se fluxo vem do vizinho que "morreu"
                    for vizinho in vizinhos: # Pedir caminhos mais curtos aos restantes vizinhos
                        msg = pp.criaPacoteTipo0()
                        vizinhos[vizinho].send(msg)
            #@TODO: Se rota vai para outros vizinho remover entrada da tablea {Destino : Estado}
            break # Parar Worker


def main():
    global PORT
    global local_ip
    global tabela_rotas
    #Processar argumentos recebidos
    sys.argv.pop(0)
    local_ip = sys.argv.pop(0)
    ips_vizinhos = sys.argv
    tabela_rotas[1] = ("",13,{}) # @TODO: REMOVER LINHA QUADNO ACABAREM TESTES

    thread_tcp = threading.Thread(target=espera_conexoes, args=())
    thread_tcp.start()
    thread_vizinhos = threading.Thread(target=conecta_vizinhos,args=(ips_vizinhos,))
    thread_vizinhos.start()

    thread_tcp.join()
    thread_vizinhos.join()

if __name__ == '__main__':
    main()