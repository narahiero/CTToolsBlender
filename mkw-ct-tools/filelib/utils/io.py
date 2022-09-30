
from ..memory import Buffer


def read_file(path) -> Buffer:
    """
    Read the contents of the file at the specified path and store it in a Buffer.
    """
    with open(path, 'rb') as file:
        data = file.read()
        buf = Buffer(size=len(data))
        for i in range(len(data)):
            buf.data[i] = data[i]
        return buf

def write_file(path, buf: Buffer):
    """
    Write the contents of the buffer to a file at the specified path.
    """
    with open(path, 'wb') as file:
        file.write(buf.data[buf.pos:buf.limit])
    buf.pos = buf.limit
