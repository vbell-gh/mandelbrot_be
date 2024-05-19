from pydantic import BaseModel
from typing import Optional


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
    max_iter: int = 200
    iteration_limit: int = 2
    is_canvas: Optional[bool] = False
    is_image: Optional[bool] = True
