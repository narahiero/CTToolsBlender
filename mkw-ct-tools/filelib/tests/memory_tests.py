
import unittest

import numpy as np

from ..memory import Buffer, BufferOverflowError


class TestBufferConstructor(unittest.TestCase):

    def test_no_arg(self):
        with self.assertRaises(TypeError):
            Buffer()

    def test_size(self):
        for size in range(64):
            buf = Buffer(size=size)
            self.assertEqual(len(buf.data), size)
            self.assertTrue(np.array_equal(buf.data, np.zeros(size)))

    def test_size_errors(self):
        for size in range(-64, 64):
            if size < 0:
                with self.assertRaises(ValueError):
                    Buffer(size=size)
            else:
                Buffer(size=size)

    def test_src(self):
        buf0 = Buffer(size=8)
        for i in range(8):
            buf0.data[i] = 2 ** i

        buf1 = Buffer(src=buf0)
        self.assertTrue(np.array_equal(buf0.data, buf1.data))

    def test_src_copy(self):
        buf0 = Buffer(size=8)
        for i in range(8):
            buf0.data[i] = 2 ** i

        buf1 = Buffer(src=buf0, copy=True)
        self.assertTrue(np.array_equal(buf0.data, buf1.data))

        buf0.data[0] = 5
        self.assertFalse(np.array_equal(buf0.data, buf1.data))

    def test_src_share(self):
        buf0 = Buffer(size=8)
        for i in range(8):
            buf0.data[i] = 2 ** i

        buf1 = Buffer(src=buf0, copy=False)
        self.assertTrue(np.array_equal(buf0.data, buf1.data))

        buf0.data[4] = 100
        self.assertTrue(np.array_equal(buf0.data, buf1.data))

        buf1.data[7] = 150
        self.assertTrue(np.array_equal(buf0.data, buf1.data))

        buf2 = Buffer(src=buf1) # Ensure copy defaults to False
        self.assertTrue(np.array_equal(buf0.data, buf2.data))
        self.assertTrue(np.array_equal(buf1.data, buf2.data))

        buf2.data[7] = 75
        self.assertTrue(np.array_equal(buf0.data, buf2.data))
        self.assertTrue(np.array_equal(buf1.data, buf2.data))

    def test_src_size(self):
        buf0 = Buffer(size=8)
        for i in range(8):
            buf0.data[i] = 2 ** i

        buf1 = Buffer(src=buf0, copy=True, size=4)
        self.assertEqual(len(buf1.data), 4)
        self.assertFalse(np.array_equal(buf0.data, buf1.data))
        self.assertTrue(np.array_equal(buf0.data[:4], buf1.data))

        buf2 = Buffer(src=buf0, size=6)
        self.assertEqual(len(buf2.data), 6)
        self.assertFalse(np.array_equal(buf0.data, buf2.data))
        self.assertTrue(np.array_equal(buf0.data[:6], buf2.data))
        self.assertFalse(np.array_equal(buf1.data, buf2.data))
        self.assertTrue(np.array_equal(buf1.data, buf2.data[:4]))

        buf0.data[2] = 50
        self.assertFalse(np.array_equal(buf0.data[:4], buf1.data))
        self.assertTrue(np.array_equal(buf0.data[:6], buf2.data))
        self.assertFalse(np.array_equal(buf1.data, buf2.data[:4]))

        buf1.data[1] = 100
        self.assertFalse(np.array_equal(buf0.data[:4], buf1.data))
        self.assertTrue(np.array_equal(buf0.data[:6], buf2.data))
        self.assertFalse(np.array_equal(buf1.data, buf2.data[:4]))

    def test_src_off(self):
        buf0 = Buffer(size=8)
        for i in range(8):
            buf0.data[i] = 2 ** i

        buf1 = Buffer(src=buf0, off=2)
        self.assertEqual(len(buf1.data), 6)
        self.assertTrue(np.array_equal(buf0.data[2:], buf1.data))

        buf2 = Buffer(src=buf0, off=-5)
        self.assertEqual(len(buf2.data), 5)
        self.assertTrue(np.array_equal(buf0.data[-5:], buf2.data))

    def test_src_off_size(self):
        buf0 = Buffer(size=8)
        for i in range(8):
            buf0.data[i] = 2 ** i

        buf1 = Buffer(src=buf0, copy=True, off=1, size=6)
        self.assertEqual(len(buf1.data), 6)
        self.assertFalse(np.array_equal(buf0.data, buf1.data))
        self.assertTrue(np.array_equal(buf0.data[1:7], buf1.data))

        buf2 = Buffer(src=buf1, off=2, size=3)
        self.assertEqual(len(buf2.data), 3)
        self.assertFalse(np.array_equal(buf0.data, buf2.data))
        self.assertTrue(np.array_equal(buf0.data[3:6], buf2.data))
        self.assertFalse(np.array_equal(buf1.data, buf2.data))
        self.assertTrue(np.array_equal(buf1.data[2:5], buf2.data))

        buf0.data[5] = 50
        self.assertFalse(np.array_equal(buf0.data[1:7], buf1.data))
        self.assertFalse(np.array_equal(buf0.data[3:6], buf2.data))
        self.assertTrue(np.array_equal(buf1.data[2:5], buf2.data))

        buf1.data[2] = 25
        self.assertFalse(np.array_equal(buf0.data[1:7], buf1.data))
        self.assertFalse(np.array_equal(buf0.data[3:6], buf2.data))
        self.assertTrue(np.array_equal(buf1.data[2:5], buf2.data))

        buf2.data[1] = 100
        self.assertFalse(np.array_equal(buf0.data[1:7], buf1.data))
        self.assertFalse(np.array_equal(buf0.data[3:6], buf2.data))
        self.assertTrue(np.array_equal(buf1.data[2:5], buf2.data))

    def test_src_default_off_size(self):
        buf0 = Buffer(size=8)
        for i in range(8):
            buf0.data[i] = 2 ** i

        buf0.pos = 3
        buf0.limit = 6
        buf1 = Buffer(src=buf0)
        self.assertTrue(np.array_equal(buf0.data[3:6], buf1.data))

        buf0.pos = 2
        buf0.limit = 4
        buf2 = Buffer(src=buf0, off=1)
        self.assertTrue(np.array_equal(buf0.data[1:4], buf2.data))

        buf0.pos = 1
        buf0.limit = 7
        buf3 = Buffer(src=buf0, size=5)
        self.assertTrue(np.array_equal(buf0.data[1:6], buf3.data))

    def test_src_off_size_errors(self):
        buf = Buffer(size=8)

        for size in range(-8, 16):
            if size < 0:
                with self.assertRaises(ValueError):
                    Buffer(src=buf, size=size)
            elif size > 8:
                with self.assertRaises(BufferOverflowError):
                    Buffer(src=buf, size=size)
            else:
                Buffer(src=buf, size=size)

        for off in range(-16, 16):
            if abs(off) > 8:
                with self.assertRaises(BufferOverflowError):
                    Buffer(src=buf, off=off)
            else:
                Buffer(src=buf, off=off)

        for size in range(16):
            for limit in range(8):
                buf.limit = limit
                for off in range(-16, 16):
                    if abs(off) > limit or (off >= 0 and off + size > limit) or (off < 0 and limit + off + size > limit):
                        with self.assertRaises(BufferOverflowError):
                            Buffer(src=buf, off=off, size=size)
                    else:
                        Buffer(src=buf, off=off, size=size)

    def test_slice(self):  # included since slice is just a shorthand constructor
        buf0 = Buffer(size=8)
        for i in range(8):
            buf0.data[i] = 2 ** i

        buf1 = buf0.slice(size=5)
        self.assertTrue(np.array_equal(buf0.data[:5], buf1.data))

        buf1.data[3] = 127
        self.assertTrue(np.array_equal(buf0.data[:5], buf1.data))

        buf2 = buf0.slice(copy=True, off=2, size=4)
        self.assertTrue(np.array_equal(buf0.data[2:6], buf2.data))
        self.assertTrue(np.array_equal(buf1.data[2:], buf2.data[:3]))

        buf0.data[2] = 255
        self.assertTrue(np.array_equal(buf0.data[:5], buf1.data))
        self.assertFalse(np.array_equal(buf0.data[2:6], buf2.data))
        self.assertFalse(np.array_equal(buf1.data[2:], buf2.data[:3]))

        buf0.pos = 2
        buf0.limit = 6
        buf3 = buf0.slice()
        self.assertTrue(np.array_equal(buf0.data[2:6], buf3.data))

    def test_copy(self):
        buf0 = Buffer(size=8)
        for i in range(8):
            buf0.data[i] = 2 ** i

        buf1 = buf0.copy(off=1, size=5)
        self.assertTrue(np.array_equal(buf0.data[1:6], buf1.data))

        buf0.data[4] = 127
        self.assertFalse(np.array_equal(buf0.data[1:6], buf1.data))

        buf0.pos = 3
        buf0.limit = 7
        buf2 = buf0.copy()
        self.assertTrue(np.array_equal(buf0.data[3:7], buf2.data))


class TestBufferProperties(unittest.TestCase):

    def test_len(self):
        for size in range(64):
            buf = Buffer(size=size)
            self.assertEqual(len(buf), size)
            self.assertEqual(len(buf), len(buf.data))

    def test_limit(self):
        for size in range(8):
            buf = Buffer(size=size)
            self.assertEqual(buf.limit, size)

            for limit in range(-size-8, size+8):
                if abs(limit) > len(buf):
                    with self.assertRaises(BufferOverflowError):
                        buf.limit = limit
                else:
                    buf.limit = limit
                    if limit >= 0:
                        self.assertEqual(buf.limit, limit)
                    else:
                        self.assertEqual(buf.limit, size + limit)

    def test_pos(self):
        for size in range(8):
            buf = Buffer(size=size)
            self.assertEqual(buf.pos, 0)

            for limit in range(size+1):
                buf.limit = limit
                for pos in range(-size-8, size+8):
                    if abs(pos) > limit:
                        with self.assertRaises(BufferOverflowError):
                            buf.pos = pos
                    else:
                        buf.pos = pos
                        if pos >= 0:
                            self.assertEqual(buf.pos, pos)
                        else:
                            self.assertEqual(buf.pos, limit + pos)

    def test_remaining(self):
        for size in range(8):
            buf = Buffer(size=size)

            for limit in range(size+1):
                buf.limit = limit
                for pos in range(limit+1):
                    buf.pos = pos
                    self.assertEqual(buf.remaining, limit - pos)

    def test_clear(self):
        buf = Buffer(size=8)

        buf.pos = 5
        buf.limit = 6
        buf.clear()
        self.assertEqual(buf.pos, 0)
        self.assertEqual(buf.limit, 8)

    def test_flip(self):
        buf = Buffer(size=8)

        buf.pos = 3
        buf.limit = 5
        buf.flip()
        self.assertEqual(buf.pos, 0)
        self.assertEqual(buf.limit, 3)


class TestBufferPutMethods(unittest.TestCase):

    def test_put8(self):
        buf = Buffer(size=6)

        buf.put8(24)
        self.assertEqual(buf.pos, 1)
        self.assertTrue(np.array_equal(buf.data, [24, 0, 0, 0, 0, 0]))

        buf.put8(64)
        self.assertEqual(buf.pos, 2)
        self.assertTrue(np.array_equal(buf.data, [24, 64, 0, 0, 0, 0]))

        buf.put8(96, pos=5)
        self.assertEqual(buf.pos, 2)
        self.assertTrue(np.array_equal(buf.data, [24, 64, 0, 0, 0, 96]))

        buf.put8(8)
        self.assertEqual(buf.pos, 3)
        self.assertTrue(np.array_equal(buf.data, [24, 64, 8, 0, 0, 96]))

        buf.pos = 4
        buf.put8(192)
        self.assertEqual(buf.pos, 5)
        self.assertTrue(np.array_equal(buf.data, [24, 64, 8, 0, 192, 96]))

        buf.put8(36)
        self.assertEqual(buf.pos, 6)
        self.assertTrue(np.array_equal(buf.data, [24, 64, 8, 0, 192, 36]))

        buf.put8(2, pos=-5)
        self.assertEqual(buf.pos, 6)
        self.assertTrue(np.array_equal(buf.data, [24, 2, 8, 0, 192, 36]))

        buf.pos = 3
        buf.put8(6).put8(48).put8(12, pos=1)
        self.assertEqual(buf.pos, 5)
        self.assertTrue(np.array_equal(buf.data, [24, 12, 8, 6, 48, 36]))

    def test_put8_errors(self):
        for size in range(16):
            buf = Buffer(size=size)

            for limit in range(size+1):
                buf.limit = limit
                while buf.remaining > 0:
                    buf.put8(0)
                with self.assertRaises(BufferOverflowError):
                    buf.put8(0)

                for pos in range(-limit-8, limit+8):
                    if abs(pos) > limit or pos == limit:
                        with self.assertRaises(BufferOverflowError):
                            buf.put8(0, pos=pos)
                    else:
                        buf.put8(0, pos=pos)

    def test_put16(self):
        buf = Buffer(size=8)

        buf.put16(0x1234)
        self.assertEqual(buf.pos, 2)
        self.assertTrue(np.array_equal(buf.data, [0x12, 0x34, 0, 0, 0, 0, 0, 0]))

        buf.put16(0x5678)
        self.assertEqual(buf.pos, 4)
        self.assertTrue(np.array_equal(buf.data, [0x12, 0x34, 0x56, 0x78, 0, 0, 0, 0]))

        buf.put16(0x9ABC, pos=5)
        self.assertEqual(buf.pos, 4)
        self.assertTrue(np.array_equal(buf.data, [0x12, 0x34, 0x56, 0x78, 0, 0x9A, 0xBC, 0]))

        buf.pos = 1
        buf.put16(0xDEF0).put16(0x0FED).put16(0xEFD0, pos=0)
        self.assertEqual(buf.pos, 5)
        self.assertTrue(np.array_equal(buf.data, [0xEF, 0xD0, 0xF0, 0x0F, 0xED, 0x9A, 0xBC, 0]))

    def test_put16_errors(self):
        for size in range(16):
            buf = Buffer(size=size)

            for limit in range(size+1):
                buf.limit = limit
                while buf.remaining >= 2:
                    buf.put16(0)
                with self.assertRaises(BufferOverflowError):
                    buf.put16(0)

                for pos in range(-limit-8, limit+8):
                    if abs(pos) > limit or pos + 2 > limit or pos == -1:
                        with self.assertRaises(BufferOverflowError):
                            buf.put16(0, pos=pos)
                    else:
                        buf.put16(0, pos=pos)

    def test_put32(self):
        buf = Buffer(size=12)

        buf.put32(0x10204080)
        self.assertEqual(buf.pos, 4)
        self.assertTrue(np.array_equal(buf.data, [0x10, 0x20, 0x40, 0x80, 0, 0, 0, 0, 0, 0, 0, 0]))

        buf.put32(0x01020408)
        self.assertEqual(buf.pos, 8)
        self.assertTrue(np.array_equal(buf.data, [0x10, 0x20, 0x40, 0x80, 0x01, 0x02, 0x04, 0x08, 0, 0, 0, 0]))

        buf.pos = 5
        buf.put32(0xA0C0E0FF)
        self.assertEqual(buf.pos, 9)
        self.assertTrue(np.array_equal(buf.data, [0x10, 0x20, 0x40, 0x80, 0x01, 0xA0, 0xC0, 0xE0, 0xFF, 0, 0, 0]))

        buf.put32(0xB0D0F010, pos=3)
        self.assertEqual(buf.pos, 9)
        self.assertTrue(np.array_equal(buf.data, [0x10, 0x20, 0x40, 0xB0, 0xD0, 0xF0, 0x10, 0xE0, 0xFF, 0, 0, 0]))

        buf.pos = 2
        buf.put32(0x18283848).put32(0x58687888).put32(0x98A8B8C8, pos=8)
        self.assertEqual(buf.pos, 10)
        self.assertTrue(np.array_equal(buf.data, [0x10, 0x20, 0x18, 0x28, 0x38, 0x48, 0x58, 0x68, 0x98, 0xA8, 0xB8, 0xC8]))

    def test_put32_errors(self):
        for size in range(16):
            buf = Buffer(size=size)

            for limit in range(size+1):
                buf.limit = limit
                while buf.remaining >= 4:
                    buf.put32(0)
                with self.assertRaises(BufferOverflowError):
                    buf.put32(0)

                for pos in range(-limit-8, limit+8):
                    if abs(pos) > limit or pos + 4 > limit or (pos < 0 and pos > -4):
                        with self.assertRaises(BufferOverflowError):
                            buf.put32(0, pos=pos)
                    else:
                        buf.put32(0, pos=pos)

    def test_putf(self):
        buf = Buffer(size=12)

        buf.putf(1.) # 0x3F800000
        self.assertEqual(buf.pos, 4)
        self.assertTrue(np.array_equal(buf.data, [0x3F, 0x80, 0x00, 0x00, 0, 0, 0, 0, 0, 0, 0, 0]))

        buf.putf(-3.5) # 0xC0600000
        self.assertEqual(buf.pos, 8)
        self.assertTrue(np.array_equal(buf.data, [0x3F, 0x80, 0x00, 0x00, 0xC0, 0x60, 0x00, 0x00, 0, 0, 0, 0]))

        buf.pos = 2
        buf.putf(42.375) # 0x42298000
        self.assertEqual(buf.pos, 6)
        self.assertTrue(np.array_equal(buf.data, [0x3F, 0x80, 0x42, 0x29, 0x80, 0x00, 0x00, 0x00, 0, 0, 0, 0]))

        buf.putf(82572.6875, pos=7) # 0x47A14658
        self.assertEqual(buf.pos, 6)
        self.assertTrue(np.array_equal(buf.data, [0x3F, 0x80, 0x42, 0x29, 0x80, 0x00, 0x00, 0x47, 0xA1, 0x46, 0x58, 0]))

        buf.pos = 3
        buf.putf(-6.75).putf(12.125).putf(-2., pos=8) # 0xC0D80000 0x41420000 0xC0000000
        self.assertEqual(buf.pos, 11)
        self.assertTrue(np.array_equal(buf.data, [0x3F, 0x80, 0x42, 0xC0, 0xD8, 0x00, 0x00, 0x41, 0xC0, 0x00, 0x00, 0x00]))

    def test_putf_errors(self):
        for size in range(16):
            buf = Buffer(size=size)

            for limit in range(size+1):
                buf.limit = limit
                while buf.remaining >= 4:
                    buf.putf(0.)
                with self.assertRaises(BufferOverflowError):
                    buf.putf(0.)

                for pos in range(-limit-8, limit+8):
                    if abs(pos) > limit or pos + 4 > limit or (pos < 0 and pos > -4):
                        with self.assertRaises(BufferOverflowError):
                            buf.putf(0., pos=pos)
                    else:
                        buf.putf(0., pos=pos)


class TestBufferGetMethods(unittest.TestCase):

    def test_get8(self):
        buf = Buffer(size=8)
        buf.put32(0x12345678).put32(0x9ABCDEF0)
        buf.pos = 0

        self.assertEqual(buf.get8(), 0x12)
        self.assertEqual(buf.pos, 1)

        self.assertEqual(buf.get8(), 0x34)
        self.assertEqual(buf.pos, 2)

        self.assertEqual(buf.get8(pos=4), 0x9A)
        self.assertEqual(buf.pos, 2)

    def test_get8_errors(self):
        for size in range(16):
            buf = Buffer(size=size)

            for limit in range(size+1):
                buf.limit = limit
                while buf.remaining > 0:
                    buf.get8()
                with self.assertRaises(BufferOverflowError):
                    buf.get8()

                for pos in range(-limit-8, limit+8):
                    if abs(pos) > limit or pos == limit:
                        with self.assertRaises(BufferOverflowError):
                            buf.get8(pos=pos)
                    else:
                        buf.get8(pos=pos)

    def test_get16(self):
        buf = Buffer(size=8)
        buf.put32(0xFEDCBA98).put32(0x76543210)
        buf.pos = 0

        self.assertEqual(buf.get16(), 0xFEDC)
        self.assertEqual(buf.pos, 2)

        self.assertEqual(buf.get16(), 0xBA98)
        self.assertEqual(buf.pos, 4)

        self.assertEqual(buf.get16(pos=3), 0x9876)
        self.assertEqual(buf.pos, 4)

    def test_get16_errors(self):
        for size in range(16):
            buf = Buffer(size=size)

            for limit in range(size+1):
                buf.limit = limit
                while buf.remaining >= 2:
                    buf.get16()
                with self.assertRaises(BufferOverflowError):
                    buf.get16()

                for pos in range(-limit-8, limit+8):
                    if abs(pos) > limit or pos + 2 > limit or pos == -1:
                        with self.assertRaises(BufferOverflowError):
                            buf.get16(pos=pos)
                    else:
                        buf.get16(pos=pos)

    def test_get32(self):
        buf = Buffer(size=14)
        buf.put32(0x11223344).put32(0x55667788).put32(0x99AABBCC).put16(0xDDEE)
        buf.pos = 0

        self.assertEqual(buf.get32(), 0x11223344)
        self.assertEqual(buf.pos, 4)

        self.assertEqual(buf.get32(), 0x55667788)
        self.assertEqual(buf.pos, 8)

        self.assertEqual(buf.get32(pos=9), 0xAABBCCDD)
        self.assertEqual(buf.pos, 8)

    def test_get32_errors(self):
        for size in range(16):
            buf = Buffer(size=size)

            for limit in range(size+1):
                buf.limit = limit
                while buf.remaining >= 4:
                    buf.get32()
                with self.assertRaises(BufferOverflowError):
                    buf.get32()

                for pos in range(-limit-8, limit+8):
                    if abs(pos) > limit or pos + 4 > limit or (pos < 0 and pos > -4):
                        with self.assertRaises(BufferOverflowError):
                            buf.get32(pos=pos)
                    else:
                        buf.get32(pos=pos)

    def test_getf(self):
        buf = Buffer(size=16)
        buf.putf(5.).putf(-11.25).put16(0).put32(0x42F7C000) # 123.875
        buf.pos = 0

        self.assertEqual(buf.getf(), 5.)
        self.assertEqual(buf.pos, 4)

        self.assertEqual(buf.getf(), -11.25)
        self.assertEqual(buf.pos, 8)

        self.assertEqual(buf.getf(pos=10), 123.875)
        self.assertEqual(buf.pos, 8)

    def test_getf_errors(self):
        for size in range(16):
            buf = Buffer(size=size)

            for limit in range(size+1):
                buf.limit = limit
                while buf.remaining >= 4:
                    buf.getf()
                with self.assertRaises(BufferOverflowError):
                    buf.getf()

                for pos in range(-limit-8, limit+8):
                    if abs(pos) > limit or pos + 4 > limit or (pos < 0 and pos > -4):
                        with self.assertRaises(BufferOverflowError):
                            buf.getf(pos=pos)
                    else:
                        buf.getf(pos=pos)


if __name__ == '__main__':
    unittest.main()
