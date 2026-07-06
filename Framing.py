
class Framing:
    FLAG = b'\x7E'  # Delimitador de início e fim (~)
    ESC  = b'\x7D'  # Caractere de escape (})

    # recebe a mensagem já em bytes, aplica o byte stuffing nos dados, concatena tudo e retorna
    # [0] flag
    # [1] tipo do frame (0 dados, 1 ack)
    # [2] índice
    # [3] dados ...
    # flag final e crc são adicionados pelo controle de erro
    @staticmethod
    def enquadrar(dados: bytes, num_seq: int, tipo_frame: int) -> bytes:

        # se tem ESC nos dados, duplica, \x7D vira \x7D\x7D
        dados_com_stuffing = dados.replace(Framing.ESC, Framing.ESC + Framing.ESC)

        # se tem uma FLAG nos dados, escapa, \x7E vira \x7D\x7E
        dados_com_stuffing = dados_com_stuffing.replace(Framing.FLAG, Framing.ESC + Framing.FLAG)

        # cria cabecalho concatenando [1] tipo frame(0 dados, 1 ack) e [2] sequencia
        cabecalho = bytes([tipo_frame, num_seq])

        # cabeçalho + dados (falta CRC)
        frame_parcial = cabecalho + dados_com_stuffing

        return frame_parcial
    
    # caminho inverso
    @staticmethod
    def desenquadrar(frame_completo: bytes) -> tuple:

        # tamanho minimo flag + cabecalho(2) + CRC(2) + flag = 6 bytes
        if len(frame_completo) < 6:
            raise ValueError("Quadro corrompido ou curto demais para desenquadrar.")
            
        # extrai o cabecalho
        tipo_frame = frame_completo[1]
        num_seq = frame_completo[2]
        
        # CRC fica nos 2 bytes antes da flag de fim
        # como o último byte [-1] é a flag de fim, o CRC ocupa [-3:-1]
        crc_recebido = int.from_bytes(frame_completo[-3:-1], byteorder='big')
        
        # extrai a parte dos dados com stuffing
        # dados começam na posição 3 e vai até antes do CRC (posição -3)
        dados_com_stuffing = frame_completo[3:-3]
        
        # desfaz o byte stuffing
        
        # remove o escape das flags falsas
        dados_puros = dados_com_stuffing.replace(Framing.ESC + Framing.FLAG, Framing.FLAG)
       
        # desfaz os escapes duplicados
        dados_puros = dados_puros.replace(Framing.ESC + Framing.ESC, Framing.ESC)
        
        return tipo_frame, num_seq, dados_puros, crc_recebido