from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import timeit

from src.schemas import MandelRequestSchema
from src.mandelbrot import Mandelbrot


app = FastAPI(
    title="Mandelbrot API",
    summary="API to generate Mandelbrot set made to work with the mandelsite frontend.",
    version="0.1",  # Most probably the only version
)
origins = ["http://localhost:9000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    """
    Test if the API is working.
    """
    return {"Test": "Working!"}


@app.get("/test_arr")
def test_arr():
    """
    Get a sample array to test the API. 10x10 array with a description.
    """
    return {
        "sample": [
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
            [0, 0, 0, 1, 1, 1, 1, 1, 0, 0],
            [0, 0, 1, 2, 3, 200, 1, 1, 1, 0],
            [0, 0, 2, 4, 200, 200, 4, 1, 1, 0],
            [0, 200, 200, 200, 200, 200, 4, 2, 1, 1],
            [0, 0, 2, 4, 200, 200, 4, 1, 1, 0],
            [0, 0, 1, 2, 3, 200, 1, 1, 1, 0],
            [0, 0, 0, 1, 1, 1, 1, 1, 0, 0],
            [0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
        ],
        "description": "This is a sample array to test the API.",
    }


@app.post("/get_mandelbrot")
def get_mandelbrot(request_data: MandelRequestSchema):
    """
    Get the Mandelbrot set data for the given request data.

    - **size**: List of two integers representing the x and y size of the image.
    - **zoom_level**: Float representing the zoom level of the image.
    - **pixel_per_point**: Integer representing the number of pixels per point.
    - **central_point**: List of two floats representing the x and y coordinates of the central point of the image.
    - **max_iter**: Integer representing the maximum number of iterations. Default is 255.
    - **iteration_limit**: Integer representing the iteration limit. Default is 2.
    - **is_canvas**: Boolean indicating if the request is for a canvas. Default is False.

    Returns a dictionary with the following keys:
    - **count_grid**: A 2D array representing the count grid.
    - **complex_grid**: A dictionary with keys 'x_line' and 'y_line', each containing a list of floats for which the set was generated.
    - **color**: A list of colors if is_canvat is set to true, dictionary of red, green and blue if set to false.

    """

    try:
        mdlbrt = Mandelbrot()
        count_grid, x_line, y_line, color_data = mdlbrt.main_loop(request_data)
        count_grid_list = count_grid.tolist()
        complex_grid = {
            "x_line": x_line.tolist(),
            "y_line": y_line.tolist(),
        }
        return {
            "count_grid": count_grid_list,
            "complex_grid": complex_grid,
            "color": color_data,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
