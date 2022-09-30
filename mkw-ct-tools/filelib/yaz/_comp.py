
from enum import auto, Enum

import numpy as np

from ..memory import Buffer

import time


class Format(Enum):
    """
    The Yaz compression format. Note that the only difference between the 2 is
    simply the magic, the compression method is the same.
    """
    YAZ0 = 0
    YAZ1 = 1


class Level(Enum):
    """
    The level of compression to use. Better compression rates mean longer
    execution time.
    """
    NONE = auto()
    """
    No compression at all, the data length is increased by roughly 12.5%.
    """
    FAST = auto()
    """
    """
    BEST = auto()
    """
    Perfect compression.
    """


def _validate_args(format, level):
    if not isinstance(format, Format):
        raise ValueError(f"format must be of type 'yaz.Format', not '{type(format).__name__}'")
    if not isinstance(level, Level):
        raise ValueError(f"level must be of type 'yaz.Level', not '{type(level).__name__}'")

def _calc_max_output_size(datalen):
    """
    ```
    0x10: header length
    datalen: uncompressed data length
    (datalen >> 3): 1:1 copy chunk header (0xFF) for every 8 byte
    (1 if datalen & 7 > 0 else 0): additional 1:1 copy chunk header for remaining data
    ```
    """
    return 0x10 + datalen + (datalen >> 3) + (1 if datalen & 7 > 0 else 0)

def _write_header(out: Buffer, format: Format, datalen: int):
    out.puts('Yaz0' if format is Format.YAZ0 else 'Yaz1')
    out.put32(datalen)
    out.put32(0)
    out.put32(0)


class _LookupTable:

    def __init__(self, level):
        if level is Level.FAST:
            self._search_len = 0x100
        else:  # Level.BEST
            self._search_len = 0x1000

        self._data = np.zeros((0x100, (self._search_len)<<1), np.uint16)
        self._off = self._search_len - 1

    def find_best_match(self, buf: Buffer):
        data = buf.data
        pos = buf.pos
        start = pos + 1
        size = 0x111 if 0x111 < buf.remaining else buf.remaining
        end = pos + size

        off = self._off
        limit = self._search_len + off

        offs = self._data[data[pos]]
        doffs = offs[1:offs[0]+1]
        first = 0
        for doff in doffs:
            if doff <= limit:
                break
            first += 1

        doffs = doffs[first:]
        best = 0
        bestback = 0
        for doff in doffs:
            back = doff - off
            if back <= 0:
                break  # all remaining offsets are after the current location

            j = start
            while j < end and data[j] == data[j-back]:
                j += 1  # loop until difference is found or max size is reached

            if best < j:
                best = j
                bestback = back

            if best == size:
                break  # it's impossible to find a better match

        return (best-pos, bestback)

    def fill(self, buf: Buffer):
        curr = buf.data[buf.pos:buf.pos+min(self._search_len, buf.remaining)]
        for i in range(len(curr)):
            offs = self._data[curr[i]]
            offs[0] += 1
            count = offs[0]
            offs[count] = self._search_len - 1 - i

    def update(self, buf: Buffer):
        off_limit = self._search_len + self._off
        off_add = self._search_len - 1 - self._off

        for offs in self._data:
            end = offs[0] + 1
            i = 1
            while i < end:
                if offs[i] < off_limit:
                    break
                i += 1

            move = i - 1
            while i < end:
                offs[i-move] = offs[i] + off_add
                i += 1

            offs[0] -= move  # subtract from count

        self.fill(buf)

    def move(self, count, buf: Buffer):
        self._off -= count
        if self._off < 0:
            self.update(buf)
            self._off = self._search_len - 1

def _compress_data(out: Buffer, data: Buffer, level: Level):
    if level is Level.NONE:
        while data.remaining > 8:
            out.put8(0xFF)
            out.putv(data.getv(size=8))

        head = 0
        for bit in range(data.remaining):
            head |= 1 << (7 - bit)
        out.put8(head)
        out.putv(data.getv())

    else:
        lut = _LookupTable(level)
        lut.fill(data)

        odata = out.data
        opos = out.pos

        group = np.ndarray(0x18)
        gpos = 0
        head = 0
        bit = 8
        while data.remaining > 0:
            (size, back) = lut.find_best_match(data)

            if size >= 0x3:
                if size >= 0x12:
                    group[gpos  ] = (back - 1) >> 8
                    group[gpos+1] = (back - 1) & 0xFF
                    group[gpos+2] = size - 0x12
                    gpos += 3
                else:
                    group[gpos  ] = ((size - 0x2) << 4) | ((back - 1) >> 8)
                    group[gpos+1] = (back - 1) & 0xFF
                    gpos += 2

                data.pos += size
                lut.move(size, data)

            else:
                group[gpos] = data.data[data.pos]
                gpos += 1
                data.pos += 1
                head |= 0x1  # set bit of current chunk

                lut.move(1, data)

            bit -= 1
            if bit == 0:  # flush and move to next group
                odata[opos] = head
                for i in range(gpos):
                    odata[opos+i+1] = group[i]
                opos += gpos + 1
                gpos = 0
                head = 0
                bit = 8
            else:  # move to next chunk
                head <<= 1

        if bit < 8:
            head <<= bit - 1
            odata[opos] = head
            for i in range(gpos):
                odata[opos+i+1] = group[i]
            opos += gpos + 1

        out.pos = opos

def compress(data: Buffer, format: Format, level: Level) -> Buffer:
    """
    """
    _validate_args(format, level)

    out = Buffer(size=_calc_max_output_size(data.remaining))

    _write_header(out, format, data.remaining)
    _compress_data(out, data, level)

    return out.flip()
