
class YazError(RuntimeError):
    """
    A YazError occurs when trying to decompress invalid or corrupted Yaz data.
    """

    def __init__(self, *args):
        super().__init__(*args)
