import numpy as np
from src.schemas import MandelSchema, XYpointFloat, XYpointInt


class Mandelbrot:


    def __init__(self):
        """
        Initialize the Mandelbrot class.

        Args:
            size (dict): A dictionary containing the size of the Mandelbrot image in pixels.
            zoom_level (float): The zoom level of the Mandelbrot image.
            pixels_per_point (int): The number of pixels per point in the Mandelbrot image.
            central_point (dict): A dictionary containing the coordinates of the central point of the Mandelbrot image.
            max_iterations (int, optional): The maximum number of iterations to compute for each point. Defaults to 200.
            iteration_limit (int, optional): The iteration limit for determining if a point is in the Mandelbrot set. Defaults to 2.
        """

        self.plane_default_limits = (
            {  # the default limits of the complex plane at zoom 1
                "x_min": -2.5,
                "x_max": 2.5,
                "y_min": -2.5,
                "y_max": 2.5,
            }
        )

    def generate_series_c(self, c: complex, iterations:int):
        """
        Generates a series of complex numbers based on the Mandelbrot set algorithm.
        Args:
            c (complex): The complex number for which the series is generated.
        Returns:
            list: A list of complex numbers representing the generated series.
        """
        series = []
        zn = 0
        for _ in range(iterations):
            zn = zn ** 2 + c
            series.append(zn)
        return series

    def xlim_ylim_rescale(self, mdl_data: MandelSchema) -> dict:
        """
        Rescales the x and y limits of the plane based on the aspect ratio and zoom level.
        Returns:
            dict: A dictionary containing the rescaled x and y limits of the plane.
        """
        aspect_ratio = mdl_data.size.x / mdl_data.size.y
        plane_limits = self.plane_default_limits.copy()

        for key in plane_limits:
            if key.startswith("x") and aspect_ratio < 1:
                plane_limits[key] = (
                    (self.plane_default_limits[key] + mdl_data.central_point.x)
                    * aspect_ratio
                    / mdl_data.zoom_level
                )
                continue
            elif key.startswith("x") and aspect_ratio >= 1:
                plane_limits[key] = (
                    self.plane_default_limits[key] + mdl_data.central_point.x
                ) /mdl_data.zoom_level

                continue
            elif key.startswith("y") and aspect_ratio > 1:
                plane_limits[key] = (
                    (self.plane_default_limits[key] + mdl_data.central_point.y)
                    / aspect_ratio
                    / mdl_data.zoom_level
                )
                continue
            elif key.startswith("y") and aspect_ratio <= 1:
                plane_limits[key] = (
                    self.plane_default_limits[key] + mdl_data.central_point.y
                ) / mdl_data.zoom_level
                continue
        return plane_limits

    def main_loop(self, mdl_data: MandelSchema) -> np.array:
        """
        Perform the main loop to calculate the Mandelbrot set.
        Returns:
            np.array: The data table containing the number of iterations for each point in the complex plane.
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

        return count_grid


if __name__ == "__main__":
    import timeit
    sample_request_data = MandelSchema(
        size=XYpointInt(x=3000, y=2000),
        zoom_level=1,
        pixel_per_point=1,
        central_point=XYpointFloat(x=0.0, y=0.0),
        max_iter=200,
        iteration_limit=2,
    )

    mdlbrd = Mandelbrot()
    start_time = timeit.default_timer()
    output = mdlbrd.main_loop(mdl_data=sample_request_data)
    end_time = timeit.default_timer()
    # print(output)
    # print("Sum:", np.sum(output))
    print(f"The main loop took {end_time-start_time}.")
