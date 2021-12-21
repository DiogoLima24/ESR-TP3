import socket
import threading
import sys
import MyProtocolParser as pp
import time
import re

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
        ip = addr[0]
        vizinhos[ip] = conexao

        threads.append(threading.Thread(target=worker, args=(ip,)))
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
            if(tipo==0): # Se recebeu pedido de caminho mais curto
                print("[0] Recebi pedido de caminhos mais curtos de: " , ip)
                for fluxo in tabela_rotas.keys():
                    metrica = tabela_rotas[fluxo][1]
                    msg = pp.criaPacoteTipo1(fluxo,metrica)
                    print("Enviar rota do fluxo ",fluxo," para: ",ip)
                    conn.send(msg)

            elif (tipo==1): # Se recebeu caminho mais curto de um vizinho
                fluxo ,metrica = pp.extraiPacoteTipo1ou2(data)
                print("[1] Recebi caminho mais curto do fluxo ",fluxo," com métrica " ,metrica, " de: ",ip)

                if(not(fluxo in tabela_rotas) or tabela_rotas[fluxo][1] > metrica): # Se caminho é melhor que o atual
                    print("Caminho é ótimo, enviar confirmação.")
                    msg = pp.criaPacoteTipo2(fluxo,metrica)  # Confirmar que quer rota
                    conn.send(msg)
                    tabela_rotas[fluxo] = (ip,metrica,{}) # Registar Rota
                    print("Tabela Rotas: ",tabela_rotas)

                    for vizinho in vizinhos.keys(): # Avisar outros vizinhos
                        if (vizinho != ip):
                            print("Enviar rota do fluxo ", fluxo , " para: " , vizinho)
                            msg = pp.criaPacoteTipo1(fluxo,(metrica+1),ip)
                            vizinhos[vizinho].send(msg)

            elif (tipo==2): # Se recebeu confirmação da rota
                print("[2] Recebi confirmação do caminho mais curto")
                fluxo, metrica = pp.extraiPacoteTipo1ou2(data)
                aux = tabela_rotas[fluxo][2][ip] = False
                print("Tabela Rotas: ", tabela_rotas)

            elif (tipo==3): # Se recebeu alteração do estado da rota
                fluxo, estado = pp.extraiPacoteTipo3(data)
                tabela_rotas[fluxo][2][ip] = estado
                print("Tabela Rotas: ",tabela_rotas)
                msg = pp.criaPacoteTipo3(fluxo,estado)

                next = tabela_rotas[fluxo][0]
                vizinhos[next].send(msg)

        except: # Se vizinho "morreu"
            vizinhos.pop(ip)  # Remover da tabela de vizinhos
            fluxos = list(tabela_rotas.keys())
            for fluxo in fluxos: # Para cada Fluxo
                if (tabela_rotas[fluxo][0] == ip): # Verificar se fluxo vem do vizinho que "morreu"
                    tabela_rotas.pop(fluxo)
                    for vizinho in vizinhos: # Pedir caminhos mais curtos aos restantes vizinhos
                        msg = pp.criaPacoteTipo0()
                        vizinhos[vizinho].send(msg)
                elif(ip in tabela_rotas[fluxo][2]):
                    tabela_rotas[fluxo][2].pop(ip)
            print("Tabela Rotas: ",tabela_rotas)
            break # Parar Worker

def server():
    global vizinhos
    fluxo = int(input())
    msg = pp.criaPacoteTipo1(fluxo,2)
    tabela_rotas[fluxo] = ("",1,{})
    for vizinho in vizinhos:
        vizinhos[vizinho].send(msg)


def main():
    global PORT
    global local_ip
    global tabela_rotas
    #Processar argumentos recebidos
    sys.argv.pop(0)
    srv = False
    if(re.search(r'^-S$',sys.argv[0])):
        srv = True
        sys.argv.pop(0)
    local_ip = sys.argv.pop(0)
    ips_vizinhos = sys.argv

    thread_tcp = threading.Thread(target=espera_conexoes, args=())
    thread_tcp.start()
    thread_vizinhos = threading.Thread(target=conecta_vizinhos,args=(ips_vizinhos,))
    thread_vizinhos.start()
    if(srv):
        thread_server = threading.Thread(target=server,args=())
        thread_server.start()

    thread_tcp.join()
    thread_vizinhos.join()

if __name__ == '__main__':
    main()