#!/usr/bin/env python3
# place cgrom.dat at current directory and run
# will generate jpnhn16x.68 and jpnzn16x.68

import struct

# JIS lower: 0x21 - 0x7e
jishir = [(0x21, 0x28), (0x30, 0x4f), (0x50, 0x74)]

def mkhdr(x, y, dbcs):
    return struct.pack("<6s8sBBB", b"FONTX2", b"x68cgrom", x, y, dbcs)

def jis2sjis(jis):
    jis += 0x217e
    jis ^= 0x4000
    c = (jis & 0x0100) != 0
    jis = (jis & 0x00ff) | (((jis >> 1) | 0x8000) & 0xff00)
    if not c:
        jisl = jis & 0x00ff
        jisl -= 0xde
        if (jisl >> 8):
            jisl -= 1
        jisl -= 0x80
        jis = (jis & 0xff00) | (jisl & 0x00ff)
    return jis

def jishi_to_sjisranges(jishi):
    sjisbeg = jis2sjis((jishi << 8) | 0x21)
    sjism1 = jis2sjis((jishi << 8) | 0x5f)
    sjism2 = jis2sjis((jishi << 8) | 0x60)
    sjisend = jis2sjis((jishi << 8) | 0x7e)

    return [(sjisbeg, sjism1), (sjism2, sjisend)]

def gen_jisblks():
    jisblks = []
    for jishit in jishir:
        for jishi in range(jishit[0], jishit[1]+1):
            jisblks += jishi_to_sjisranges(jishi)

    # join adjacent blocks
    njisblks = []
    prevnblk = None
    for jisblk in jisblks:
        if not prevnblk:
            njisblks += [jisblk]
            prevnblk = jisblk
        else:
            if (prevnblk[1] + 1) == jisblk[0]:
                njisblks = njisblks[:-1] + [(prevnblk[0], jisblk[1])]
            else:
                njisblks += [jisblk]
            prevnblk = njisblks[-1]

    return njisblks

cgfile = open("cgrom.dat", "rb")
cgbytes = memoryview(cgfile.read(0xc0000))


jisblks = gen_jisblks()

blkhdr = b""

blkhdr += struct.pack("<B", len(jisblks))

for jisblk in jisblks:
    blkhdr += struct.pack("<2H", jisblk[0], jisblk[1])

# 8x16 ANK
h16f = open("jpnhn16x.68", "wb")
h16f.write(mkhdr(8, 16, 0))
h16f.write(cgbytes[0x3a800:0x3b800])
h16f.close()

# 16x16 SJIS
z16f = open("jpnzn16x.68", "wb")
z16f.write(mkhdr(16, 16, 1))
z16f.write(blkhdr)
z16f.write(cgbytes[0x00000:0x388c0])
z16f.close()
