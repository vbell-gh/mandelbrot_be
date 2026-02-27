import os

import numpy as np
from PIL import Image

from src.schemas import MandelData, MandelRequestSchema
from src.h5_cache import H5Cache


class MandelImage:
    def __init__(self):
        self.images_folder = "images"

    def generate_img(self, mdl_data: MandelData):
        red = mdl_data.color_data["red"]
        green = mdl_data.color_data["green"]
        blue = mdl_data.color_data["blue"]
        color_stack = np.stack([red, green, blue], axis=2)
        img = Image.fromarray(color_stack.astype("uint8"))
        return img

    def generage_img_cache(self):
        cache = H5Cache()
        print(cache.get_keys())
        for key in cache.get_keys():
            mdl_data = cache.read_cache(key)
            img = self.generate_img(mdl_data)
            image_save_path = os.path.join(
                cache.data_folder, self.images_folder, f"{key}.png"
            )
            img.save(image_save_path)
            print(f"Saved image {key}.png")
        print("All images saved.")
        

if __name__ == "__main__":
    mandel_image = MandelImage()
    mandel_image.generage_img_cache()
