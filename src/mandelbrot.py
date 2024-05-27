import numpy as np
from PIL import Image
from src.schemas import (
    MandelData,
    MandelLineSpaceSchema,
    MandelRequestSchema,
    XYpointFloat,
    XYpointInt,
)

import timeit


class Mandelbrot:
    """
    A class used to generate and manipulate Mandelbrot sets.

    Attributes:
        `plane_default_limits` (dict): The default limits of the complex plane at zoom 1.

    Methods:
        `generate_series_c(c: complex, iterations:int)`: Generates a series of complex numbers based
                                                         on the Mandelbrot set algorithm.
        `xlim_ylim_rescale(mdl_data: MandelRequestSchema) -> dict`: Rescales the x and y limits of the plane
                                                             based on the aspect ratio and zoom level.
        `main_loop(mdl_data: MandelRequestSchema) -> np.array`: Perform the main loop to calculate the
                                                         Mandelbrot set.
    """

    def __init__(self):
        """
        Initializes the Mandelbrot set generator.
        """
        self.plane_default_limits = (
            {  # the default limits of the complex plane at zoom 1
                "x_min": -2.5,
                "x_max": 2.5,
                "y_min": -2.5,
                "y_max": 2.5,
            }
        )

    def generate_series_c(self, c: complex, iterations: int):
        """
        Generates a series of complex numbers based on the Mandelbrot set algorithm.

        Args:
            `c` (complex): The complex number for which the series is generated.
            `iterations` (int): The number of iterations to perform.

        Returns:
            list: A list of complex numbers representing the generated series.
        """
        series = []
        zn = 0
        for _ in range(iterations):
            zn = zn**2 + c
            series.append(zn)
        return series

    def xlim_ylim_rescale(self, mdl_data: MandelRequestSchema) -> dict:
        """
        Rescales the x and y limits of the plane based on the aspect ratio and zoom level.

        Args:
            `mdl_data` (MandelRequestSchema): An object containing parameters for the Mandelbrot set calculation.

        Returns:
            dict: A dictionary containing the rescaled x and y limits of the plane. The keys are 'x_min',
                  'x_max', 'y_min', and 'y_max'.
        """
        aspect_ratio = mdl_data.size.x / mdl_data.size.y
        plane_limits = self.plane_default_limits.copy()

        for key in plane_limits:
            if key.startswith("x") and aspect_ratio < 1:
                plane_limits[key] = (
                    self.plane_default_limits[key] / mdl_data.zoom_level
                    + mdl_data.central_point.x
                ) * aspect_ratio
                continue
            elif key.startswith("x") and aspect_ratio >= 1:
                plane_limits[key] = (
                    self.plane_default_limits[key] / mdl_data.zoom_level
                    + mdl_data.central_point.x
                )

                continue
            elif key.startswith("y") and aspect_ratio > 1:
                plane_limits[key] = (
                    self.plane_default_limits[key] / mdl_data.zoom_level
                    + mdl_data.central_point.y
                ) / aspect_ratio
                continue
            elif key.startswith("y") and aspect_ratio <= 1:
                plane_limits[key] = (
                    self.plane_default_limits[key] / mdl_data.zoom_level
                    + mdl_data.central_point.y
                )
                continue
        return plane_limits

    def colorize(
        self,
        count_grid: np.array,
        max_iter: int,
        pixel_pp=1,
        is_canvas=False,
    ):
        """
        Colorizes the Mandelbrot set based on the number of iterations it took for each point to escape.

        Args:
            count_grid (np.array): A 2D numpy array containing the number of iterations it took for each
                                   point in the complex plane to escape the Mandelbrot set.
            max_iter (int): The maximum number of iterations allowed for each point.
            pixel_pp (int, optional): The number of pixels per point. Defaults to 1.
            is_canvas (bool, optional): Indicates whether the output should be formatted for a canvas. 
                                        Defaults to False.

        Returns:
            If is_canvas is True, returns a flattened list containing the color values for each pixel.
            If is_canvas is False, returns a dictionary containing the color values for each channel (red, green, blue).
        """
        color_max, color_min = 255, 0
        max_iter_grid = np.full_like(count_grid, max_iter)
        np_red = count_grid / max_iter_grid * color_max
        np_green = (np.cos(count_grid) + 1) / 2 * color_max
        np_blue = (np.sin(count_grid) + 1) / 2 * color_max
        if is_canvas:
            gamma = color_max
            np_red = np_red.repeat(pixel_pp, axis=1).astype(int).flatten()
            np_green = np_green.repeat(pixel_pp, axis=1).astype(int).flatten()
            np_blue = np_blue.repeat(pixel_pp, axis=1).astype(int).flatten()
            np_gamma = np.full_like(np_red, gamma)
            new_arr = np.vstack([np_red, np_green, np_blue, np_gamma])
            return new_arr.flatten("F").tolist()
        else:
            colors_dic = {}
            colors_dic["red"] = np_red.repeat(pixel_pp, axis=1).astype(int)
            colors_dic["green"] = np_green.repeat(pixel_pp, axis=1).astype(int)
            colors_dic["blue"] = np_blue.repeat(pixel_pp, axis=1).astype(int)
            return colors_dic

    def main_loop(
        self, x_line: np.array, y_line: np.array, max_iter: int, iteration_limit: int
    ) -> MandelData:
        """
        Perform the main loop of the Mandelbrot algorithm.

        Args:
            x_line (np.array): Array of x-coordinates for the complex grid.
            y_line (np.array): Array of y-coordinates for the complex grid.
            max_iter (int): Maximum number of iterations.
            iteration_limit (int): Limit for the absolute value of the complex numbers.

        Returns:
            MandelData: Object containing the results of the Mandelbrot algorithm.
        """

        complex_grid = np.zeros(
            (len(y_line), len(x_line)), dtype=complex
        )  # Create an empty complex grid
        x_real, y_imag = np.meshgrid(
            x_line, y_line
        )  # Create the meshgrid in order to fill in the complex grid
        complex_grid.real = x_real
        complex_grid.imag = y_imag

        mask_grid = np.ones_like(
            complex_grid, dtype=bool
        )  # Create a mask grid of the complex plane to follow which elements to do the calculations
        count_grid = np.zeros_like(
            complex_grid, dtype=int
        )  # Keeps count of the operations
        z_grid = np.zeros_like(
            complex_grid
        )  # Z Grid to keep the values of the complex numbers

        # The main loop
        for _ in range(max_iter):
            z_grid[mask_grid] = np.power(z_grid[mask_grid], 2) + complex_grid[mask_grid]
            mask_grid = np.logical_and(mask_grid, np.abs(z_grid) <= iteration_limit)
            count_grid += mask_grid

        data = MandelData(
            x_line=x_line, y_line=y_line, count_grid=count_grid, color_data=None
        )
        return data

    def mandel_data_from_request(self, mdl_data: MandelRequestSchema):
        """
        Generate Mandelbrot data based on the provided MandelRequestSchema.
        If the MandelRequestSchema is canvas, the color data is returned in canvas format (i.e. not RGB array)

        Args:
            mdl_data (MandelRequestSchema): The MandelRequestSchema object containing the parameters for generating Mandelbrot data.

        Returns:
            MandelData: The generated MandelData object containing the Mandelbrot data.
            The returned object is in np.arrays format, needs to be transformed to lists in order to return to backend.
        """
        plane_limits = self.xlim_ylim_rescale(mdl_data)
        # Calc the sizes of the x and y axes
        x_size = mdl_data.size.x // mdl_data.pixel_per_point
        y_size = mdl_data.size.y // mdl_data.pixel_per_point
        # Generate the main X and y lines
        x_line = np.linspace(
            plane_limits["x_min"], plane_limits["x_max"], x_size, endpoint=False
        )
        y_line = np.linspace(
            plane_limits["y_max"], plane_limits["y_min"], y_size, endpoint=False
        )  # y is inverted, as the y starts from positive to negative
        data = self.main_loop(
            x_line, y_line, mdl_data.max_iter, mdl_data.iteration_limit
        )
        data.color_data = self.colorize(
            data.count_grid,
            mdl_data.max_iter,
            mdl_data.pixel_per_point,
            mdl_data.is_canvas,
        )
        return data

    def mandel_data_from_lines(self, mdl_data: MandelLineSpaceSchema) -> MandelData:
        """
        Generates Mandelbrot data from the given MandelLineSpaceSchema.

        Args:
            mdl_data (MandelLineSpaceSchema): The MandelLineSpaceSchema object containing the input parameters.

        Returns:
            MandelData: The generated MandelData object.
        """
        data = self.main_loop(
            mdl_data.x_line,
            mdl_data.y_line,
            mdl_data.max_iter,
            mdl_data.iteration_limit,
        )
        data.color_data = self.colorize(data.count_grid, mdl_data.max_iter)
        return data




if __name__ == "__main__":

    def main():
        sample_request_data = MandelRequestSchema(
            size=XYpointInt(x=20, y=20),
            zoom_level=1,
            pixel_per_point=1,
            central_point=XYpointFloat(x=-0.8, y=0.2),
            max_iter=200,
            iteration_limit=2,
            is_canvas=False,
        )
        sample_mandel_data = MandelLineSpaceSchema(
            x_line=np.linspace(-2.5, 2.5, 20),
            y_line=np.linspace(-2.5, 2.5, 20),
            max_iter=200,
            iteration_limit=2,
        )

        mdlbrd = Mandelbrot()
        start_time = timeit.default_timer()
        # output = mdlbrd.mandel_data_from_request(mdl_data=sample_request_data)
        output = mdlbrd.mandel_data_from_lines(mdl_data=sample_mandel_data)
        end_time = timeit.default_timer()

        print(output.color_data['red'].shape)
        # print(len(color_data))
        # print("Sum:", np.sum(color_data))
        print(f"The main loop took {end_time-start_time}.")

    main()
