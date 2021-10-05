from sys import argv
from PIL import Image
import requests
from io import BytesIO


def get_image(url):
    '''https://stackoverflow.com/a/49092583'''
    response = requests.get(url)
    return Image.open(BytesIO(response.content))


def trungify(source):
    dest = Image.new("RGBA", source.size, (0, 0, 0, 0))

    w, h = source.size
    unit = w / (2*h)
    for i in range(source.height):
        start = w / 2 - unit * i
        for j in range(int(2 * unit * i)):
            dest.putpixel(
                (int(start + j), i),
                source.getpixel((int(w / (i * 2 * unit + 1) * j - 1), i))
            )

    return dest


def trungify_and_save(url, destination):
    source = get_image(url)
    output = trungify(source)
    output.save(destination)


if __name__ == '__main__':
    source = Image.open(argv[1])
    output = trungify(source)
    output.save("out.png")
