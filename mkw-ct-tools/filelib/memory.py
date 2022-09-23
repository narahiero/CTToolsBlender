
from struct import Struct

import numpy as np


class BufferOverflowError(RuntimeError):
    """
    A BufferOverflowError occurs when attempting to access or modify data
    outside of the :class:`Buffer`'s memory block.
    """

    def __init__(self, *args):
        super().__init__(*args)


class Buffer:
    """
    If `src` is specified, and `copy` is `True`, the new buffer will be a copy
    of `src`.
    If `src` is specified, and `copy` is `False`, the new buffer will share the
    memory block of `src`.
    If `src` is not specified, an empty buffer is allocated.

    When `src` is specified, the data of the new buffer will be a subset of
    `src` starting from `off` with a length of `size`. If `size` is 0 (the
    default), then the length of the new buffer will be the length of `src`
    minus `off`.

    When `src` is not specified, the length of the new buffer is `size`, and
    `off` is ignored.

    :raises ValueError: If `src` is specified and `off` or `size` is less than
    0, or `off` is greater than or equal to `src` length, or the sum of `off`
    and `size` is greater than `src` length. If `src` is not specified and
    `size` is less than or equal to 0.

    :param src: Buffer containing the data of the new buffer
    :type src: Buffer, optional
    :param copy: Whether to copy or share data with `src`
    :type copy: bool, optional
    :param off: The offset into the data of `src`
    :type off: int, optional
    :param size: The size of the new buffer
    :type size: int, optional
    """

    def __init__(self, *, src=None, copy=False, off=0, size=0):
        if src is None:
            if size <= 0:
                raise ValueError(f"size must be > 0; {size=}")

            self._data = np.zeros(size, np.uint8)

        else:
            if size < 0:
                raise ValueError(f"size must be >= 0; {size=}")
            if off < 0:
                raise ValueError(f"off must be >= 0; {off=}")
            if off >= len(src):
                raise ValueError(f"off must be < src length; {off=}, {len(src)=}")
            if off + size > len(src):
                raise ValueError(f"off + size must be <= src length; {off+size=}, {len(src)=}")

            if size == 0:
                size = len(src) - off

            self._data = src._data[off:off+size]
            if copy:
                self._data = self._data.copy()

        self._pos = 0

        self._su8 = Struct('>B')
        self._su16 = Struct('>H')
        self._su32 = Struct('>I')
        self._sf32 = Struct('>f')

    def __len__(self):
        return len(self._data)

    @property
    def data(self) -> np.ndarray:
        """The backend numpy array"""
        return self._data

    @property
    def pos(self) -> int:
        """Current position"""
        return self._pos

    @pos.setter
    def pos(self, pos: int):
        if pos < 0 or pos > len(self):
            raise ValueError(f"pos must be >= 0 and <= the length; {pos=}, {len(self)=}")

        self._pos = pos

    def slice(self, *, copy=False, off=0, size=0):
        """
        Create a subset of this Buffer.

        This is a shortcut for the constructor and is the equivalent of the
        following:

            buf.slice(copy=c, off=o, size=s) # is equivalent to
            Buffer(src=buf, copy=c, off=o, size=s)

        :raises ValueError: If `off` or `size` is less than 0, or `off` is
        greater than or equal to the length of this buffer, or the sum of `off`
        and `size` is greater than the length of this buffer.

        :param copy: Whether to copy or share data with this buffer
        :type copy: bool, optional
        :param off: The offset into the data of this buffer
        :type off: int, optional
        :param size: The size of the new buffer
        :type size: int, optional
        :rtype: Buffer
        """
        return Buffer(src=self, copy=copy, off=off, size=size)

    def _put(self, strct, size, data, pos):
        if pos is None:
            if self._pos + size > len(self):
                raise BufferOverflowError()

            strct.pack_into(self._data, self._pos, data)
            self._pos += size

        else:
            if pos < 0 or pos + size > len(self):
                raise BufferOverflowError()

            strct.pack_into(self._data, pos, data)

        return self

    def put8(self, data: np.uint8, *, pos: int = None):
        """
        Put a single byte in the buffer.

        If `pos` is specified, put `data` at index `pos` in the buffer.
        If `pos` is not specified, put `data` at the current position and
        increment the current position by 1.

        :raises BufferOverflowError: If `pos` is specified and is less than 0 or
        greater than or equal to the buffer length. If `pos` is not specified
        and the current position is equal to the buffer length.

        :param data: The byte to put in the buffer
        :type data: np.uint8
        :param pos: The position in the buffer, or None to use current position
        :type pos: int, optional
        """
        return self._put(self._su8, 1, data, pos)

    def put16(self, data: np.uint16, pos: int = None):
        """
        Put a single short (2 bytes) in the buffer.

        If `pos` is specified, put `data` at index `pos` in the buffer.
        If `pos` is not specified, put `data` at the current position and
        increment the current position by 2.

        :raises BufferOverflowError: If `pos` is specified and is less than 0 or
        greater than the buffer length plus 2. If `pos` is not specified
        and the current position is greater than the buffer length plus 2.

        :param data: The short to put in the buffer
        :type data: np.uint16
        :param pos: The position in the buffer, or None to use current position
        :type pos: int, optional
        """
        return self._put(self._su16, 2, data, pos)

    def put32(self, data: np.uint32, pos: int = None):
        """
        Put a single integer (4 bytes) in the buffer.

        If `pos` is specified, put `data` at index `pos` in the buffer.
        If `pos` is not specified, put `data` at the current position and
        increment the current position by 4.

        :raises BufferOverflowError: If `pos` is specified and is less than 0 or
        greater than the buffer length plus 4. If `pos` is not specified
        and the current position is greater than the buffer length plus 4.

        :param data: The integer to put in the buffer
        :type data: np.uint32
        :param pos: The position in the buffer, or None to use current position
        :type pos: int, optional
        """
        return self._put(self._su32, 4, data, pos)

    def putf(self, data: np.float32, pos: int = None):
        """
        Put a single float (4 bytes) in the buffer.

        If `pos` is specified, put `data` at index `pos` in the buffer.
        If `pos` is not specified, put `data` at the current position and
        increment the current position by 4.

        :raises BufferOverflowError: If `pos` is specified and is less than 0 or
        greater than the buffer length plus 4. If `pos` is not specified
        and the current position is greater than the buffer length plus 4.

        :param data: The float to put in the buffer
        :type data: np.float32
        :param pos: The position in the buffer, or None to use current position
        :type pos: int, optional
        """
        return self._put(self._sf32, 4, data, pos)

    def _get(self, strct, size, pos):
        if pos is None:
            if self._pos + size > len(self):
                raise BufferOverflowError()

            retval = strct.unpack_from(self._data, self._pos)[0]
            self._pos += size

            return retval

        else:
            if pos < 0 or pos + size > len(self):
                raise BufferOverflowError()

            return strct.unpack_from(self._data, pos)[0]

    def get8(self, pos: int = None) -> np.uint8:
        """
        Get a single byte from the buffer.

        If `pos` is specified, return the byte at index `pos` from the buffer.
        If `pos` is not specified, return the byte at the current position and
        increment the current position by 1.

        :raises BufferOverflowError: If `pos` is specified and is less than 0 or
        greater than or equal to the buffer length. If `pos` is not specified
        and the current position is equal to the buffer length.

        :param pos: The position in the buffer, or None to use current position
        :type pos: int, optional
        :rtype: np.uint8
        """
        return self._get(self._su8, 1, pos)

    def get16(self, pos: int = None) -> np.uint16:
        """
        Get a single short (2 bytes) from the buffer.

        If `pos` is specified, return the short at index `pos` from the buffer.
        If `pos` is not specified, return the short at the current position and
        increment the current position by 2.

        :raises BufferOverflowError: If `pos` is specified and is less than 0 or
        greater than or equal to the buffer length. If `pos` is not specified
        and the current position is equal to the buffer length.

        :param pos: The position in the buffer, or None to use current position
        :type pos: int, optional
        :rtype: np.uint16
        """
        return self._get(self._su16, 2, pos)

    def get32(self, pos: int = None) -> np.uint32:
        """
        Get a single integer (4 bytes) from the buffer.

        If `pos` is specified, return the integer at index `pos` from the buffer.
        If `pos` is not specified, return the integer at the current position
        and increment the current position by 4.

        :raises BufferOverflowError: If `pos` is specified and is less than 0 or
        greater than or equal to the buffer length. If `pos` is not specified
        and the current position is equal to the buffer length.

        :param pos: The position in the buffer, or None to use current position
        :type pos: int, optional
        :rtype: np.uint32
        """
        return self._get(self._su32, 4, pos)

    def getf(self, pos: int = None) -> np.float32:
        """
        Get a single float (4 bytes) from the buffer.

        If `pos` is specified, return the float at index `pos` from the buffer.
        If `pos` is not specified, return the float at the current position and
        increment the current position by 4.

        :raises BufferOverflowError: If `pos` is specified and is less than 0 or
        greater than or equal to the buffer length. If `pos` is not specified
        and the current position is equal to the buffer length.

        :param pos: The position in the buffer, or None to use current position
        :type pos: int, optional
        :rtype: np.float32
        """
        return self._get(self._sf32, 4, pos)
