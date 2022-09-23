
from .memory import Buffer


class YAZError(RuntimeError):
    """
    A YAZError occurs when trying to decompress invalid or corrupted YAZ data.
    """

    def __init__(self, *args):
        super().__init__(*args)


def decompress(data: Buffer) -> Buffer:
    """
    Decompress YAZ0 or YAZ1 data.

    :raises YAZError: If the data is not compressed using YAZ0 or YAZ1 or is
    corrupted.

    :param data: The YAZ data to decompress.
    :type data: Buffer
    :rtype: Buffer
    """
