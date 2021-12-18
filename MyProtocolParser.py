import sys
# Construtores de Pacotes
def criaPacoteTipo0(): # Pedir Caminhos Mais Curtos
    tipo = bytes([0])
    return tipo

def criaPacoteTipo1(fluxo,metrica): # Enviar Caminho Mais Curto
    tipo = bytes([1])
    f = bytes([fluxo])
    m = bytes([metrica])
    pacote = tipo + f + m
    return pacote

def criaPacoteTipo2(fluxo,metrica): # Confirmar melhor rota
    tipo = bytes([2])
    f = bytes([fluxo])
    m = bytes([metrica])
    pacote = tipo + f + m
    return pacote

# Extrair Conteudo dos Pacotes
def getTipo(pacote): # Consultar o tipo da mensagem
    return int(pacote[0])