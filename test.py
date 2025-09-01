import io

a = io.BytesIO()

a.write(b"hi")

print(a.read())