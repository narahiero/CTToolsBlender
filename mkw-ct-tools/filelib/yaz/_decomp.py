
from .. import utils
from ..memory import Buffer

from . import YazError


def _read_header(data: Buffer) -> int:
    if data.remaining < 0x10:
        raise YazError(f"incomplete Yaz header: insufficient data; {data.remaining} < {0x10}")

    magic = data.gets(size=4)
    if magic != 'Yaz0' and magic != 'Yaz1':
        raise YazError("invalid Yaz header: invalid magic")

    datalen = data.get32()

    data.get32()
    data.get32()

    return datalen

def _decompress_data(data: Buffer, out: Buffer):
    while data.remaining > 0:
        head = data.get8()
        for bit in range(7, -1, -1):
            if data.remaining == 0:
                break

            if ((head >> bit) & 1) == 1:
                if out.remaining == 0:
                    raise YazError(f"invalid Yaz data: reached end of output buffer before end of data; at pos={data.pos:#x}")

                out.put8(data.get8())

            else:
                if data.remaining < 2:
                    raise YazError(f"invalid Yaz data: reached end of data before end of chunk header; at pos={data.pos:#x}")

                chunkhead = data.get16()
                size = (chunkhead >> 0xC) + 0x2
                if size == 0x2:
                    if data.remaining < 1:
                        raise YazError(f"invalid Yaz data: reached end of data before end of chunk header; at pos={data.pos:#x}")
                    size = data.get8() + 0x12

                if out.remaining < size:
                    raise YazError(f"invalid Yaz data: reached end of output buffer before end of data; at pos={data.pos:#x}")

                off = (chunkhead & 0xFFF) + 0x1
                if off > out.pos:
                    raise YazError(f"invalid Yaz data: chunk refers to data before start of output buffer; at pos={data.pos:#x}")

                backref = Buffer(src=out, off=out.pos-off, size=size)
                while backref.remaining > 0:
                    out.put8(backref.get8())

def decompress(data: Buffer) -> Buffer:
    """
    Decompress Yaz0 or Yaz1 data. If the data is not compressed using Yaz0 or
    Yaz1, or is corrupted, a `YazError` is raised.
    """
    datalen = _read_header(data)

    out = Buffer(size=datalen)
    _decompress_data(data, out)
    out.flip()

    return out
