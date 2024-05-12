import numpy as np
from src.schemas import MandelSchema, XYpointFloat, XYpointInt


class Mandelbrot:
    """
    A class used to generate and manipulate Mandelbrot sets.

    Attributes:
        `plane_default_limits` (dict): The default limits of the complex plane at zoom 1.

    Methods:
        `generate_series_c(c: complex, iterations:int)`: Generates a series of complex numbers based
                                                         on the Mandelbrot set algorithm.
        `xlim_ylim_rescale(mdl_data: MandelSchema) -> dict`: Rescales the x and y limits of the plane
                                                             based on the aspect ratio and zoom level.
        `main_loop(mdl_data: MandelSchema) -> np.array`: Perform the main loop to calculate the
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

    def xlim_ylim_rescale(self, mdl_data: MandelSchema) -> dict:
        """
        Rescales the x and y limits of the plane based on the aspect ratio and zoom level.

        Args:
            `mdl_data` (MandelSchema): An object containing parameters for the Mandelbrot set calculation.

        Returns:
            dict: A dictionary containing the rescaled x and y limits of the plane. The keys are 'x_min',
                  'x_max', 'y_min', and 'y_max'.
        """
        aspect_ratio = mdl_data.size.x / mdl_data.size.y
        plane_limits = self.plane_default_limits.copy()

        for key in plane_limits:
            if key.startswith("x") and aspect_ratio < 1:
                plane_limits[key] = (
                    (self.plane_default_limits[key]/ mdl_data.zoom_level + mdl_data.central_point.x)
                    * aspect_ratio
                    
                )
                continue
            elif key.startswith("x") and aspect_ratio >= 1:
                plane_limits[key] = (
                    self.plane_default_limits[key]/ mdl_data.zoom_level + mdl_data.central_point.x
                ) 

                continue
            elif key.startswith("y") and aspect_ratio > 1:
                plane_limits[key] = (
                    (self.plane_default_limits[key]/ mdl_data.zoom_level + mdl_data.central_point.y)
                    / aspect_ratio
                    
                )
                continue
            elif key.startswith("y") and aspect_ratio <= 1:
                plane_limits[key] = (
                    self.plane_default_limits[key] / mdl_data.zoom_level + mdl_data.central_point.y
                )
                continue
        return plane_limits

    def colorize(
        self, count_grid: np.array, max_iter: int, pixel_pp: int
    ) -> dict[np.array]:
        """
        Colorizes the Mandelbrot set based on the number of iterations it took for each point to escape.

        Args:
            count_grid (np.array): A 2D numpy array containing the number of iterations it took for each
                                   point in the complex plane to escape the Mandelbrot set.

        Returns:
           dictionarry with lists
        """
        color_max, color_min = 255, 0
        max_iter_grid = np.full_like(count_grid, max_iter)
        colors_dic = {}
        np_red = count_grid / max_iter_grid * color_max
        np_green = (np.cos(count_grid) + 1) / 2 * 255
        np_blue = (np.sin(count_grid) + 1) / 2 * 255
        colors_dic["red"] = np_red.repeat(pixel_pp, axis=1).astype(int).tolist()
        colors_dic["green"] = np_green.repeat(pixel_pp, axis=1).astype(int).tolist()
        colors_dic["blue"] = np_blue.repeat(pixel_pp, axis=1).astype(int).tolist()
        return colors_dic

    def main_loop(self, mdl_data: MandelSchema) -> np.array:
        """
        Perform the main loop to calculate the Mandelbrot set.

        This function generates a grid of complex numbers representing points in the complex plane,
        and then iteratively applies the Mandelbrot function to each point. The number of iterations
        it takes for each point to escape the Mandelbrot set is recorded in a count grid.

        The function takes as input a `MandelSchema` object, which contains parameters such as the
        size of the plane, the pixel density, the maximum number of iterations, and the iteration limit.

        Args:
            mdl_data (MandelSchema): An object containing parameters for the Mandelbrot set calculation.

        Returns:
            np.array: A 2D numpy array containing the number of iterations it took for each point in
                    the complex plane to escape the Mandelbrot set. Points that did not escape within
                    the maximum number of iterations are marked with the maximum iteration count.
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
        complex_grid = np.zeros(
            (y_size, x_size), dtype=complex
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
        for _ in range(mdl_data.max_iter):
            z_grid[mask_grid] = z_grid[mask_grid] ** 2 + complex_grid[mask_grid]
            mask_grid = np.logical_and(
                mask_grid, np.abs(z_grid) <= mdl_data.iteration_limit
            )
            count_grid += mask_grid
        # implement np.repeat with pixel_per_point
        color_dic = self.colorize(
            count_grid, mdl_data.max_iter, mdl_data.pixel_per_point
        )
        return (
            count_grid.repeat(mdl_data.pixel_per_point, axis=1),
            complex_grid.repeat(mdl_data.pixel_per_point, axis=1),
            color_dic,
        )


if __name__ == "__main__":
    import timeit

    sample_request_data = MandelSchema(
        size=XYpointInt(x=500, y=500),
        zoom_level=1,
        pixel_per_point=1,
        central_point=XYpointFloat(x=0.0, y=1.0),
        max_iter=250,
        iteration_limit=2,
    )

    mdlbrd = Mandelbrot()
    start_time = timeit.default_timer()
    count_grid, complex_grid, color_dic = mdlbrd.main_loop(mdl_data=sample_request_data)
    end_time = timeit.default_timer()
    # print(output)
    print("Sum:", np.sum(count_grid))
    print(f"The main loop took {end_time-start_time}.")
