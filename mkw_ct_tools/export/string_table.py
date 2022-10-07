

class StringTable:

    def __init__(self):
        self._strings = dict()
        self._len = 0

    def __getitem__(self, string: str) -> int:
        """
        Add the string to the table if not already present and return the index.
        """
        if string not in self._strings:
            # self._strings.append(string)
            self._strings[string] = self._len
            prev_len = self._len
            self._len += len(string) + 1
            return prev_len

        return self._strings[string]

    @property
    def strings(self) -> dict:
        return self._strings

    @property
    def total_len(self) -> int:
        return self._len
