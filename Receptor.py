# Arquivo: receptor.py
import socket
from Framing import Framing
import ControleErros

class Receptor:
    def __init__(self, ip_escuta='0.0.0.0', porta_escuta=5001):
        self.endereco = (ip_escuta, porta_escuta)
 
        # próximo número de sequência que o receptor espera receber (Go-Back-N)
        self.esperado = 0
 
        #onde é guardado os dados que já chegaram em ordem
        self.mensagem_recebida = bytearray()
 
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(self.endereco)


    def _construir_ack(self, num_seq_esperado: int) -> bytes:
        # monta um frame do tipo ACK (tipo_frame=1) sem dados, informando
        # qual é o próximo número de sequência que o receptor está esperando
        quadro_parcial = Framing.enquadrar(b'', num_seq_esperado % 256, tipo_frame=1)
        quadro_com_crc = ControleErros.encodeData(quadro_parcial, ControleErros.KEY)
        return Framing.FLAG + quadro_com_crc + Framing.FLAG
    

    def iniciar(self):
        # Dar bind no socket UDP para escutar a porta
        print(f"[Receptor] Escutando em {self.endereco}...")
        while True:
            # PASSO 1: recebe dados brutos do socket UDP
            dados_brutos, endereco_origem = self.sock.recvfrom(2048)
 
            #tamanho mínimo: flag(1) + cabecalho(2) + crc(2) + flag(1) = 6 bytes
            if len(dados_brutos) < 6:
                print("[Receptor] Frame curto demais, descartado.")
                continue
 
            # PASSO 2: chama o crc para validar (sem as flags, que não entram no cálculo)
            frame_sem_flags = dados_brutos[1:-1]
            if not ControleErros.checkData(frame_sem_flags, ControleErros.KEY):
                print("[Receptor] Frame corrompido (CRC inválido) - descartado, sem ACK.")
                # não manda ack: o transmissor vai estourar o timeout e reenviar sozinho
                continue
 
            #PASSO 3: chama o Framing para abrir o pacote
            tipo, num_seq, dados, _crc = Framing.desenquadrar(dados_brutos)
 
            # o receptor só trata frames de dados; ack's (tipo=1) não chegam aqui
            if tipo == 1:
                continue
 
            # PASSO 4: lógica da janela (go-back-N: só aceita em ordem)
            if num_seq == self.esperado % 256:
                print(f"[Receptor] Frame {num_seq} recebido em ordem.")
                self.mensagem_recebida.extend(dados)
                self.esperado += 1
            else:
                print(f"[Receptor] Frame {num_seq} fora de ordem "
                      f"(esperava {self.esperado % 256}) -> descartado.")
 
            # PASSO 5: envia o ack cumulativo, sempre informando o próximo
            # número esperado (mesmo se o frame recém recebido foi descartado,
            # isso reforça para o transmissor até onde ele já pode avançar)
            ack = self._construir_ack(self.esperado)
            self.sock.sendto(ack, endereco_origem)