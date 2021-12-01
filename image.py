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
        for j in range(int(2 * unit * i + 1)):
            
            # this is the source x coordinate we want to get the color of.
            # we calculate this by:
            # - dividing the width of the image by 2*i units (so that we have 2*i evenly sized regions to pull from)
            # - multiplying that by j so that we get the j-th region
            # - subtracting one from the whole thing because of off-by-one errors
            sx = int(w / (i * 2 * unit + 1) * j - 1)

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
        # for j in range(int(2 * unit * i)):
        for j in range(source.width):
            
            # this is the source x coordinate we want to get the color of.
            # we calculate this by:
            # - dividing the width of the image by 2*i units (so that we have 2*i evenly sized regions to pull from)
            # - multiplying that by j so that we get the j-th region
            # - subtracting one from the whole thing because of off-by-one errors
            region_num = j * (2 * i * unit) // w
            sx = int(w / (i * 2 * unit + 1) * j)

            # finally fill in the pixel.
            dest.putpixel(
                (j, i),
                source.getpixel((start + region_num, i))
            )

    return dest

    # dest = Image.new("RGBA", source.size, (0, 0, 0, 0))

    # w, h = source.size

    # # this divides the width of the image into a number of sections equal to two times the height in pixels.
    # # each row has two more of these units than the last, one on each side.
    # unit = w / (2*h)

    # # iterate over each row of the image.
    # for i in range(source.height):
    #     
    #     # we start filling in pixels at i units to the left of center.
    #     start = w / 2 - unit * i

    #     # the number of "regions" we have
    #     num_regions = 2 * (i + 1)

    #     # divide the width of the image by 2*i units (so that we have 2*i evenly sized regions to pull from)
    #     region_width = w / num_regions

    #     # iterate over each pixel to fill, which will be the 2*i units of pixels.
    #     # for j in range(int(2 * unit * i)):
    #     for j in range(num_regions):
    #         
    #         # this is the source x coordinate we want to get the color of.
    #         region_start = region_width * j - 1

    #         sx = int(w / (j * 2 * unit + 1) * j - 1)

    #         color = source.getpixel((sx, i))

    #         for k in range(int(region_width)):
    #             # finally fill in the pixel.
    #             try:
    #                 dest.putpixel(
    #                     (int(region_width + k), i),
    #                     color
    #                 )
    #             except IndexError:
    #                 print("IndexError!")
    #                 print(f"h={h}, w={w}, i={i}, j={j}, k={k}")
    #                 print(f"num_regions={num_regions}, region_width={region_width}")
    #                 print(f"region_start={region_start}, color={color}")
    #                 return

    # return dest


if __name__ == '__main__':
    commands = { "t": trungify, "d": detrungify }

    funct = commands[argv[1]]
    source = Image.open(argv[2])
    output = funct(source)
    output.save(f"out_{argv[1]}.png")
