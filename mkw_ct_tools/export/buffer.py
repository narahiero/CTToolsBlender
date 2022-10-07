
from struct import Struct

from mathutils import Vector


V3F_ORDER = [0, -2, 1]
"""The order used by Mario Kart Wii for position and rotation."""

V3F_SCALE_ORDER = [0, 2, 1]
"""The order used by Mario Kart Wii for scale."""


class BufferOverflowError(RuntimeError):
    """
    A BufferOverflowError occurs when attempting to access or modify data
    outside of the `Buffer`'s memory block.
    """

    def __init__(self, *args):
        super().__init__(*args)


class Buffer:
    """
    The Buffer class is a memory manipulation utility that read and write data
    from and to a contiguous sequence of bytes. It is similar to Java's
    `java.nio.ByteBuffer`.

    Each buffer has a data array and a set of properties. The length is the
    length of the data, the position is an offset in the data, and the limit is
    an artificial upper bound to the data. The limit is always less than or
    equal to the length, and the position is always less than or equal to the
    limit. A negative value is converted into a positive value the same way as
    Python's slice notation, the limit starting from the length and the position
    starting from the limit. Should the limit be set to a value less than the
    position, the position will also be set to the new limit.

    Each buffer also has multiple functionalities. There are the functions which
    alter the state of the buffer, some which read or write from or to the data,
    and others which creates buffers.

    First are the functions altering the buffer state. The `flip` function sets
    the limit to the current position, then moves the position back to 0, the
    start of the buffer. The `clear` function simply resets the position to 0
    and the limit to the length.

    Second are the I/O functions. The `get` functions read data from the buffer
    while the `put` functions write data to the buffer. Both aforementioned
    functions have multiple 'flavors', a suffix indicating the type and size of
    data to use. Some examples are `~8` which represents an 8-bit (1 byte)
    unsigned integer and `~f` which stands for a 32-bit (4 bytes) floating point
    number. These functions also have as an optional argument an absolute index
    into the buffer. Should that argument be provided, the function will operate
    at said position, and the buffer state will remain unchanged. On the other
    hand, if it is omitted, the function will operate at the buffer's current
    position, and the position will be incremented by the size of the data,
    effectively 'consuming' it.

    Lastly are the functions for constructing buffers. There is the constructor
    as well as the `copy` and `slice` functions. The constructor can create
    either an empty buffer or a buffer initialized with the contents of another,
    while the `copy` and `slice` functions only do the latter. When constructing
    a buffer from another, the data can be either shared or copied. Shared means
    both the source and new buffer will use the same data array under the hood,
    meaning any modifications to the data by one will be reflected in the other.
    Copied simply means the new buffer will get its own data array initialized
    with the contents of the source. Both the constructor and the `slice`
    function can make subsets of the source's data.

    In addition to the functions above, the Buffer class implements the
    subscript operator. Given a single index, the operator acts like the
    absolute index version of the I/O single byte (`~8`) functions. With a slice
    notation, the operator acts like the `slice` function to create a subset
    buffer with shared data. The step of the slice notation is not supported.

    To ensure all operations occur within the bounds of the data, errors of type
    `BufferOverflowError` are raised when trying to access outside of the
    buffer's range. This includes attempting to set the position to a value
    greater than the limit, to create a subset exceeding the bounds of the
    source, and to read or write data of size greater than the remaining data in
    the buffer.

    ============================================================================

    From here on is the documentation for the constructor.

    The data of the constructed buffer can either be empty (all zeros) or
    initialized from another source buffer (`src`).

    When no source is given, `size` must be specified. This will be the length,
    in bytes, of the data array of new buffer. It must be greater than or equal
    to 0. All other arguments will be ignored.

    When a source is provided, the data can either be shared or copied. This is
    controlled by the argument `copy` and defaults to `False` (shared). When the
    data is shared, the new buffer will share the same data array as the source,
    meaning any modifications to one's data will be reflected on the other's.
    When the data is copied, the new buffer will have its own data array
    initialized with the contents of the source's.

    The last two arguments are the offset (`off`) and the length (`size`). The
    data of the new buffer will be a subset of the source's data, starting from
    the offset and of the specified length. If the offset is `None` (the
    default), the position of the source buffer is used. Negative values are
    allowed for the offset, in which case it will be calculated by subtracting
    from the source's limit. The absolute value of the offset must be less than
    or equal to the source's limit. If the length is `None` (also the default),
    the difference between the source's limit and the offset will be used. The
    length must be greater than or equal to zero, and the sum of the offset and
    the length must be less than or equal to the source's limit.
    """

    def __init__(self, *, src = None, copy = False, off: int = None, size: int = None):
        if src is None:
            if size is None:
                raise TypeError(f"at least one of the following arguments must be provided: 'src', 'size'")
            if size < 0:
                raise ValueError(f"size must be >= 0; {size=}")

            self._array = bytearray(size)
            self._data = memoryview(self._array)

        else:
            if off is None:
                off = src.pos
            elif abs(off) > src.limit:
                raise BufferOverflowError(f"abs(off) must be <= src limit; {abs(off)=}, {src.limit=}")
            elif off < 0:
                off = src.limit + off  # negative so effectively a subtraction

            if size is None:
                size = src.limit - off
            elif size < 0:
                raise ValueError(f"size must be >= 0; {size=}")

            if off + size > src.limit:
                raise BufferOverflowError(f"off + size must be <= src limit; {off+size=}, {src.limit=}")

            if copy:
                self._array = bytearray(src._array)

            self._data = src._data[off:off+size]
            if copy:
                self._array = bytearray(self._data)
                self._data = memoryview(self._array)

        self._pos = 0
        self._limit = len(self)

        self._su8 = Struct('>B')
        self._su16 = Struct('>H')
        self._su32 = Struct('>I')
        self._sf32 = Struct('>f')

    def __len__(self):
        return len(self._data)

    @property
    def data(self) -> bytearray:
        """
        The backend data array, a `bytearray`. Note that this is not a copy, so
        any modifications made to this array will be reflected in the buffer.
        """
        return self._data

    @property
    def limit(self) -> int:
        """
        The upper bound to the data. Any operation attempting to access data
        beyond the limit will result in a `BufferOverflowError`.

        If the limit is set to a value less than the position, the position will
        be set to the new limit.

        If the limit is set to a negative value, it will be recalculated like
        slice notation, the length of the buffer minus absolute value of the new
        limit.

        If the absolute value of the new limit is greater than the length, a
        `BufferOverflowError` will be raised.
        """
        return self._limit

    @limit.setter
    def limit(self, limit: int):
        if abs(limit) > len(self):
            raise BufferOverflowError(f"abs(limit) must be <= the length; {abs(limit)=}, {len(self)=}")

        self._limit = limit if limit >= 0 else len(self) + limit

        if self._limit < self._pos:
            self._pos = self._limit

    @property
    def pos(self) -> int:
        """
        The offset in the data used by relative operations.

        If the position is set to a negative value, it will be recalculated like
        slice notation, the limit minus absolute value of the new position.

        If the absolute value of the new position is greater than the limit, a
        `BufferOverflowError` will be raised.
        """
        return self._pos

    @pos.setter
    def pos(self, pos: int):
        if abs(pos) > self._limit:
            raise BufferOverflowError(f"abs(pos) must be <= the limit; {abs(pos)=}, {self.limit=}")

        self._pos = pos if pos >= 0 else self._limit + pos

    @property
    def remaining(self) -> int:
        """
        The amount of remaining bytes in the buffer, or the limit of this buffer
        minus the current position.
        """
        return self._limit - self._pos

    def clear(self):
        """
        Set the position to 0 and the limit to the length. Note that this method
        doesn't clear the actual data from the buffer.
        """
        self._pos = 0
        self._limit = len(self)

        return self

    def flip(self):
        """
        Set the limit to the current position, then set the position to 0. This
        is usually called after writing data to prepare the buffer to be read.
        """
        self._limit = self._pos
        self._pos = 0

        return self

    def slice(self, *, copy = False, off: int = None, size: int = None):
        """
        Create a subset of this buffer.

        This is a shortcut for the constructor and is equivalent to the
        following:

        ```
            buf.slice(copy=c, off=o, size=s)  # is equivalent to
            Buffer(src=buf, copy=c, off=o, size=s)
        ```
        """
        return Buffer(src=self, copy=copy, off=off, size=size)

    def copy(self, *, off: int = None, size: int = None):
        """
        Create a copy of this buffer.

        This is a shortcut for the constructor and is equivalent to the
        following:

        ```
            buf.copy(off=o, size=s)  # is equivalent to
            Buffer(src=buf, copy=True, off=o, size=s)
        ```
        """
        return Buffer(src=self, copy=True, off=off, size=size)

    def _put(self, strct, size, data, pos):
        if pos is None:
            self._checkEnoughRemaining(size, True)

            strct.pack_into(self._data, self._pos, data)
            self._pos += size

        else:
            pos = self._calcAbsolutePosAndCheck(pos, size, True)

            strct.pack_into(self._data, pos, data)

        return self

    def put8(self, data, *, pos: int = None):
        """
        Put a single byte in the buffer at the current position and increment
        the position by 1. If there is less than 1 byte remaining in the buffer,
        a `BufferOverflowError` is raised.

        If the optional argument `pos` is provided, then that value is used as
        the position and the buffer's position is left unchanged. If `pos` is a
        negative value, it will be recalculated like slice notation, the limit
        minus the absolute value of `pos`. If the absolute value of `pos` is
        greater than the limit, or `pos` plus 1 is greater than the limit, a
        `BufferOverflowError` is raised.
        """
        return self._put(self._su8, 1, data, pos)

    def put16(self, data, pos: int = None):
        """
        Put a single short (2 bytes) in the buffer at the current position and
        increment the position by 2. If there are less than 2 bytes remaining in
        the buffer, a `BufferOverflowError` is raised.

        If the optional argument `pos` is provided, then that value is used as
        the position and the buffer's position is left unchanged. If `pos` is a
        negative value, it will be recalculated like slice notation, the limit
        minus the absolute value of `pos`. If the absolute value of `pos` is
        greater than the limit, `pos` plus 2 is greater than the limit, or `pos`
        is less than 0 and greater than -2, a `BufferOverflowError` is raised.
        """
        return self._put(self._su16, 2, data, pos)

    def put32(self, data, pos: int = None):
        """
        Put a single integer (4 bytes) in the buffer at the current position and
        increment the position by 4. If there are less than 4 bytes remaining in
        the buffer, a `BufferOverflowError` is raised.

        If the optional argument `pos` is provided, then that value is used as
        the position and the buffer's position is left unchanged. If `pos` is a
        negative value, it will be recalculated like slice notation, the limit
        minus the absolute value of `pos`. If the absolute value of `pos` is
        greater than the limit, `pos` plus 4 is greater than the limit, or `pos`
        is less than 0 and greater than -4, a `BufferOverflowError` is raised.
        """
        return self._put(self._su32, 4, data, pos)

    def putf(self, data, pos: int = None):
        """
        Put a single float (4 bytes) in the buffer at the current position and
        increment the position by 4. If there are less than 4 bytes remaining in
        the buffer, a `BufferOverflowError` is raised.

        If the optional argument `pos` is provided, then that value is used as
        the position and the buffer's position is left unchanged. If `pos` is a
        negative value, it will be recalculated like slice notation, the limit
        minus the absolute value of `pos`. If the absolute value of `pos` is
        greater than the limit, `pos` plus 4 is greater than the limit, or `pos`
        is less than 0 and greater than -4, a `BufferOverflowError` is raised.
        """
        return self._put(self._sf32, 4, data, pos)

    def puta(self, data, pos: int = None):
        """
        Put an array of bytes in the buffer at the current position and
        increment the position by the length of the array. The data can be of
        any type as long as it is subscriptable by index, its length can be
        queried, and the returned values are integers between 0 and 255. If
        there are less bytes remaining in the buffer than the length of the
        array, a `BufferOverflowError` is raised.

        If the optional argument `pos` is provided, then that value is used as
        the position and the buffer's position is left unchanged. If `pos` is a
        negative value, it will be recalculated like slice notation, the limit
        minus the absolute value of `pos`. If the absolute value of `pos` is
        greater than the limit, `pos` plus the length of the array is greater
        than the limit, or `pos` is less than 0 and its absolute value is
        greater than the length of the array, a `BufferOverflowError` is raised.
        """
        if pos is None:
            self._checkEnoughRemaining(len(data), True)

            pos = self._pos
            self._pos += len(data)

        else:
            pos = self._calcAbsolutePosAndCheck(pos, len(data), True)

        for i in range(len(data)):
            self._data[pos+i] = data[i]

        return self

    def puts(self, data: str, nt = False, pos: int = None):
        """
        Put the `str` in the buffer at the current position and increment the
        position by the length of the string. The string will be converted to a
        sequence of ASCII codes using `encode('ascii')`. If `nt` is `True`, the
        null character '`\\0`' will be appended to the string, and the data
        length will thus be incremented by 1. If there are less bytes remaining
        in the buffer than the length of the data, a `BufferOverflowError` is
        raised.

        If the optional argument `pos` is provided, then that value is used as
        the position and the buffer's position is left unchanged. If `pos` is a
        negative value, it will be recalculated like slice notation, the limit
        minus the absolute value of `pos`. If the absolute value of `pos` is
        greater than the limit, `pos` plus the length of the data is greater
        than the limit, or `pos` is less than 0 and its absolute value is
        greater than the length of the data, a `BufferOverflowError` is raised.
        """
        if nt:
            data = data + '\0'

        return self.puta(data.encode('ascii'), pos=pos)

    def putv(self, data: Vector, order: list = None, pos: int = None):
        """
        Put a `Vector` of `float` in the buffer at the current position and
        increment the position 4 times the length of the vector. The optional
        `order` argument is a `list` with the indices of which and what order
        to write the components of the vector. If an index is negative, it will
        be used as a positive index and the component at that index will be
        negated. If there are less bytes remaining in the buffer than the length
        of the vector's data, a `BufferOverflowError` is raised. If any index in
        `order` is out of the range of the vector, an `IndexError` is raised.

        If the optional argument `pos` is provided, then that value is used as
        the position and the buffer's position is left unchanged. If `pos` is a
        negative value, it will be recalculated like slice notation, the limit
        minus the absolute value of `pos`. If the absolute value of `pos` is
        greater than the limit, `pos` plus the length of the data is greater
        than the limit, or `pos` is less than 0 and its absolute value is
        greater than the length of the data, a `BufferOverflowError` is raised.
        """
        if order is None:
            order = list(range(len(data)))

        idcs = list(order)
        scale = [1.] * len(idcs)
        for i in range(len(idcs)):
            if idcs[i] < 0:
                idcs[i] = abs(idcs[i])
                scale[i] = -1.
            if i >= len(data):
                raise IndexError(f"index out of vector range; {idcs[i]} >= {len(data)}")

        for idx in idcs:
            self.putf(data[idx]*scale[idx], pos=pos)
            if pos is not None:
                pos += 4

        return self

    def _get(self, strct, size, pos):
        if pos is None:
            self._checkEnoughRemaining(size, False)

            retval = strct.unpack_from(self._data, self._pos)[0]
            self._pos += size

            return retval

        else:
            pos = self._calcAbsolutePosAndCheck(pos, size, False)

            return strct.unpack_from(self._data, pos)[0]

    def get8(self, pos: int = None):
        """
        Get a single byte from the buffer from the current position and
        increment the position by 1. The there is less than 1 byte remaining in
        the buffer, a `BufferOverflowError` is raised.

        If the optional argument `pos` is provided, then that value is used as
        the position and the buffer's position is left unchanged. If `pos` is a
        negative value, it will be recalculated like slice notation, the limit
        minus the absolute value of `pos`. If the absolute value of `pos` is
        greater than the limit, or `pos` plus 1 is greater than the limit, a
        `BufferOverflowError` is raised.
        """
        return self._get(self._su8, 1, pos)

    def get16(self, pos: int = None):
        """
        Get a single short (2 bytes) from the buffer from the current position
        and increment the position by 2. The there are less than 2 bytes
        remaining in the buffer, a `BufferOverflowError` is raised.

        If the optional argument `pos` is provided, then that value is used as
        the position and the buffer's position is left unchanged. If `pos` is a
        negative value, it will be recalculated like slice notation, the limit
        minus the absolute value of `pos`. If the absolute value of `pos` is
        greater than the limit, `pos` plus 2 is greater than the limit, or `pos`
        is less than 0 and greater than -2, a `BufferOverflowError` is raised.
        """
        return self._get(self._su16, 2, pos)

    def get32(self, pos: int = None):
        """
        Get a single integer (4 bytes) from the buffer from the current position
        and increment the position by 4. The there are less than 4 bytes
        remaining in the buffer, a `BufferOverflowError` is raised.

        If the optional argument `pos` is provided, then that value is used as
        the position and the buffer's position is left unchanged. If `pos` is a
        negative value, it will be recalculated like slice notation, the limit
        minus the absolute value of `pos`. If the absolute value of `pos` is
        greater than the limit, `pos` plus 4 is greater than the limit, or `pos`
        is less than 0 and greater than -4, a `BufferOverflowError` is raised.
        """
        return self._get(self._su32, 4, pos)

    def getf(self, pos: int = None):
        """
        Get a single float (4 bytes) from the buffer from the current position
        and increment the position by 4. The there are less than 4 bytes
        remaining in the buffer, a `BufferOverflowError` is raised.

        If the optional argument `pos` is provided, then that value is used as
        the position and the buffer's position is left unchanged. If `pos` is a
        negative value, it will be recalculated like slice notation, the limit
        minus the absolute value of `pos`. If the absolute value of `pos` is
        greater than the limit, `pos` plus 4 is greater than the limit, or `pos`
        is less than 0 and greater than -4, a `BufferOverflowError` is raised.
        """
        return self._get(self._sf32, 4, pos)

    def geta(self, size: int = None, pos: int = None) -> bytearray:
        """
        Get get the next `size` bytes from the buffer at the current position
        and increment the position by `size`. If there are less than `size`
        bytes remaining in the buffer, a `BufferOverflowError` is raised.

        If `size` is not provided, then the difference between the limit and the
        position is used.

        If the optional argument `pos` is provided, then that value is used as
        the position and the buffer's position is left unchanged. If `pos` is a
        negative value, it will be recalculated like slice notation, the limit
        minus the absolute value of `pos`. If the absolute value of `pos` is
        greater than the limit, `pos` plus `size` is greater than the limit, or
        `pos` is less than 0 and its absolute value is greater than `size`, a
        `BufferOverflowError` is raised.
        """
        if pos is None:
            if size is None:
                size = self.remaining
            else:
                self._checkEnoughRemaining(size, False)

            pos = self._pos
            self._pos += size

        else:
            pos = self._calcAbsolutePosAndCheck(pos, size, False)
            if size is None:
                size = self._limit - pos

        return bytearray(self._data[pos:pos+size])

    def gets(self, size: int = None, nt = False, pos: int = None) -> str:
        """
        Get a string from the buffer at the current position and increment the
        position by the length of the string. The data is interpreted as a
        sequence of ASCII codes.

        If `size` is provided, the next `size` bytes are used to construct a
        string. If `nt` is True, an additional byte is read, and a `ValueError`
        is raised if it is not the null character '`\\0`'. The null character
        will not be appended to the returned string. If there are less bytes
        remaining in the buffer than the length of the string, a
        `BufferOverflowError` is raised.

        If `size` is not provided and `nt` is `True`, the string is constructed
        from the position until a null character is encountered. The null
        character will not be appended to the string. If no null character is
        found before reaching the end of the buffer, a `BufferOverflowError` is
        raised.

        If `size` is not provided and `nt` is `False`, then the string is
        constructed from the remaining data.

        If the optional argument `pos` is provided, then that value is used as
        the position and the buffer's position is left unchanged. If `pos` is a
        negative value, it will be recalculated like slice notation, the limit
        minus the absolute value of `pos`. If the absolute value of `pos` is
        greater than the limit, `pos` plus `size` is greater than the limit, or
        `pos` is less than 0 and its absolute value is greater than `size`, a
        `BufferOverflowError` is raised.
        """
        if nt:
            if size is None:
                if pos is None:
                    start = self._pos
                else:
                    start = self._calcAbsolutePosAndCheck(pos, None, False)

                end = start
                while True:
                    if end == self._limit:
                        raise BufferOverflowError("reached end of buffer before null character")

                    if self._data[end] == 0:
                        break

                    end += 1

                size = end - start + 1

            else:
                size += 1

                if pos is None:
                    self._checkEnoughRemaining(size, False)
                    start = self._pos
                else:
                    start = self._calcAbsolutePosAndCheck(pos, size, False)

                tail = self._data[start+size-1]
                if tail != 0:
                    raise ValueError(f"string does not end with a null character; got {tail:#x}")

        data = self.geta(size=size, pos=pos)
        if nt:
            data = data[:-1]

        return data.decode('ascii')

    def _checkEnoughRemaining(self, size, isinput):
        if self.remaining < size:
            act = "write" if isinput else "read"
            raise BufferOverflowError(f"not enough bytes left to {act} data; {self.remaining=} < {size}")

    def _calcAbsolutePosAndCheck(self, pos, size, isinput):
        if abs(pos) > self._limit:
            raise BufferOverflowError(f"abs(pos) must be <= the limit; {abs(pos)=}, {self.limit=}")
        if pos < 0:
            pos = self._limit + pos
        if size is not None and pos + size > self._limit:
            act = "write" if isinput else "read"
            raise BufferOverflowError(f"attempted to {act} past limit; pos ({pos}) + {size} > limit ({self._limit})")
        return pos
