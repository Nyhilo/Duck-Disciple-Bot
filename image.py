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

    # this divides the width of the image into a number of sections equal to two times the height in pixels.
    # each row has two more of these units than the last, one on each side.
    unit = w / (2*h)

    # iterate over each row of the image.
    for i in range(source.height):
        
        # we start filling in pixels at i units to the left of center.
        start = w / 2 - unit * i

        # iterate over each pixel to fill, which will be the 2*i units of pixels.
        for j in range(int(2 * unit * i)):
            
            # this is the source x coordinate we want to get the color of.
            # we calculate this by:
            # - dividing the width of the image by 2*i units (so that we have 2*i evenly sized regions to pull from)
            # - multiplying that by j so that we get the j-th region
            # - subtracting one from the whole thing because of off-by-one errors
            sx = int(w / (i * 2 * unit) * j - 1)

            # finally fill in the pixel.
            dest.putpixel(
                (int(start + j), i),
                source.getpixel((sx, i))
            )

    return dest


def trungify_and_save(url, destination):
    source = get_image(url)
    output = trungify(source)
    output.save(destination)


def detrungify(source):
    pass


if __name__ == '__main__':
    source = Image.open(argv[1])
    output = trungify(source)
    output.save("out.png")
