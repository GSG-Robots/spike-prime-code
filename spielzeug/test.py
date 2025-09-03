from micropython import RingIO

a = RingIO(100)

a.write(b"hi")
print(a.readline())
a.write(b"hi\n")
a.write(b"hi")
print(a.readline())
a.write(b"hi\n")
print(a.readline())
