TRABALHO 2 CD - CAMADA DE ENLACE

DIVISÃO DAS CLASSES:

--- CLASSES UTILITÁRIAS ---
1. Framing (PRONTA)
   - Enquadramento: Faz o byte stuffing e coloca cabeçalhos nos dados.
   - Desenquadramento: Abre o pacote e desfaz o stuffing no receptor.

2. ControleErro
   - Calcula o CRC-16 e cola no final do frame .
   - Valida o CRC-16 no recetor para ver se houve erro.

3. CanalComRuido (PRONTA)
   - Recebe o frame e um modo: sucesso, perda, erro, aleatorio.

--- CLASSES DE CONTROLE DE FLUXO ---
1. Transmissor
   - Controla a janela de envio (Go-Back-N).
   - Controla o cronômetro (Timeout) e retransmissões.

2. Receptor
   - Recebe os pacotes e verifica se estão na ordem certa.
   - Envia os ACKs de confirmação.


COMO OS DADOS TRAFEGAM (FLUXO DO CODIGO):
Transmissor -> Chama Framing -> Chama CRC -> Aplica Ruido -> Envia via socket UDP -> Receptor