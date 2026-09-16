def pretvarjanje_v_hex(binary):
    niz_bit = ""
    niz_list = []
    if len(binary) % 8 != 0:
        return ""
    for bit in range(0, len(binary), 8):
        niz_bit += hex(int(binary[bit:bit+8], 2)) + "|"
    return niz_bit