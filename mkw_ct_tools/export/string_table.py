

class StringTable:

    def __init__(self):
        self._strings = dict()
        self._len = 0

    def __getitem__(self, key):
        """
        If `key` is of type `str`, add the string to the table if not already
        present and return the index.

        If `key` is of type `int`, return the string at the index in the table.
        """
        if type(key) is str:
            if key not in self._strings:
                self._strings[key] = self._len
                prev_len = self._len
                self._len += len(key) + 1
                return prev_len

            return self._strings[key]

        elif type(key) is int:
            for string in self._strings:
                if self._strings[string] == key:
                    return string

    @property
    def strings(self) -> dict:
        return self._strings

    @property
    def total_len(self) -> int:
        return self._len
