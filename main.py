from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

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
def get_mandelbrot(request_data: MandelSchema):

    try:
        mdlbrt = Mandelbrot()
        data_set = mdlbrt.main_loop(request_data)
        data_list = data_set.tolist()
        return {"mandel_set": data_list}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
