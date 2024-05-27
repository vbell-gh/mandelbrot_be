from pydantic import BaseModel
from typing import Optional, Any


class XYpointInt(BaseModel):
    x: int
    y: int


class XYpointFloat(BaseModel):
    x: float
    y: float


class MandelRequestSchema(BaseModel):
    size: XYpointInt
    zoom_level: float
    pixel_per_point: int
    central_point: XYpointFloat
    max_iter: int = 255
    iteration_limit: int = 2
    is_canvas: Optional[bool] = False # if sent to true the color is returned in canvas format

class MandelLineSpaceSchema(BaseModel):
    x_line: Any
    y_line: Any
    max_iter: int = 255
    iteration_limit: int = 2

class MandelData(BaseModel):
    count_grid: Any
    x_line: Any
    y_line: Any
    color_data: Any
    level: str = 'na'


