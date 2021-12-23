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
cliente = False
clientSocket = None

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
    global cliente
    global clientSocket

    conn = vizinhos[ip]
    while(True):
        try:
            data = conn.recv(20482)
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
                            msg = pp.criaPacoteTipo1(fluxo,(metrica+1))
                            vizinhos[vizinho].send(msg)
                else:
                    print("Já tenho caminho melhor..")

            elif (tipo==2): # Se recebeu confirmação da rota
                print("[2] Recebi confirmação do caminho mais curto")
                fluxo, metrica = pp.extraiPacoteTipo1ou2(data)
                tabela_rotas[fluxo][2][ip] = False
                print("Tabela Rotas: ", tabela_rotas)

            elif (tipo==3): # Se recebeu alteração do estado da rota
                fluxo, estado = pp.extraiPacoteTipo3(data)
                print("[3] Recebi alteração do estado do fluxo ",fluxo," para " ,estado, " de: ",ip)
                tabela_rotas[fluxo][2][ip] = estado
                print("Tabela Rotas: ",tabela_rotas)

                next = tabela_rotas[fluxo][0]
                if(next != ''):
                    if (estado):
                        msg = pp.criaPacoteTipo3(fluxo, estado)
                        vizinhos[next].send(msg)
                    elif(not estado):
                        propagar = True
                        for destino in tabela_rotas[fluxo][2]:
                            if (tabela_rotas[fluxo][2][destino]):
                                propagar = False
                        if (propagar):
                            msg = pp.criaPacoteTipo3(fluxo, estado)
                            vizinhos[next].send(msg)

            elif (tipo==4):
                fluxo , pacote = pp.extraiPacoteTipo4(data)
                print("[4] Recebi stream do fluxo ", fluxo, " de: ", ip)
                if (cliente):
                    clientSocket.sendto(pacote,(local_ip,25000))

                for rota in tabela_rotas[fluxo][2]:
                    if (tabela_rotas[fluxo][2][rota]):
                        print("Reencaminhar para", rota)
                        msg = pp.criaPacoteTipo4(fluxo, pacote)
                        vizinhos[rota].send(msg)

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
            break # Parar Worker"""

def server():
    global vizinhos
    global local_ip
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        # Bind the socket to the address using the RTP port
        serverSocket.bind((local_ip, 25000))
        #serverSocket.settimeout(5)
        while(True):
            data = serverSocket.recv(20482)
            if (int(data[0]) == 0):
                fluxo = int(data[1])
                msg = pp.criaPacoteTipo1(fluxo,2)
                tabela_rotas[fluxo] = ("",1,{})
                for vizinho in vizinhos:
                   vizinhos[vizinho].send(msg)

            if (int(data[0]) == 1):
                fluxo = int(data[1])
                data = data[2:]
                for rota in tabela_rotas[fluxo][2]:
                    if (tabela_rotas[fluxo][2][rota]):
                        msg = pp.criaPacoteTipo4(fluxo,data)
                        vizinhos[rota].send(msg)
    except:
        print("Didn't Bind\n")


def client():
    global vizinhos
    global local_ip
    global clientSocket
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


    # Bind the socket to the address using the RTP port
    clientSocket.bind((local_ip, 25001))
    # serverSocket.settimeout(5)
    while (True):
        data = clientSocket.recv(20481)
        if (int(data[0]) == 0):
            fluxo = int(data[1])
            msg= pp.criaPacoteTipo3(fluxo,True)
            next = tabela_rotas[fluxo][0]
            vizinhos[next].send(msg)

        elif (int(data[0]) == 1):
            fluxo = int(data[1])
            msg = pp.criaPacoteTipo3(fluxo,False)
            next = tabela_rotas[fluxo][0]
            vizinhos[next].send(msg)



def main():
    global PORT
    global local_ip
    global tabela_rotas
    global cliente
    #Processar argumentos recebidos
    sys.argv.pop(0)
    srv = False
    if(re.search(r'^-S$',sys.argv[0])):
        srv = True
        sys.argv.pop(0)
    elif (re.search(r'^-C$', sys.argv[0])):
        cliente = True
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
    elif(cliente):
        thread_client = threading.Thread(target=client, args=())
        thread_client.start()

    thread_tcp.join()
    thread_vizinhos.join()


if __name__ == '__main__':
    main()