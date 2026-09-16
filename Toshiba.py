from micropython import const
from ir_tx import IR, STOP

_TBURST = const(543)
_T_ONE = const(1623)

class TOSHIBA(IR):
    valid = (0xffff, 0xff, 0)  # Max addr, data, toggle
    niz2 = [0xf2, 0x0d, 0x05, 0xfa, 0x01, 0x80, 0x00, 0x00, 0x21, 0x02, 0x00]
    niz  = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
    niz1 = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
    #samsung = False

    def __init__(self, pin, freq=38000, verbose=False):  # NEC specifies 38KHz also Samsung
        super().__init__(pin, freq, 200, 33, verbose)  # Measured duty ratio 33%

    def _bit(self, b):
        self.append(_TBURST, _T_ONE if b else _TBURST)

    def tx(self, addr, data, _):  # Ignore toggle
        self.append(4500, 4500)
        #if addr < 256:  # Short address: append complement
        #    addr |= addr << 8
#         data |= ((data ^ 0xff) << 8)
#         for _ in range(16):
#             self._bit(data & 1)
#             data >>= 1

        if addr >> 3 == 1:
            self.niz = self.niz1
            self.niz[:5] = 0xf2, 0xd,0x5, 0xfa, 0x1
            self.niz[5] = data << 4
            self.niz[6] = addr ^ 8
            self.niz[7] = 0x00
            self.niz[8:10] = 0x21, 0x2
            self.niz[10] = 0x00
        else:
            self.niz[:5] = 0xf2, 0xd, 0x3, 0xfc, 0x1
            self.niz[5] = data << 4
            self.niz[6] = addr
            self.niz[len(self.niz) - 1] = 0
        for byte in self.niz[:-1]:
            self.niz[len(self.niz) -1] ^= byte
        for byte in self.niz:
            for _ in range(8):
                self._bit((byte >> 7) & 1)
                byte <<= 1
        self.append(_TBURST)

    def repeat(self):
        self.aptr = 0
        self.append(440, 7048, _TBURST)
        self.trigger()  # Initiate physical transmission.
