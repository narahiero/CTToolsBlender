
import unittest

import numpy as np

from .. import utils, yaz

from .tests_helper import data_file_path


class DecompressTests(unittest.TestCase):

    def test_decompress(self):
        data = utils.io.read_file(data_file_path('yaz/data.yaz0'))
        buf = yaz.decompress(data)
        self.assertTrue(np.array_equal(buf.getv(), [
            0xAA, 0x55, 0xAA, 0x55, 0xAA, 0x55, 0xAA, 0x55, 0xAA, 0x55, 0xAA, 0x55, 0xAA, 0x55, 0xAA, 0x55,
            0x11, 0x11, 0x11, 0x22, 0x22, 0x22, 0x33, 0x33, 0x33, 0x11, 0x11, 0x11, 0x22, 0x22, 0x22, 0x33,
            0x33, 0x33, 0x74, 0x65, 0x78, 0x74, 0x00, 0x74, 0x65, 0x78, 0x74, 0x31, 0x00, 0x74, 0x65, 0x78,
            0x74, 0x32, 0x00, 0x74, 0x65, 0x78, 0x74, 0x33, 0x00, 0x55, 0xAA, 0x55, 0xAA, 0x55, 0xAA, 0x55,
            0xAA, 0x55, 0x11, 0x11, 0x11, 0x22, 0x22, 0x22, 0x33, 0x33, 0x33, 0x11, 0x11, 0x11, 0x22, 0x22,
        ]))

        data = utils.io.read_file(data_file_path('yaz/text.yaz1'))
        text = yaz.decompress(data)
        self.assertEqual(text.gets(), "This is some compressed text that, when decompressed, will produce some uncompressed text.")


class CompressTests(unittest.TestCase):

    def test_compress_none(self):
        data = utils.io.read_file(data_file_path('yaz/cmp0.bin'))
        out = yaz.compress(data, format=yaz.Format.YAZ1, level=yaz.Level.NONE)
        expect = utils.io.read_file(data_file_path('yaz/cmp0.yaz1'))
        self.assertTrue(np.array_equal(out.getv(), expect.getv()))

    def test_compress_best(self):
        data = utils.io.read_file(data_file_path('yaz/cmp0.bin'))
        out = yaz.compress(data, format=yaz.Format.YAZ0, level=yaz.Level.BEST)

        dcmp = yaz.decompress(out)
        self.assertTrue(dcmp.getv(), data.clear().getv())
