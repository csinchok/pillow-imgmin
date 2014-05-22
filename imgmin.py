#!/usr/bin/env python

import os
import sys
import itertools
import tempfile
from PIL import Image

MAX_ERROR = 3.5
QUALITY_RANGE = (60, 95)
TARGET_WIDTH = 1000


def get_color_density(im):
    area = im.size[0] * im.size[1]
    unique_colors = len(filter(None, im.histogram()))
    return unique_colors / area


def get_error(a, b):
    assert a.size == b.size
    difference = 0
    for color_sets in itertools.izip(a.getdata(), b.getdata()):
        distance = 0
        for color_pair in zip(color_sets[0], color_sets[1]):
            distance += ((color_pair[0] - color_pair[1]) ** 2)
        difference += (distance ** 0.5)

    pixel_error = difference / float(b.size[0] * b.size[1])
    return pixel_error


def prepare_image(im):
    area = im.size[0] * im.size[1]
    if area > (1000 * 1000):
        scale = area / (1000.0 * 1000.0)
        new_size = (im.size[0] * scale, im.size[1] * scale)
        im = im.resize(map(int, new_size), Image.ANTIALIAS)
    if im.mode != "RGB":
        im = im.convert("RGB", palette=Image.ADAPTIVE)
    return im


def main():
    if len(sys.argv) == 1:
        print("Usage:")
        print("    > imgmin.py <file_name>")
        exit(1)

    filepath = sys.argv[1]

    im = Image.open(filepath)
    search_im = prepare_image(im)
    original_density = get_color_density(search_im)
    icc_profile = im.info.get("icc_profile")

    search_range = QUALITY_RANGE
    while (search_range[1] - search_range[0]) > 1:
        quality = int(round(search_range[0] + (search_range[1] - search_range[0]) / 2.0))
        print("Searching: {}".format(quality))

        handler, output_filepath = tempfile.mkstemp()
        search_im.save(output_filepath, "jpeg", quality=quality, icc_profile=icc_profile)
        saved = Image.open(output_filepath)

        pixel_error = get_error(saved, search_im)

        if pixel_error > MAX_ERROR or get_color_density(saved) > original_density:
            search_range = (quality, search_range[1])
        else:
            search_range = (search_range[0], quality)
        os.remove(output_filepath)

    quality = search_range[1]
    output_filepath = "{}.optim.jpg".format(filepath)
    im.save(output_filepath, "jpeg", quality=quality, icc_profile=icc_profile, optimize=True)
    output_filepath = "{}.origin.jpg".format(filepath)
    im.save(output_filepath, "jpeg", quality="keep", icc_profile=icc_profile)
    print("Optimal quality: {}, error: {}".format(quality, pixel_error))


if __name__ == "__main__":
    main()
