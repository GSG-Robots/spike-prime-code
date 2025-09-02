import io

class RingIO:
    def __init__(self, initial_bytes: b""):
        self._buffer = bytearray(initial_bytes)

    def write(self, data: bytes):
        self._buffer.extend(data)

    def read(self, n: int):
        a = self._buffer[:n]
        self._buffer = self._buffer[n:]
        return a