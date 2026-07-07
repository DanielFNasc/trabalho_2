import random

class CanalComRuido:
    def __init__(self):
        pass

    # modos: sucesso, perda, erro, aleatorio 
    def aplicar(self, frame: bytes, modo: str) -> bytes or None:
        # extrai o índice do quadro direto do cabeçalho (posição 2 dos bytes)
        indice_frame = frame[2]

        if modo == "aleatorio":
            sorteio = random.randint(1, 3)
            if sorteio == 1:
                modo = "erro"
            elif sorteio == 2:
                modo = "perda"
            else:
                modo = "sucesso"

        if modo == "sucesso":
            print(f"Frame de índice {indice_frame} foi enviado com sucesso")
            return frame  # Não faz nada, o pacote passa limpo
            
        elif modo == "perda":
            print(f"Frame de índice {indice_frame} foi perdido")
            return None    # Devolve "nada", simulando que o pacote se perdeu
            
        elif modo == "erro":
            print(f"Frame de índice {indice_frame} sofreu ruído e foi corrompido")
            
            print("Frame antes de ser corrompido:")
            print(frame)
            # cria uma cópia de frame só que com bytesarray pode alterar, bytes não
            frame_corrompido = bytearray(frame) 
            
            # a partir do byte 3 começa os dados
            if len(frame_corrompido) > 3:
                # pega o primeiro byte de dados ^= e faz xor com 00000001 
                # ou seja, cada inverte o último bit do byte 3
                frame_corrompido[3] ^= 0x01 
                
            return bytes(frame_corrompido)
            
        return frame