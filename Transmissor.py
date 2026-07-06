# Arquivo: transmissor.py
import socket
import ControleErros
from Framing import Framing
from CanalComRuido import CanalComRuido

class Transmissor:
    def __init__(self):
        self.canal = CanalComRuido()
        # Criar variaveis da janela aqui (base, proximo, buffer)

    def enviar_mensagem(self, mensagem):
        # Configurar socket UDP aqui
        
        # LOOP PRINCIPAL DA JANELA GO-BACK-N:
        # Enquanto tiver dados para enviar na janela...
        
        # PASSO 1: Chama Framing
        # quadro_parcial = Framing.enquadrar(dados, num_seq, tipo_quadro=0)
        dados = ''
        num_seq = 0
        tipo_quadro = 0
        quadro_parcial = Framing.enquadrar(dados,num_seq,tipo_quadro)
        # PASSO 2: Chama CRC
        # quadro_completo = ControladorErro.adicionar_crc(quadro_parcial)
        quadro_completo = ControleErros.encodeData(quadro_parcial,ControleErros.KEY)

        # Completa com flags
        quadro_completo = Framing.FLAG + quadro_completo + Framing.FLAG
        
        # PASSO 3: Aplica Ruido
        # quadro_viajado = self.canal.aplicar(quadro_completo, modo="aleatorio")
        quadro_viajado = self.canal.aplicar(quadro_completo,modo="aleatorio")
        
        
        # PASSO 4: Envia via UDP
        # if quadro_viajado is not None:
        #     sock.sendto(quadro_viajado, destino)
            
        # PASSO 5: Escuta ACK e trata TIMEOUT
        # Se der Timeout, volta o proximo_sequencial para a base
        pass
