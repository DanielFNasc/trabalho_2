
def CRC(mensagem:str):
    valorCRC = 0
    for byte in mensagem:
        for i in range(8):
            bit = (byte >> (7-i)) & 1 ##como acessar o bit, se for 0 continua


def Hamming(dados):
    pass
