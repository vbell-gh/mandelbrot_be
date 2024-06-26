from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import timeit

from src.schemas import MandelRequestSchema
from src.mandelbrot import Mandelbrot


app = FastAPI()
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
    return {"Hello": "World"}


@app.get("/test_arr")
def test_arr():
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
        ]
    }


@app.post("/get_mandelbrot")
def get_mandelbrot(request_data: MandelRequestSchema):
    start_time = timeit.default_timer()

    try:
        mdlbrt = Mandelbrot()
        count_grid, x_line, y_line, color_data = mdlbrt.main_loop(request_data)
        count_grid_list = count_grid.tolist()
        complex_grid = {
            "x_line": x_line.tolist(),
            "y_line": y_line.tolist(),
        }
        end_time = timeit.default_timer()
        print(f"Time taken: {end_time - start_time}")
        return {
            "count_grid": count_grid_list,
            "complex_grid": complex_grid,
            "color": color_data,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
