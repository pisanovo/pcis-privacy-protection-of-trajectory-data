from location_cloaking.location_server.granularity_plane.plane_data import PlaneDataProvider
from location_cloaking.model.data import GranularityPlaneDimensions


class ManualPlaneDataProvider(PlaneDataProvider):
    def get_plane_dimensions(self) -> GranularityPlaneDimensions:
        width = float(input("Enter granularity plane width: "))
        height = float(input("Enter granularity plane height: "))

        prompt_answer = input("Start plane at (0,0)? [y/n]")

        x_min = 0
        x_max = width
        y_min = 0
        y_max = height

        if prompt_answer == "n":
            x_min = float(input("Enter x axis start: "))
            y_min = float(input("Enter y axis start: "))
            x_max = x_min + width
            y_max = y_min + height

        return GranularityPlaneDimensions(width, height, x_min, x_max, y_min, y_max)
