# Mandelbrot Backend

This project provides a way to generate Mandelbrot images, numbers, canvas, and colors for the Mandelbrot set.

## Installation
Currently, the project is set up to use devcontainers. Simply use the `.devcontainer` folder. The devcontainer installs the following dependencies: `fastapi`, `uvicorn`, `numpy`, `black`, `pillow` (optional for canvas generation), and `h5py`.

## Usage
The primary usage is through `main.py`, which starts a REST API. The following backends are available:
(NOT FINISHED)

## Code Structure 
The codebase is organized into the following folders:

`src`: 
Contains the core logic for generating and manipulating Mandelbrot sets.
- `mandelbrot.py`: Implements the Mandelbrot class for generating Mandelbrot data.
- `schemas.py`: Defines the data structures used for Mandelbrot data and requests.
- `h5_cache.py` (Optional): Implements a class for caching Mandelbrot data in HDF5 files.

`main.py` (Optional): Provides a basic FastAPI server for serving the Mandelbrot generation functionality as a web service.

There are two main ways to use the codebase:

1. Using the Mandelbrot class without serving the API:
`python
from src.mandelbrot import Mandelbrot
from src.schemas import MandelLineSpaceSchema

# Define the x and y lines for the complex plane
x_line = np.linspace(-2.5, 2.5, 100)
y_line = np.linspace(-1.25, 1.25, 50)

# Create a Mandelbrot data object
mandelbrot_data = Mandelbrot().mandel_data_from_lines(
    MandelLineSpaceSchema(x_line=x_line, y_line=y_line)
)

# Access the generated data
count_grid = mandelbrot_data.count_grid
color_data = mandelbrot_data.color_data
`
2. Serving through the FastAPI server:
`
import requests

# Sample Mandelbrot request data
data = {
    "size": {"x": 200, "y": 200},
    "zoom_level": 1.0,
    "pixel_per_point": 1,
    "central_point": {"x": 0.0, "y": 0.0},
    "max_iter": 255,
    "iteration_limit": 2,
}

response = requests.post("http://localhost:8000/get_mandelbrot", json=data)
response_data = response.json()

# Access the generated data
count_grid = response_data["count_grid"]
color_data = response_data["color"]
`