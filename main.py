import numpy as np


# Sample format of the request data
request_data = {
    "size": {"x": 40, "y": 20},
    "zoom_level": 1.0,
    "pixels_per_point": 2,
    "central_point": {"x": 0.0, "y": 0.0},
}

# Request data from the client transformed into variables
RESOLUTION = (
    request_data["size"]["x"],
    request_data["size"]["y"],
)  # resolution of the image as a tuple
PIXEL_PP = request_data["pixels_per_point"]  # how many pixels per point
ZOOM_LEVEL = request_data["zoom_level"]
CENTRAL_POINT = complex(
    request_data["central_point"]["x"], request_data["central_point"]["y"]
)

# For now its here, but it might be a parameter in the request
MAX_ITERATIONS = 200  # maximum number of iterations to check if a complex number is in the Mandelbrot set
ITERATION_LIMIT = 5  # the limit for the iteration to check if a complex number is in the Mandelbrot set


data_table = np.zeros(
    (request_data["size"]["x"], request_data["size"]["y"]), dtype=int
)  # create a 2D array of zeros with the shape of the image


def z(zn, c):
    return zn**2 + c


def get_series_for_c(c: complex, max_iterations: int) -> list:
    series = []
    zn = 0
    for _ in range(max_iterations):
        zn = z(zn, c)
        series.append(zn)
    return series


def complex_num_check(c: complex, max_iterations: int, limit: float) -> int:
    """
    Check if a complex number is in the Mandelbrot set.
    Parameters:
    z0 (complex): The complex number to check.
    max_iterations (int): The maximum number of iterations to check.
    Returns:
    int: The number of iterations until the complex number left the Mandelbrot set.
    """
    zn = 0  # initial value of zn
    for i in range(max_iterations):
        zn = z(zn, c)  # calculate the next value of zn
        if abs(zn) > limit:
            return i
    return max_iterations


def xlim_ylim_rescale(
    resolution: tuple, zoom_level: float, central_point: complex
) -> dict:
    aspect_ratio = resolution[0] / resolution[1]
    plane_default_limits = {  # the default limits of the complex plane at zoom 1
        "x_min": -2.5,
        "x_max": 2.5,
        "y_min": -2.5,
        "y_max": 2.5,
    }
    plane_limits = plane_default_limits.copy()

    for key in plane_limits:
        if key.startswith("x") and aspect_ratio < 1:
            plane_limits[key] = (
                (plane_default_limits[key] + central_point.real)
                * aspect_ratio
                / zoom_level
            )
            continue
        elif key.startswith("x") and aspect_ratio >= 1:
            plane_limits[key] = (
                plane_default_limits[key] + central_point.real
            ) / zoom_level

            continue
        elif key.startswith("y") and aspect_ratio > 1:
            plane_limits[key] = (
                (plane_default_limits[key] + central_point.real)
                / aspect_ratio
                / zoom_level
            )
            continue
        elif key.startswith("y") and aspect_ratio <= 1:
            plane_limits[key] = (
                plane_default_limits[key] + central_point.real
            ) / zoom_level
            continue
    return plane_limits


def main_loop(
    data_table: np.array,
    central_point: complex,
    pixels_per_point: int,
    resolution: tuple,
    max_iterations: int,
    limit: int,
    zoom_level: float,
) -> np.array:
    # THIS IS NOT RIGHT
    plane_limits = xlim_ylim_rescale(resolution, zoom_level, central_point)
    increment_real = (plane_limits["x_max"] - plane_limits["x_min"]) / resolution[0]
    increment_imag = (plane_limits["y_max"] - plane_limits["y_min"]) / resolution[1]
    print(increment_real, increment_imag)
    current_point = complex(plane_limits["x_min"], plane_limits["y_min"])
    # each row represents a row of numbers where the step is the pixels_per_point
    for y_idx in range(0, len(data_table), pixels_per_point):
        # each item in each row represents a point in the complex plane, skipping each step
        for x_idx in range(0, len(data_table[0]), pixels_per_point):
            # calculate the number of iterations for each point, where the step is the pixels_per_point
            # store it in the data table, but amend based on the pixels_per_point

            y_idx_start, y_idx_end = y_idx, y_idx + pixels_per_point
            x_idx_start, x_idx_end = x_idx, x_idx + pixels_per_point
            mandelbrot_iters = complex_num_check(current_point, max_iterations, limit)
            data_table[y_idx_start:y_idx_end, x_idx_start:x_idx_end] = mandelbrot_iters
            # print(current_point)
            # change the current point to the next target for calculation
            current_point += complex(increment_real, increment_imag)

    return data_table


if __name__ == "__main__":
    output = main_loop(
        data_table=data_table,
        central_point=CENTRAL_POINT,
        pixels_per_point=PIXEL_PP,
        resolution=RESOLUTION,
        max_iterations=MAX_ITERATIONS,
        limit=ITERATION_LIMIT,
        zoom_level=ZOOM_LEVEL,
    )
    # print(output)
    print("Sum:", np.sum(output))
