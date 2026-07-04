# Arquivo: receptor.py
import socket
from framing import Framing

class ReceptorGBN:
    def __init__(self):
        # Criar variavel do frame esperado (começa em 0)
        pass

    def iniciar(self):
        # Dar bind no socket UDP para escutar a porta
        
        while True:
            # PASSO 1: Recebe dados brutos do socket UDP
            # dados_brutos = sock.recvfrom(1024)
            
            # PASSO 2: Chama CRC para validar
            # Se o CRC der erro, da 'continue' para ignorar o pacote
            
            # PASSO 3: Chama Framing para abrir o pacote
            # tipo, seq, dados, crc = Framing.desenquadrar(dados_brutos)
            
            # PASSO 4: Logica da Janela
            # Se seq == esperado: guarda os dados e incrementa o esperado
            # Se seq diferente: descarta o pacote
            
            # PASSO 5: Envia o ACK de volta
            # Monta frame de ACK -> Bota CRC no ACK -> Envia via UDP
            pass
