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
    max_iter: int
    iteration_limit: int
    max_iter: Optional[int] = None
    iteration_limit: Optional[int] = None