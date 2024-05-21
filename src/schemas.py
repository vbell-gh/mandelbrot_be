from pydantic import BaseModel
from typing import Optional, Any
import numpy as np


class XYpointInt(BaseModel):
    x: int
    y: int


class XYpointFloat(BaseModel):
    x: float
    y: float


class MandelSchema(BaseModel):
    size: XYpointInt
    zoom_level: float
    pixel_per_point: int
    central_point: XYpointFloat
    max_iter: int = 255
    iteration_limit: int = 2
    is_canvas: Optional[bool] = False
    is_image: Optional[bool] = True


class MandelData(BaseModel):
    count_grid: Any
    x_line: Any
    y_line: Any
    color_data: Any
    level: str

    @property
    def level(self):
        return str(self.level)
