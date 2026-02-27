import os

import numpy as np
import h5py
from tqdm import tqdm

from src.schemas import MandelData, MandelLineSpaceSchema
from src.mandelbrot import Mandelbrot


class H5Cache:
    def __init__(
        self,
        data_folder="cache",
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
        self.keys = {}  # The keys at a specific level

    def create_cache(self, data: MandelData) -> None:
        """
        Creates a cache in an HDF5 file for the given MandelData object.
        The data is stored in the HDF5 file under the level of the MandelData object.
        Parameters:
            data (MandelData): The MandelData object containing the data to be cached.
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

    def read_cache(self, level: str) -> MandelData:
        """
        Reads the cache data for the specified level.
        Args:
            level (str): The level of the cache data to read.
        Returns:
            MandelData: An instance of the MandelData class containing the cache data.

        """
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
        # The base name will be zoom_x_y where x and y are the coordinates of the block
        base_name = "0_0_0"

        # Create the initial level
        mdlbrt = Mandelbrot()
        mdl_data = mdlbrt.mandel_data_from_lines(starting_linespace)
        mdl_data.level = base_name
        self.create_cache(mdl_data)
        self.keys[0] = [mdl_data.level]  # Add the key to the keys list

        current_level = 0  # The starting/current depth level
        while current_level < depth:
            for parrent_item in tqdm(
                self.keys[current_level],
                total=len(self.keys[current_level]),
                desc=f"Generating sublevel {current_level+1}",
                bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [Time taken: {elapsed_s} seconds]",
                ncols=100,
            ):
                parrent_mdl_data = self.read_cache(parrent_item)
                self.generate_next_level(parrent_mdl_data)
            # Go to the next level
            current_level += 1

    def generate_next_level(self, parrent_mdl_data: MandelData) -> None:
        """
        Generates the next level of Mandelbrot data based on the parent MandelData.

        Args:
            parrent_mdl_data (MandelData): The parent MandelData object.
        """
        parent_x_line = parrent_mdl_data.x_line
        parent_y_line = parrent_mdl_data.y_line
        parrent_name = parrent_mdl_data.level
        parent_depth, parent_x_idx, parent_y_idx = map(int, parrent_name.split("_"))

        current_depth = parent_depth + 1
        current_x_line = np.linspace(
            parent_x_line[0],
            parent_x_line[-1],
            len(parent_x_line) * self.level_granularity,
        )
        current_y_line = np.linspace(
            parent_y_line[-1],
            parent_y_line[0],
            len(parent_y_line) * self.level_granularity,
        )  # Reverse the y_line to match the coordinate system from left to right, top to bottom
        iter_box = np.arange(self.level_granularity**2).reshape(
            self.level_granularity, -1
        )  # Creates a 2D array of the iteration box this can be removed
        mdlbrt = Mandelbrot()

        current_y_idx = parent_y_idx * self.level_granularity
        for box_row, y_item in zip(
            iter_box, np.array_split(current_y_line, self.level_granularity)
        ):

            current_x_idx = parent_x_idx * self.level_granularity
            for _, x_item in zip(
                box_row, np.array_split(current_x_line, self.level_granularity)
            ):
                mdl_line_space = MandelLineSpaceSchema(
                    x_line=x_item, y_line=y_item[::-1]
                )
                mdl_data = mdlbrt.mandel_data_from_lines(mdl_line_space)
                mdl_data.level = f"{current_depth}_{current_x_idx}_{current_y_idx}"
                if current_depth not in self.keys:
                    self.keys[current_depth] = []
                self.keys[current_depth].append(mdl_data.level)
                # Add the key to the keys list
                self.create_cache(mdl_data)
                current_x_idx += 1
            current_y_idx += 1

    def get_keys(self, depth=None):
        """
        Returns the keys at a specific level depth from the hdf5 file.
        If depth is None, returns all keys from the file.
        Args:
            depth (int): The desired level depth, if None, returns all keys.
        Returns:
            list: A list of keys from the hdf5 file.
        """
        file_keys = []
        with h5py.File(self.file_path, "r") as f:
            f.visit(file_keys.append)
        if depth is not None:
            filtered_keys = []
            for key in file_keys:
                if int(key.split("_")[0]) == depth:
                    filtered_keys.append(key)
            return filtered_keys
        else:
            return file_keys

    def create_file(self):
        """
        Creates an initial empty HDF5 file at the specified file path when the class is instantiated.

        """
        os.makedirs(self.data_folder, exist_ok=True)
        if os.path.exists(self.file_path):
            os.remove(self.file_path)
            with h5py.File(self.file_path, "w") as f:
                pass
        else:
            with h5py.File(self.file_path, "w") as f:
                pass


if __name__ == "__main__":

    def main():
        h5_cache = H5Cache()
        # mandel_space = MandelLineSpaceSchema(
        #     x_line=np.linspace(-2.5, 2.5, 100), y_line=np.linspace(-1.25, 1.25, 50)
        # )
        # h5_cache.create_initial_cache(mandel_space, depth=4, level_granularity=2)
        print(h5_cache.get_keys())

    main()
