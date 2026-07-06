#crc-16 kermit
KEY = "0001000000100001"

def bytes_para_bits(dados: bytes) -> str:
    return ''.join(f'{b:08b}' for b in dados)


def bits_para_bytes(bits: str) -> bytes:
    # completa com zeros caso necessário
    while len(bits) % 8 != 0:
        bits += '0'

    return bytes(
        int(bits[i:i+8], 2)
        for i in range(0, len(bits), 8)
    )


# ----------------------------
# XOR
# ----------------------------

def xor(a: str, b: str) -> str:

    resultado = []

    for i in range(1, len(b)):
        if a[i] == b[i]:
            resultado.append('0')
        else:
            resultado.append('1')

    return ''.join(resultado)


# ----------------------------
# Divisão módulo 2
# ----------------------------

def mod2div(dividend: str, divisor: str) -> str:

    pick = len(divisor)

    tmp = dividend[:pick]

    while pick < len(dividend):

        if tmp[0] == '1':
            tmp = xor(divisor, tmp) + dividend[pick]
        else:
            tmp = xor('0' * len(divisor), tmp) + dividend[pick]

        pick += 1

    if tmp[0] == '1':
        tmp = xor(divisor, tmp)
    else:
        tmp = xor('0' * len(divisor), tmp)

    return tmp


# ----------------------------
# Codificação CRC
# ----------------------------

def encodeData(dados: bytes, polinomio: str) -> bytes:

    bits = bytes_para_bits(dados)

    appended = bits + '0' * (len(polinomio) - 1)

    resto = mod2div(appended, polinomio)

    codeword = bits + resto

    return bits_para_bytes(codeword)


# ----------------------------
# Verificação CRC
# ----------------------------

def checkData(frame: bytes, polinomio: str) -> bool:

    bits = bytes_para_bits(frame)

    resto = mod2div(bits, polinomio)

    return set(resto) == {'0'}    


