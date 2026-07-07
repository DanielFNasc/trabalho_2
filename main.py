import threading
import time

from Transmissor import Transmissor
from Receptor import Receptor
 

def rodar_receptor(receptor: Receptor):
    receptor.iniciar()


def main():
     # o receptor escuta na porta 5001
    receptor = Receptor(porta_escuta=5001)
    thread_receptor = threading.Thread(target=rodar_receptor, args=(receptor,), daemon=True)
    thread_receptor.start()
 
    time.sleep(0.3)  # dá tempo do receptor abrir o socket antes do transmissor começar
 
    #transmissor escuta acks na porta 5000 e manda dados para a porta 5001
    transmissor = Transmissor(
        ip_destino='127.0.0.1',
        porta_destino=5001,
        porta_escuta=5000,
        tamanho_janela=4,
        timeout=1.0,
        tamanho_chunk=4,
        modo_ruido="sucesso",       #comportamento padrão dos frames (caso de sucesso)
        falhas_forcadas={           #controle dos casos de frames perdidos e frames com erro 
            2: "perda",             #o frame de índice 2 vai se perder na 1a tentativa
            5: "erro",              #o frame de índice 5 vai chegar corrompido na 1a tentativa
        },
    )
 
    transmissor.enviar_mensagem("Trabalho 2 de Comunicação de Dados feito por Daniel, Laura e Yasmin.")
 
    time.sleep(0.5)
    print("\nMensagem remontada no receptor:")
    print(receptor.mensagem_recebida.decode('utf-8', errors='replace'))


if __name__ == "__main__":
    main()

