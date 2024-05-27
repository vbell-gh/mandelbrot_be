import numpy as np
from PIL import Image
from src.schemas import MandelData, MandelRequestSchema

class MandelImage:
    def __init__(self):
        pass
    
    def generate_image_request(self, mdl_data: MandelRequestSchema):
        _, _, _, color_data = self.main_loop(mdl_data)
        red = color_data["red"]
        green = color_data["green"]
        blue = color_data["blue"]
        color_stack = np.stack([red, green, blue], axis=2)
        img = Image.fromarray(color_stack.astype("uint8"))
        return img