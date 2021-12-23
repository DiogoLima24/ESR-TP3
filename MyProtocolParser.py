import sys
# Construtores de Pacotes
def criaPacoteTipo0(): # Pedir Caminhos Mais Curtos
    tipo = bytes([0])
    return tipo

def criaPacoteTipo1(fluxo,metrica): # Enviar Caminho Mais Curto
    tipo = bytes([1])
    fluxo = bytes([fluxo])
    metrica = bytes([metrica])
    pacote = tipo + fluxo + metrica
    return pacote

def criaPacoteTipo2(fluxo,estado): # Confirmar melhor rota
    tipo = bytes([2])
    fluxo = bytes([fluxo])
    if estado:
        e = bytes([1])
    else:
        e = bytes([0])
    pacote = tipo + fluxo + e
    return pacote

def criaPacoteTipo3(fluxo,estado): # Alterar estado da rota
    tipo = bytes([3])
    fluxo = bytes([fluxo])
    if estado:
        e = bytes([1])
    else:
        e = bytes([0])
    pacote = tipo + fluxo + e
    return pacote

def criaPacoteTipo4(fluxo,dados): # Reencaminhar pacote da stream
    tipo = bytes([4])
    fluxo = bytes([fluxo])
    pacote = tipo + fluxo + dados
    return pacote

# Extrair Conteudo dos Pacotes
def getTipo(pacote): # Consultar o tipo da mensagem
    return int(pacote[0])

# Extrair conteudo dos Pacotes tipo 1 ou tipo 2
def extraiPacoteTipo1(pacote):
    fluxo = int(pacote[1])
    metrica = int(pacote[2])
    return (fluxo , metrica)

# Extrair conteudo dos Pacotes de tipo 3
def extraiPacoteTipo2ou3(pacote):
    fluxo = int(pacote[1])
    estado = (int(pacote[2]) == 1)
    return (fluxo, estado)

# Extrair conteudo dos Pacotes de tipo 4
def extraiPacoteTipo4(pacote):
    fluxo = int(pacote[1])
    data = pacote[2:]
    return (fluxo, data)