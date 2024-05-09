from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from src.schemas import MandelSchema
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
            [128, 42, 85, 193, 11, 149, 70, 105, 183, 154],
            [176, 84, 48, 160, 39, 10, 53, 55, 83, 155],
            [27, 163, 155, 34, 42, 26, 109, 123, 39, 144],
            [50, 192, 61, 144, 189, 101, 84, 28, 123, 38],
            [59, 131, 142, 144, 119, 111, 38, 93, 72, 139],
            [144, 41, 68, 40, 16, 114, 87, 152, 36, 147],
            [71, 166, 120, 95, 19, 139, 16, 55, 140, 42],
            [179, 22, 144, 30, 112, 57, 97, 84, 45, 77],
            [9, 39, 184, 70, 122, 169, 29, 98, 36, 142],
            [67, 50, 60, 9, 11, 0, 102, 78, 176, 152],
        ],
    }


@app.post("/get_mandelbrot")
def get_mandelbrot(data: MandelSchema):
    try:
        mandebrot = Mandelbrot(
            size=data.size,
            zoom_level=data.zoom_level,
            pixels_per_point=data.pixel_per_point,
            central_point=data.central_point,
            max_iterations=data.max_iter,
            iteration_limit=data.iteration_limit,
        )
        data_set = mandebrot.main_loop()
        return {"data_set": data_set}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
