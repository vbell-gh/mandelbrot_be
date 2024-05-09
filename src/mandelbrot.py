import numpy as np
from schemas import MandelSchema, XYpointFloat, XYpointInt

class Mandelbrot:
    """
    Represents the Mandelbrot set.

    ## Methods

    z(zn, c):
        Calculate the next value in the Mandelbrot sequence.
    generate_series_c(c):
        Generates a series of complex numbers based on the Mandelbrot set algorithm.
    c_num_check(c_point):
        Check if the given complex number c_point belongs to the Mandelbrot set.
    xlim_ylim_rescale():
        Rescales the x and y limits of the plane based on the aspect ratio and zoom level.
    main_loop():
        Perform the main loop to calculate the Mandelbrot set.
    """

    def __init__(
        self,
        size: dict,
        zoom_level: float,
        pixels_per_point: int,
        central_point: dict,
        max_iterations=200,
        iteration_limit=2,
    ):
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
        self.resolution = (size["x"], size["y"])
        self.pixel_pp = pixels_per_point
        self.zoom = zoom_level
        self.central_point = complex(central_point["x"], central_point["y"])

        self.max_iterations = max_iterations
        self.iteration_limit = iteration_limit

        self.data_table = np.zeros((self.resolution[0], self.resolution[1]))

        self.plane_default_limits = {  # the default limits of the complex plane at zoom 1
            "x_min": -2.5,
            "x_max": 2.5,
            "y_min": -2.5,
            "y_max": 2.5,
        }

    def z(self, zn, c):
        """Calculate the next value in the Mandelbrot sequence.
        Args:
            zn (complex): The current value in the sequence.
            c (complex): The constant value.
        Returns:
            complex: The next value in the sequence.
        """
        return zn**2 + c

    def generate_series_c(self, c: complex):
        """
        Generates a series of complex numbers based on the Mandelbrot set algorithm.
        Args:
            c (complex): The complex number for which the series is generated.
        Returns:
            list: A list of complex numbers representing the generated series.
        """
        series = []
        zn = 0
        for _ in range(self.max_iterations):
            zn = self.z(zn, c)
            series.append(zn)
        return series

    def c_num_check(self, c_point: complex):
        """
        Check if the given complex number c_point belongs to the Mandelbrot set.
        Parameters:
        - c_point (complex): The complex number to be checked.
        Returns:
        - int: The number of iterations required to determine if c_point belongs to the Mandelbrot set.
               If the number of iterations exceeds the maximum iterations, returns the maximum iterations.
        """
        zn = 0
        for i in range(self.max_iterations):
            zn = self.z(zn, c_point)
            if abs(zn) > self.iteration_limit:
                return i
        return self.max_iterations

    def xlim_ylim_rescale(self) -> dict:
        """
        Rescales the x and y limits of the plane based on the aspect ratio and zoom level.
        Returns:
            dict: A dictionary containing the rescaled x and y limits of the plane.
        """
        aspect_ratio = self.resolution[0] / self.resolution[1]

        plane_limits = self.plane_default_limits.copy()

        for key in plane_limits:
            if key.startswith("x") and aspect_ratio < 1:
                plane_limits[key] = (
                    (self.plane_default_limits[key] + self.central_point.real)
                    * aspect_ratio
                    / self.zoom
                )
                continue
            elif key.startswith("x") and aspect_ratio >= 1:
                plane_limits[key] = (
                    self.plane_default_limits[key] + self.central_point.real
                ) / self.zoom

                continue
            elif key.startswith("y") and aspect_ratio > 1:
                plane_limits[key] = (
                    (self.plane_default_limits[key] + self.central_point.real)
                    / aspect_ratio
                    / self.zoom
                )
                continue
            elif key.startswith("y") and aspect_ratio <= 1:
                plane_limits[key] = (
                    self.plane_default_limits[key] + self.central_point.real
                ) / self.zoom
                continue
        return plane_limits

    def main_loop(self) -> np.array:
        """
        Perform the main loop to calculate the Mandelbrot set.
        Returns:
            np.array: The data table containing the number of iterations for each point in the complex plane.
        """
        plane_limits = self.xlim_ylim_rescale()
        increment_real = (
            (plane_limits["x_max"] - plane_limits["x_min"])
            / self.resolution[0]
            * self.pixel_pp
        )
        increment_imag = (
            (plane_limits["y_max"] - plane_limits["y_min"])
            / self.resolution[1]
            * self.pixel_pp
        )
        current_point = complex(plane_limits["x_min"], plane_limits["y_min"])

        # each row represents a row of real numbers in the complex plane
        for y_idx in range(0, len(self.data_table), self.pixel_pp):
            # each item in each row represents a point in the complex plane, skipping each step
            for x_idx in range(0, len(self.data_table[0]), self.pixel_pp):
                # calculate the number of iterations for each point, where the step is the pixels_per_point
                # store it in the data table, but amend based on the pixels_per_point

                y_idx_s, y_idx_e = y_idx, y_idx + self.pixel_pp
                x_idx_s, x_idx_e = x_idx, x_idx + self.pixel_pp
                mandelbrot_iters = self.c_num_check(current_point)
                self.data_table[y_idx_s:y_idx_e, x_idx_s:x_idx_e] = mandelbrot_iters
                # change the current point to the next target for calculation
                current_point += complex(increment_real, 0)
            current_point = complex(
                plane_limits["x_min"],
                plane_limits["y_min"] + (increment_imag * y_idx_e) / self.pixel_pp,
            )

        return self.data_table


if __name__ == "__main__":
    request_data = {
        "size": {"x": 10, "y": 10},
        "zoom_level": 4.0,
        "pixels_per_point": 1,
        "central_point": {"x": 0.0, "y": 0.0},
    }
    mdlbrd = Mandelbrot(
        size=request_data["size"],
        zoom_level=request_data["zoom_level"],
        pixels_per_point=request_data["pixels_per_point"],
        central_point=request_data["central_point"],
    )
    output = mdlbrd.main_loop()
    print(output)
    print("Sum:", np.sum(output))
