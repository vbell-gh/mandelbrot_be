import os
import timeit

import numpy as np
import h5py

from src.schemas import MandelData, MandelLineSpaceSchema
from src.mandelbrot import Mandelbrot


class H5Cache:
    def __init__(
        self,
        data_folder="h5data",
        file_name="data.hdf5",
    ) -> None:
        current_dir = os.getcwd()
        self.data_folder = os.path.join(current_dir, data_folder)
        self.file_name = file_name
        self.file_path = os.path.join(self.data_folder, self.file_name)

        self.create_file()  # Create the folder and file if it doesn't exist

        self.depth = (
            0  # This is the depth of the mandelbrot set used in create_initial_cache()
        )
        self.level_granularity = 2  # How many times to split the x and y lines
        self.base_name = "0"  # The base name of each level

    def create_cache(self, data: MandelData):
        """
        Creates a cache in an HDF5 file for the given MandelData object.
        The data is stored in the HDF5 file under the level of the MandelData object.
        Parameters:
            data (MandelData): The MandelData object containing the data to be cached.

        Returns:
            None
        """
        with h5py.File(self.file_path, "r+") as f:
            level_group = f.create_group(data.level)
            level_group.create_dataset(
                "count_grid", data=data.count_grid.astype(np.uint8)
            )
            level_group.create_dataset("x_line", data=data.x_line)
            level_group.create_dataset("y_line", data=data.y_line)
            level_group.create_dataset("red", data=data.color_data["red"])
            level_group.create_dataset("green", data=data.color_data["green"])
            level_group.create_dataset("blue", data=data.color_data["blue"])

    def read_cache(self, level: str):
        """
        Reads the cache data for the specified level.
        Args:
            level (str): The level of the cache data to read.
        Returns:
            MandelData: An instance of the MandelData class containing the cache data.

        """
        print(level)
        with h5py.File(self.file_path, "r") as f:
            level_group = f[level]
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

    def create_initial_cache(
        self,
        starting_linespace: MandelLineSpaceSchema,
        depth: int,
        level_granularity=2,
    ):
        """
        Creates the initial cache for the Mandelbrot set.
        The cache is created with the specified depth and level granularity.
        Where each linespace is split into level_granularity**2 parts.
        This is done depth n times where n is the depth of the cache.
        Args:
            starting_linespace (MandelLineSpaceSchema): The starting line space for the Mandelbrot set.
            depth (int): The depth of the cache.
            level_granularity (int, optional): The level granularity. Defaults to 2.
        """

        # Pass the initial level as they are used in other functions
        self.depth = depth
        self.level_granularity = level_granularity

        # Create the initial level and the base name for it
        self.base_name = len(str(level_granularity**2 - 1)) * str(0)

        # Create the initial level
        mdlbrt = Mandelbrot()
        mdl_data = mdlbrt.mandel_data_from_lines(starting_linespace)
        mdl_data.level = str(self.base_name)
        self.create_cache(mdl_data)

        max_level = self.base_name * self.depth

        current_level = self.base_name
        while len(current_level) <= len(max_level):

            for parrent_item in self.get_keys_at_level(current_level):
                parrent_mdl_data = self.read_cache(str(parrent_item))
                self.generate_next_level(parrent_mdl_data)

            current_level += self.base_name

    def generate_next_level(self, parrent_mdl_data: MandelData) -> None:
        """
        Generates the next level of Mandelbrot data based on the parent MandelData.

        Args:
            parrent_mdl_data (MandelData): The parent MandelData object.
        """
        parent_x_line = parrent_mdl_data.x_line
        parent_y_line = parrent_mdl_data.y_line
        parrent_name = parrent_mdl_data.level

        next_x_line = np.linspace(
            parent_x_line[0],
            parent_x_line[-1],
            len(parent_x_line) * self.level_granularity,
        )
        next_y_line = np.linspace(
            parent_y_line[-1],
            parent_y_line[0],
            len(parent_y_line) * self.level_granularity,
        )  # Reverse the y_line to match the coordinate system from left to right, top to bottom
        iter_box = np.arange(self.level_granularity**2).reshape(
            self.level_granularity, -1
        )  # Creates a 2D array of the iteration box
        mdlbrt = Mandelbrot()
        for box_row, y_item in zip(
            iter_box, np.array_split(next_y_line, self.level_granularity)
        ):
            for box_item, x_item in zip(
                box_row, np.array_split(next_x_line, self.level_granularity)
            ):
                print(box_item, "x:", x_item[0], "y:", y_item[0])
                mdl_line_space = MandelLineSpaceSchema(
                    x_line=x_item, y_line=y_item[::-1]
                )
                mdl_data = mdlbrt.mandel_data_from_lines(mdl_line_space)
                formated_name = str(box_item).zfill(len(self.base_name))
                mdl_data.level = f"{parrent_name}{formated_name}"
                self.create_cache(mdl_data)

    def get_keys_at_level(self, level_depth: int):
        """
        Retrieves the keys at a specific level depth in the HDF5 file.

        Args:
            level_depth (int): The desired level depth.

        Returns:
            list: A list of keys at the specified level depth.
        """
        required_level_len = len(level_depth)
        with h5py.File(self.file_path, "r") as f:
            keys_l = list(f.keys())
            return [key for key in keys_l if len(key) == required_level_len]

    def create_file(self):
        """
        Creates an initial empty HDF5 file at the specified file path when the class is instantiated.

        """
        os.makedirs(self.data_folder, exist_ok=True)
        if not os.path.exists(self.file_path):
            with h5py.File(self.file_path, "w") as f:
                pass


if __name__ == "__main__":

    def main():
        h5_cache = H5Cache()
        mandel_space = MandelLineSpaceSchema(
            x_line=np.linspace(-2.5, 2.5, 100), y_line=np.linspace(-1.25, 1.25, 50)
        )
        h5_cache.create_initial_cache(mandel_space, depth=4, level_granularity=2)

    main()
