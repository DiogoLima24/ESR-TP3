import sys
# Construtores de Pacotes
def criaPacoteTipo0(): # Pedir Caminhos Mais Curtos
    tipo = bytes([0])
    return tipo

def criaPacoteTipo1(fluxo,metrica,ip): # Enviar Caminho Mais Curto
    tipo = bytes([1])
    fluxo = bytes([fluxo])
    metrica = bytes([metrica])
    ip = bytes(ip,'utf-8')
    pacote = tipo + fluxo + metrica + ip
    return pacote

def criaPacoteTipo2(fluxo,metrica,ip): # Confirmar melhor rota
    tipo = bytes([2])
    fluxo = bytes([fluxo])
    metrica = bytes([metrica])
    ip = bytes(ip,'utf-8')
    pacote = tipo + fluxo + metrica +ip
    return pacote

def criaPacoteTipo3(fluxo,estado):
    tipo = bytes([3])
    fluxo = bytes([fluxo])
    if estado:
        e = bytes([1])
    else:
        e = bytes([0])
    pacote = tipo + fluxo + e
    return pacote


# Extrair Conteudo dos Pacotes
def getTipo(pacote): # Consultar o tipo da mensagem
    return int(pacote[0])

# Extrair conteudo dos Pacotes tipo 1 ou tipo 2
def extraiPacoteTipo1ou2(pacote):
    fluxo = int(pacote[1])
    metrica = int(pacote[2])
    ip = pacote[3:].decode('utf-8')
    return (fluxo , metrica , ip)

# Extrair conteudo dos Pacotes de tipo 3
def extraiPacoteTipo3(pacote):
    fluxo = int(pacote[1])
    estado = (int(pacote[2]) == 1)
    return (fluxo, estado)
