
import os
import unittest

import numpy as np

from .. import utils
from ..memory import Buffer

from .tests_helper import data_file_path


class IOTests(unittest.TestCase):

    def test_read_file(self):
        data = utils.io.read_file(data_file_path('data.bin'))
        self.assertTrue(np.array_equal(data.getv(), [0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0xFF, 0x7F, 0x3F, 0x1F, 0x0F, 0x07, 0x03, 0x01]))

        data = utils.io.read_file(data_file_path('data.txt'))
        self.assertEqual(data.gets(), "This is some text.")

    def test_write_file(self):
        data = [0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF]
        buf = Buffer(size=len(data))
        buf.putv(data).flip()

        outpath = data_file_path('out.bin')
        utils.io.write_file(outpath, buf)
        self.assertTrue(os.path.isfile(outpath))

        buf = utils.io.read_file(outpath)
        self.assertTrue(np.array_equal(buf.getv(), data))

        os.remove(outpath)

        # ------------------------------

        data = "A test string."
        buf = Buffer(size=len(data))
        buf.puts(data).flip()

        outpath = data_file_path('out.txt')
        utils.io.write_file(outpath, buf)
        self.assertTrue(os.path.isfile(outpath))

        buf = utils.io.read_file(outpath)
        self.assertEqual(buf.gets(), data)

        os.remove(outpath)
