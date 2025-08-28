def Image(img: str):
    return tuple(int(pixel) / 9 * 100 for pixel in img.replace(":", ""))
