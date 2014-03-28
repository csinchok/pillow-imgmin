#!/usr/bin/env python

import os
import sys
import itertools
import tempfile
from PIL import Image

MAX_ERROR = 9.0
QUALITY_RANGE = (40, 96)


def main():
    if len(sys.argv) == 1:
        print("Usage:")
        print("    > imgmin.py <file_name>")
        exit(1)

    filepath = sys.argv[1]

    im = Image.open(filepath)
    icc_profile = im.info.get("icc_profile")

    search_range = QUALITY_RANGE
    while (search_range[1] - search_range[0]) > 1:
        quality = int(round(search_range[0] + (search_range[1] - search_range[0]) / 2.0))
        print("Searching: {}".format(quality))

        handler, output_filepath = tempfile.mkstemp()
        im.save(output_filepath, "jpeg", quality=quality, icc_profile=icc_profile)
        saved = Image.open(output_filepath)

        saved = Image.open(output_filepath)
        difference = 0
        for color_sets in itertools.izip(saved.getdata(), im.getdata()):
            for color_pair in zip(color_sets[0], color_sets[1]):
                difference += abs(color_pair[0] - color_pair[1])

        pixel_error = difference / float(len(im.getdata()))

        if pixel_error > MAX_ERROR:
            search_range = (quality, search_range[1])
        else:
            search_range = (search_range[0], quality)
        os.remove(output_filepath)

    output_filepath = "{}.optim.jpg".format(filepath)
    im.save(output_filepath, "jpeg", quality=quality, icc_profile=icc_profile)
    print("Optimal quality: {}, error: {}".format(quality, pixel_error))


if __name__ == "__main__":
    main()
