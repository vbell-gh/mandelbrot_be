import os

import numpy as np
from PIL import Image

from src.schemas import MandelData, MandelRequestSchema
from src.h5_cache import H5Cache


class MandelImage:
    def __init__(self):
        pass

    def generate_img(self, mdl_data: MandelData):
        red = mdl_data.color_data["red"]
        green = mdl_data.color_data["green"]
        blue = mdl_data.color_data["blue"]
        color_stack = np.stack([red, green, blue], axis=2)
        img = Image.fromarray(color_stack.astype("uint8"))
        return img

    def generage_imgs_cache(self):
        cache = H5Cache()
        for key in cache.keys:
            mdl_data = cache.read_cache(key)
            img = self.generate_img(mdl_data)
            img.save(f"images/{key}.png")
            print(f"Saved image {key}.png")
        print("All images saved.")
