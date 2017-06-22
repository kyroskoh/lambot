#!/usr/bin/env python
import os
import io
import boto3
from PIL import Image, ImageDraw
import colorsys
from pprint import pprint


class Fractal(object):
    def __init__(self, width, height, iterations):
        self.width = width
        self.height = height
        self.iterations = iterations
        self.monochrome = False

        self.filename = '{}x{}_{}.png'.format(width, height, iterations)
        print(self.filename)

        self.url = None

        self.image = Image.new("RGB", (width, height))
        self.draw = ImageDraw.Draw(self.image)

        self.s3 = boto3.client('s3')

        self.palette = self.make_palette()
        pprint(self.palette)


    def make_palette(self):
        palette = []
        for i in range(self.iterations):
            h, s, v = i / 256.0, 1, i / (i + 8.0)
            r, g, b = colorsys.hsv_to_rgb(h,s,v)
            palette.append((int(r * 255), int(g * 255), int(b * 255)))
        return palette


class Mandelbrot(Fractal):
    def __init__(self, width, height, iterations):
        super(Mandelbrot, self).__init__(width, height, iterations)

    def __repr__(self):
        return 'Mandelbrot({}, {}, ({}))'.format(self.width, self.height, self.iterations)

    def putpixel(self, col, row, color):
        self.draw.point((col, row), fill = color)
        return True

    def get_color(self, index):
        if self.monochrome:
            if index < self.iterations:
                return (255, 255, 255)
            else:
                return (0, 0, 0)
        else:
            return self.palette[index]

    def render(self):
        print('rendering...')
        for row in range(self.height):
            for col in range(self.width):
                # print(col, row)

                c_re = (col - self.width / 2.0) * 4.0 / self.width
                c_im = (row - self.height / 2.0) * 4.0 / self.width
                x = 0
                y = 0

                iteration = 0

                while (x * x + y * y) <= 4 and iteration < self.iterations:
                    x_new = x * x - y * y + c_re
                    y = 2 * x * y + c_im
                    x = x_new
                    iteration += 1

                self.putpixel(col, row, self.get_color(iteration - 1))
        return self

    def show(self):
        self.image.show()
        return self

    def bytesio(self):
        image_bytes = io.BytesIO()
        self.image.save(image_bytes, 'PNG')
        image_bytes.seek(0)
        return image_bytes

    def upload(self):
        print('uploading...')
        self.s3.put_object(Bucket='lambot-fractals', Key=self.filename, Body=self.bytesio())
        self.url = 'https://s3.amazonaws.com/lambot-fractals/{}'.format(self.filename)
        return self







#------------------------------------------------#
#  Command line options                          #
#------------------------------------------------#

def run():
    this_fractal = Mandelbrot(600, 400, 500)
    this_fractal.render().upload()

    print(this_fractal.url)



if __name__ == '__main__':
    run()
