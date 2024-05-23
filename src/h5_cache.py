import os
import timeit

import numpy as np
import h5py

from src.schemas import MandelRequestSchema, XYpointFloat, XYpointInt, MandelData
from src.mandelbrot import Mandelbrot


class H5Cache:
    def __init__(self, data_folder="h5data", file_name="data.hdf5") -> None:
        current_dir = os.getcwd()
        self.data_folder = os.path.join(current_dir, data_folder)
        self.file_name = file_name
        self.file_path = os.path.join(self.data_folder, self.file_name)

        self.create_file()  # Create the folder and file if it doesn't exist

    def create_cache(self, data: MandelData):
        with h5py.File(self.file_path, "w") as f:
            level_group = f.create_group(f"L_{data.level}")
            level_group.create_dataset(
                "count_grid", data=data.count_grid.astype(np.uint8)
            )
            level_group.create_dataset("x_line", data=data.x_line.astype(np.float64))
            level_group.create_dataset("y_line", data=data.y_line.astype(np.float64))
            level_group.create_dataset(
                "red", data=data.color_data["red"].astype(np.uint8)
            )
            level_group.create_dataset(
                "green", data=data.color_data["green"].astype(np.uint8)
            )
            level_group.create_dataset(
                "blue", data=data.color_data["blue"].astype(np.uint8)
            )

    def read_cache(self, level: int):
        with h5py.File(self.file_path, "r") as f:
            level_group = f[f"L_{level}"]
            count_grid = level_group["count_grid"][:]
            x_line = level_group["x_line"][:]
            y_line = level_group["y_line"][:]
            red = level_group["red"][:]
            green = level_group["green"][:]
            blue = level_group["blue"][:]
            return MandelData(
                count_grid=count_grid,
                x_line=x_line,
                y_line=y_line,
                color_data={"red": red, "green": green, "blue": blue},
                level=level,
            )

    def create_file(self):
        os.makedirs(self.data_folder, exist_ok=True)
        if not os.path.exists(self.data_folder):
            with h5py.File(self.file_path, "w") as f:
                pass


if __name__ == "__main__":

    def main():
        sample_request_data = MandelRequestSchema(
            size=XYpointInt(x=5000, y=5000),
            zoom_level=1,
            pixel_per_point=1,
            central_point=XYpointFloat(x=0.0, y=0.0),
        )

        mdlbrd = Mandelbrot()
        start_time = timeit.default_timer()

        count_grid, x_line, y_line, color_data = mdlbrd.main_loop(
            mdl_data=sample_request_data
        )
        data = MandelData(
            count_grid=count_grid,
            x_line=x_line,
            y_line=y_line,
            color_data=color_data,
            level="1",
        )
        end_time = timeit.default_timer()
        print(f"The main loop took {end_time-start_time}.")

        h5_cache = H5Cache()
        start_time = timeit.default_timer()
        h5_cache.create_cache(data=data)
        end_time = timeit.default_timer()
        print(f"Cache creation took {end_time-start_time}.")

        start_time = timeit.default_timer()
        data = h5_cache.read_cache(level="1")
        end_time = timeit.default_timer()
        print(f"Cache read took {end_time-start_time}.")
        print(data)

    main()
