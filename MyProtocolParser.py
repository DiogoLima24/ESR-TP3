import sys

# Construtores de Pacotes

def criaPacoteTipo1(fluxo,metrica):
    tipo = bytes([0])
    f = bytes([fluxo])
    m = bytes([metrica])

    pacote = tipo + f + m
    return pacote

# Extrair Conteudo dos Pacotes

def getTipo(pacote):
    return int(pacote[0])


