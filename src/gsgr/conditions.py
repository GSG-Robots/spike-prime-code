from .utils import Timer
from .configuration import hardware as hw
import math
from ._condition_base import ConditionBase


class Infinite(ConditionBase): ...


class Cm(ConditionBase):
    def __init__(self, value: int) -> None:
        self.value = value
        
    def setup(self):
        hw.right_motor.set_degrees_counted(0)
        hw.left_motor.set_degrees_counted(0)

    def check(self):
        return (
            (
                abs(hw.right_motor.get_degrees_counted())
                + abs(hw.left_motor.get_degrees_counted())
            )
            / 360
            * math.pi
            * hw.tire_radius
        ) >= self.value


class Sec(ConditionBase):
    def __init__(self, value: int) -> None:
        self.value = value
        self.timer = Timer()
        
    def setup(self):
        self.timer.reset()

    def check(self):
        return self.timer.elapsed >= self.value


# class Line(ConditionBase):
#     def check(self, run):
#         return (
#             run.front_light_sensor.get_reflected_light() < run.light_black_value + 5
#             or run.back_light_sensor.get_reflected_light() < run.light_black_value + 5
#         )


# class Deg(ConditionBase):
#     def __init__(self, value: int) -> None:
#         self.value = value

#     def check(self, run):
#         return (
#             self.value - run.turning_degree_tolerance
#             <= run.brick.motion_sensor.get_yaw_angle()
#             <= self.value + run.turning_degree_tolerance
#         )
