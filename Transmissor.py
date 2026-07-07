# Arquivo: transmissor.py
import socket
import ControleErros
from Framing import Framing
from CanalComRuido import CanalComRuido


class Transmissor:
    def __init__(self, ip_destino='127.0.0.1', porta_destino=5001, porta_escuta=5000,
                 tamanho_janela=4, timeout=1.0, tamanho_chunk=4, modo_ruido="sucesso",
                 falhas_forcadas=None):
 
        self.canal = CanalComRuido()
        self.destino = (ip_destino, porta_destino)
 
        # parâmetros do Go-Back-N 
        self.tamanho_janela = tamanho_janela   #quantos frames podem estar no ar sem ack
        self.timeout = timeout                  #segundos até considerar que deu timeout
        self.tamanho_chunk = tamanho_chunk      #quantos bytes de dados cabem em cada frame
        self.MAX_SEQ = 256                      #num_seq ocupa 1 byte no cabeçalho (0-255)
 
        # modo_ruido "padrão" usado em todas as tentativas: sucesso / perda / erro / aleatorio
       
        self.modo_ruido = modo_ruido
 
        # falhas_forcadas: transmissor permite forçar falha só na primeira tentativa de um frame específico 
        # nas tentativas seguintes (retransmissão) o frame vai normalmente ("sucesso").
        self.falhas_forcadas = falhas_forcadas or {}
        self._tentativas_por_frame = {}
 
        # variáveis da janela (base, próximo)
        self.base = 0
        self.proximo_seq = 0
 
        # socket UDP usado tanto para enviar dados quanto para escutar os ack's
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('0.0.0.0', porta_escuta))
        self.sock.settimeout(self.timeout)
 
    def _construir_frame(self, dados: bytes, num_seq: int, tipo: int) -> bytes:
        # PASSO 1: Chama Framing
        quadro_parcial = Framing.enquadrar(dados, num_seq, tipo)
        # PASSO 2: Chama CRC
        quadro_com_crc = ControleErros.encodeData(quadro_parcial, ControleErros.KEY)
        # completa com as flags de início/fim
        return Framing.FLAG + quadro_com_crc + Framing.FLAG
    
    def enviar_mensagem(self, mensagem):
        if isinstance(mensagem, str):
            mensagem = mensagem.encode('utf-8')

        # quebra a mensagem em pedaços do tamanho de um frame
        pedacos = [mensagem[i:i + self.tamanho_chunk]
                for i in range(0, len(mensagem), self.tamanho_chunk)] or [b'']
        total_frames = len(pedacos)

        buffer_frames = {}  # guarda os frames já montados, para poder retransmitir

        self.base = 0
        self.proximo_seq = 0

        # LOOP PRINCIPAL DA JANELA GO-BACK-N:
        # Enquanto tiver dados para enviar na janela
        while self.base < total_frames:

            # PASSO 1: monta framing + CRC + flags, feito dentro de _construir_frame
            # e envia com ruído todos os frames que cabem na janela e que ainda não
            # tinham sido enviados
            while self.proximo_seq < total_frames and self.proximo_seq < self.base + self.tamanho_janela:
                seq_atual = self.proximo_seq % self.MAX_SEQ

                if self.proximo_seq not in buffer_frames:
                    buffer_frames[self.proximo_seq] = self._construir_frame(
                        pedacos[self.proximo_seq], seq_atual, tipo=0
                    )

                self._enviar_com_ruido(buffer_frames[self.proximo_seq], self.proximo_seq)
                self.proximo_seq += 1

            # PASSO 2: Escuta ack e trata timeout.
            # Se receber ack, processa e avança a base. Se der timeout, retransmite todos os frames da janela.
            try:
                ack_bruto, _ = self.sock.recvfrom(2048)
                self._processar_ack(ack_bruto)
            except socket.timeout:
                print(f"[Transmissor] TIMEOUT! Retransmitindo a janela a partir do frame {self.base}.")
                for seq in range(self.base, self.proximo_seq):
                    self._enviar_com_ruido(buffer_frames[seq], seq)

        print("[Transmissor] Mensagem enviada e confirmada com sucesso.")

    #Função auxiliar para enviar um frame com ruído (ou não) e contabilizar tentativas
    def _enviar_com_ruido(self, frame_pronto: bytes, indice_frame: int):
        tentativa = self._tentativas_por_frame.get(indice_frame, 0)
        self._tentativas_por_frame[indice_frame] = tentativa + 1
 
        # se esse índice tem uma falha forçada agendada e essa é a 1a tentativa, usa ela
        if tentativa == 0 and indice_frame in self.falhas_forcadas:
            modo = self.falhas_forcadas[indice_frame]
        else:
            modo = self.modo_ruido
 
        # aplica o canal com ruído (pode devolver o frame igual, alterado ou None)
        quadro_viajado = self.canal.aplicar(frame_pronto, modo=modo)
        if quadro_viajado is not None:
            self.sock.sendto(quadro_viajado, self.destino)
 
    def _processar_ack(self, ack_bruto: bytes):
        if len(ack_bruto) < 6:
            return
 
        # valida o crc do ack (sem as flags)
        frame_sem_flags = ack_bruto[1:-1]
        if not ControleErros.checkData(frame_sem_flags, ControleErros.KEY):
            print("[Transmissor] ACK corrompido, ignorado (vai depender do timeout).")
            return
 
        tipo, num_seq_ack, _dados, _crc = Framing.desenquadrar(ack_bruto)
 
        if tipo != 1:
            return  # não é um ACK
 
        # ACK cumulativo: o receptor informa o próximo num_seq que ele espera.
        #avança a base até esse ponto (considerando o "wrap" do byte de sequência).
        antiga_base = self.base
        while (self.base % self.MAX_SEQ) != num_seq_ack and self.base < self.proximo_seq:
            self.base += 1
 
        if self.base != antiga_base:
            print(f"[Transmissor] ACK recebido (esperado={num_seq_ack}). "
                  f"Janela avançou: base {antiga_base} -> {self.base}.")
 

