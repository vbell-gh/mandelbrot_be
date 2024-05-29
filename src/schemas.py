from pydantic import BaseModel, Field
from typing import Optional, Any


class XYpointInt(BaseModel):
    x: int = Field(example=100)
    y: int = Field(example=100)


class XYpointFloat(BaseModel):
    x: float = 0.0
    y: float = 0.0


class MandelRequestSchema(BaseModel):
    size: XYpointInt
    zoom_level: float = 1
    pixel_per_point: int = 1
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
    level: str = 'na' # z_x_y where z is the zoom level and x and y are the coordinates of the block


