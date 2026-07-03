def gerar_quadro(mensagem:str):

    FLAG = 0x7E
    ESC  = 0x7D
    quadro = 0

    mensagemFormatada = ""


    mensagemFormatada.append(FLAG)


    #FALTA BYTE STUFFING PRA ESC NA MENSAGEM
    #da pra usar campo de tamanho, ai nao precisa de byte stuffing
    for char in mensagem:
        if char == FLAG:
            mensagemFormatada.append(ESC)
        mensagemFormatada.append(char)

    mensagemFormatada.append(FLAG)
    
    #adicionaCRC

    return quadro


def threadTransimissora(mensagem):
    pass