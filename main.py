# LEGO type:standard slot:0 autostart
# OTTOS PROGRAMMIERUNG IN PYTHON
# pylint: disable=too-many-lines
# pylint: disable=trailing-newlines
"""
Current Program, uses PEP8 conform names and has the new MasterControlProgram class
This is work in progress so there is no docstr on new elements.
"""
from math import fabs, floor, pi

import hub
from micropython import const
from spike import ColorSensor, Motor, MotorPair, PrimeHub
from spike.control import Timer as __Timer, wait_for_seconds, wait_until

FRONT_RIGHT = const(3)
FRONT_LEFT = const(4)
BACK_RIGHT = const(1)
BACK_LEFT = const(2)

DEBUG_MODE = True

_100 = const(100)


class WrongUnitError(ValueError):
    """Non-valid unit used."""


class BatteryLowError(RuntimeError):
    """Error raised when in debug mode and running motors while battery low."""


class EnterDebugMenu(SystemExit):
    """Error raised when debug menu should be started."""


class EndingCondition:
    """Ending Condition: Infinite and Base for other Ending Conditions"""

    # Depending on which ending condition is chosen, the function returns True as long as it is not
    # valid, then False
    def check(self, run):
        """Returns if the EndingCondition is fulfilled"""
        # this ugly thing is used because pylint wants me to use the run arg.
        return not bool(run)  # returns False, so it runs infinite.

    def __or__(self, other):
        return OrCond(self, other)

    def __ror__(self, other):
        return OrCond(self, other)

    def __and__(self, other):
        return AndCond(self, other)

    def __rand__(self, other):
        return AndCond(self, other)


class OrCond(EndingCondition):
    """Ending Condition: Or"""

    def __init__(
        self, condition_a: EndingCondition, condition_b: EndingCondition
    ) -> None:
        self.condition_a = condition_a
        self.condition_b = condition_b

    def check(self, run):
        return self.condition_a.check(run) or self.condition_b.check(run)


class AndCond(EndingCondition):
    """Ending Condition: And"""

    def __init__(
        self, condition_a: EndingCondition, condition_b: EndingCondition
    ) -> None:
        self.condition_a = condition_a
        self.condition_b = condition_b

    def check(self, run):
        return self.condition_a.check(run) and self.condition_b.check(run)


class Cm(EndingCondition):
    """Ending Condition: Centimeter"""

    # Checks if given Ending Value is fulfilled
    def __init__(self, value: int) -> None:
        self.value = value

    def check(self, run):
        return (
            (
                abs(run.right_motor.get_degrees_counted())
                + abs(run.left_motor.get_degrees_counted())
            )
            / 360
            * pi
            * run.tire_radius
        ) >= self.value


class Sec(EndingCondition):
    """Ending Condition: Seconds"""

    # Checks if given Ending Value is fulfilled
    def __init__(self, value: int) -> None:
        self.value = value

    def check(self, run):
        return run.timer.now() >= self.value


class Line(EndingCondition):
    """Ending Condition: Line"""

    # Checks if given Ending Value is fulfilled
    def check(self, run):
        return (
            run.front_light_sensor.get_reflected_light() < run.light_black_value + 5
            or run.back_light_sensor.get_reflected_light() < run.light_black_value + 5
        )


class Deg(EndingCondition):
    """Ending Condition: Degrees"""

    # Checks if given Ending Value is fulfilled
    def __init__(self, value: int) -> None:
        self.value = value

    def check(self, run):
        return (
            self.value - run.turning_degree_tolerance
            <= run.brick.motion_sensor.get_yaw_angle()
            <= self.value + run.turning_degree_tolerance
        )


class Run:
    """Run-Class for contolling the robot."""

    def __init__(
        self,
        brick: PrimeHub,
        engines: list[str] = None,
        light_sensors: list[str] = None,
        correction_values: list[float] = None,
        hold_attachment: int = 1,
        tire_radius: float = 2.6,
        light_black_value: int = 10,
        light_middle_value: int = 50,
        turning_degree_tolerance: int = 2,
        debug_mode: bool = False,
        display_as: str = None,
    ):
        """
        Initiation of Run

        Parameters:
        brick: The Brick of the Robot
        engines: List of Motors (Left, Right, Driveshaft, Gearselector)
        lightSensors: List of Lightsensors (Front, Back)
        correctionValues: List of Correction Values (GyroDrive (p,i,d),
                            LineFollower (p,i,d), GyroTurn (p,i,d))
        tireRadius: Radius of the Robots tires
        lightBlackValue: The Lightvalue of Black
        lightMiddleValue: The middle Lightvalue between Black and White
        turningDegreeTolerance: Tolerance when turning for a degree
        debug_mode: Whether to add debug features. Currently only used for battery low exceptions.
        """

        # Setting all variables that don't change during the runs, i.e. the Motorports
        if engines is None:
            engines = ["D", "C", "F", "E"]
        if light_sensors is None:
            light_sensors = ["A", "B"]
        if correction_values is None:
            correction_values = [0.5, 0, 0, 0, 0, 0, 1, 1, 1]
        self.left_motor = Motor(engines[0])
        self.right_motor = Motor(engines[1])
        self.driving_motors = MotorPair(engines[0], engines[1])
        self.drive_shaft = Motor(engines[2])
        self.gear_selector = Motor(engines[3])
        self.front_light_sensor = ColorSensor(light_sensors[0])
        self.back_light_sensor = ColorSensor(light_sensors[1])
        self.p_correction_gyro_drive = correction_values[0]
        self.i_correction_gyro_drive = correction_values[1]
        self.d_correction_gyro_drive = correction_values[2]
        self.p_correction_line_follower = correction_values[6]
        self.i_correction_line_follower = correction_values[7]
        self.d_correction_line_follower = correction_values[8]
        self.p_correction_gyro_turn = correction_values[3]
        self.i_correction_gyro_turn = correction_values[4]
        self.d_correction_gyro_turn = correction_values[5]
        self.selected_gear = 1
        self.timer = __Timer()
        self.tire_radius = tire_radius
        self.light_black_value = light_black_value
        self.light_middle_value = light_middle_value
        self.brick = brick
        self.turning_degree_tolerance = turning_degree_tolerance
        self.acceleration_counter = 0
        self.deceleration_counter = 0
        self.attachment_started = False
        self.attachment_stopped = False
        self.brick.motion_sensor.reset_yaw_angle()
        self.debug_mode = debug_mode
        self.display_as = display_as

        if self.debug_mode:
            PrimeHub().speaker.beep(60, 0.2)
            PrimeHub().speaker.beep(80, 0.2)
            PrimeHub().speaker.beep(60, 0.2)
            PrimeHub().speaker.beep(80, 0.2)

        self.check_battery()

        # Resetting Gyro-Sensor and Transmission
        self.gear_selector.set_stall_detection(True)
        self.gear_selector.set_stop_action("brake")
        if (
            self.gear_selector.get_position() <= 90
            or self.gear_selector.get_position() >= 270
        ):
            self.gear_selector.run_to_position(0, "shortest path", _100)
        else:
            self.gear_selector.run_to_position(0, "counterclockwise", _100)
        self.select_gear(hold_attachment)

    def check_battery(self):
        """
        Check if the battery is low and raise an error if it is below 100%.
        Only ran when in debug mode.
        """

        if not self.debug_mode:
            return
        if hub.battery.capacity_left() < 100:
            raise BatteryLowError("Battery capacity got below 100%")

    def select_gear(self, target_gear: int):
        """
        Gear Selection

        Parameters:
        targetGear: Wanted Gear (4:Front-Left, 3:Back-Left, 1:Front-Right, 2:Back-Right)
        """
        self.check_battery()
        # Turn gearSelector until right gear is selected
        try:
            if self.selected_gear < target_gear:
                self.gear_selector.run_to_position(
                    int(58 * (target_gear - 1)), "clockwise", 100
                )
            elif self.selected_gear > target_gear:
                self.gear_selector.run_to_position(
                    int(58 * (target_gear - 1)), "counterclockwise", 100
                )
            self.selected_gear = target_gear
        except KeyboardInterrupt as e2:
            self.gear_selector.set_stall_detection(True)
            self.select_gear(target_gear=target_gear)
            self.gear_selector.set_stall_detection(False)
            raise e2

    def drive_attachment(
        self,
        attachment_index: int,
        speed: int,
        resistance: bool = False,
        duration: float = 0,
        degree: float = 0,
    ):
        """
        Driving a chosen attachment, either for given time/distance or passively in the background

        Parameters:
        attachmentIndex: Position of Attachment
        speed: Speed of Motor
        duration: Duration of Movement in Seconds
        degree: Distance of Movement in Degrees
        resistance: Move until hitting resistance
        """
        self.check_battery()
        # Stop possible movement, select chosen gear
        self.drive_shaft.stop()
        self.select_gear(attachment_index)
        # If a duration is given, run the attachement for the given time
        if duration != 0:
            self.drive_shaft.run_for_seconds(duration, speed)
        # If a degree is given, run the attachement until the degree is reached
        elif degree != 0:
            self.drive_shaft.run_for_degrees(
                int(degree * (speed / fabs(speed))), int(fabs(speed))
            )
        # If neither are given, run the attachement forever or until it gets resistance
        else:
            self.drive_shaft.start(speed)
            if resistance:
                self.drive_shaft.set_stall_detection(True)
                wait_until(self.drive_shaft.was_stalled)
                self.drive_shaft.stop()
                self.drive_shaft.set_stall_detection(False)

    def stop_attachment(self):
        """Stop attachment drive"""
        # Stop possible movement
        self.check_battery()
        self.drive_shaft.stop()

    def reset_timer_and_ending_condition(self):
        """
        Resets Ending Conditions and Timer
        """
        # Reset all timers, motors and counters
        self.timer.reset()
        self.left_motor.set_degrees_counted(0)
        self.right_motor.set_degrees_counted(0)
        self.acceleration_counter = 0
        self.deceleration_counter = 0
        self.attachment_started = False
        self.attachment_stopped = False

    def calculate_acceleration(self, speed: float, duration: float):
        """
        Calculate Acceleration

        Parameters:
        speed: given speed
        duration: time of acceleration
        """
        # Given the target-speed and the progress X, the function returns the target-speed*(X/50)
        # If another 1/50 is reached, the progress-counter is increased
        if self.acceleration_counter < 50:
            if self.timer.now() >= ((self.acceleration_counter * duration) / 50):
                self.acceleration_counter += 1
            return (speed * self.acceleration_counter) / 50
        return int(speed)

    def calculate_deceleration(self, speed: int):  # , distance: float):
        """
        Calculate Deceleration

        Parameters:
        speed: given speed
        endSpeed: final speed to finish on
        distane: distance of deceleration
        """
        # Given the target-speed and the progress X,
        # the function returns the target-speed*((50-X)/50)
        # If another 1/50 is reached, the progress-counter is increased
        if (
            (
                (
                    self.right_motor.get_degrees_counted()
                    + self.right_motor.get_degrees_counted()
                )
                / 720
            )
        ) >= fabs(
            (self.deceleration_counter / 50)
        ):  # missing distance
            self.deceleration_counter += 1
        return int((speed * (50 - self.deceleration_counter)) / 50)

    def gyro_drive(
        self,
        speed: int,
        degree: int,
        ending_condition: EndingCondition,
        p_correction: int = 0,
        i_correction: int = 0,
        d_correction: int = 0,
        acceleration: int = 0,
        deceleration: int = 0,
        attachment_start: list[int] = None,
        attachment_stop: int = 0,
        speed_multiplier_right: int = 1,
        speed_multiplier_left: int = 1,
    ):
        """
        PID Gyro-Drive

        Parameters:
        speed: Topspeed of robot
        degree: Targetdegree
        p_correction: P-Correction-Value
        i_correction: I-Correction-Value
        d_correction: D-Correction-Value
        ending_condition: Ending Condition
        acceleration: Time for Acceleration
        deceleration: Distance for Deceleration
        attachmentStart: List of Index of Attachment, Time until Start and Speed
        attachmentStop: Time until Stop of Attachment
        speed_multiplier_left: Factor to multiply speed by on left side.
        speed_multiplier_right: Factor to multiply speed by on right side.
        """
        self.check_battery()
        # Resetting everything
        if attachment_start is None:
            attachment_start = [0, 0, 0]
        self.reset_timer_and_ending_condition()
        last_error = 0
        integral = 0
        speed = -speed
        attachment_started = False
        attachment_stopped = False
        if p_correction == 0:
            p_correction = self.p_correction_gyro_drive
        if i_correction == 0:
            i_correction = self.i_correction_gyro_drive
        if d_correction == 0:
            d_correction = self.d_correction_gyro_drive
        if deceleration != 0:
            ending_value = ending_value - deceleration
        if not isinstance(ending_condition, EndingCondition):
            raise WrongUnitError(
                type(ending_condition) + " cannot be used as an EndingCondititon."
            )
        degree = degree - 360 * floor((degree + 180) / 360)
        if isinstance(ending_condition, Deg):
            ending_condition.value = ending_condition.value - 360 * floor(
                (degree + 180) / 360
            )
        # If an Attachement is started or stopped during the movement, start this loop
        if attachment_start[1] != 0 or attachment_stop != 0:
            while not ending_condition.check(self):
                # The new sensor value is retreaved and the error-value calculated
                error_value = degree - self.brick.motion_sensor.get_yaw_angle()

                # This works now. I don't know what you were doing here before!!!!
                if error_value > 180:
                    error_value -= 360
                if error_value <= -180:
                    error_value += 360
                # The necessary values for the PID-Controller get calculated
                differential = error_value - last_error
                integral += error_value
                corrector = (
                    integral * i_correction
                    + differential * d_correction
                    + error_value * p_correction
                )
                last_error = error_value
                # The robot corrects according to the PID-Controller and Acceleration
                self.driving_motors.start_tank(
                    int(
                        self.calculate_acceleration(speed + corrector, acceleration)
                        * speed_multiplier_left
                    ),
                    int(
                        self.calculate_acceleration(speed - corrector, acceleration)
                        * speed_multiplier_right
                    ),
                )
                # If an attachementStart is planned, check the timer and start the Attachement
                if (
                    attachment_start[1] != 0
                    and not attachment_started
                    and self.timer.now() >= attachment_start[1]
                ):
                    self.drive_attachment(attachment_start[0], attachment_start[2])
                    attachment_started = True
                # If an atachementStop is planned, check the timer and stop the Attachement
                if (
                    attachment_stop != 0
                    and not attachment_stopped
                    and self.timer.now() >= attachment_stop
                ):
                    self.stop_attachment()
                    attachment_stopped = True
        # If there won't be any Attachement use, start this loop
        else:
            while not ending_condition.check(self):
                # The new sensor value is retreaved and the error-value calculated
                error_value = degree - self.brick.motion_sensor.get_yaw_angle()

                # This works now. I don't know what you were doing here before!!!!
                if error_value > 180:
                    error_value -= 360
                if error_value <= -180:
                    error_value += 360
                # The necessary values for the PID-Controller get calculated
                differential = error_value - last_error
                integral += error_value
                corrector = (
                    integral * i_correction
                    + differential * d_correction
                    + error_value * p_correction
                )
                last_error = error_value
                # The robot corrects according to the PID-Controller
                self.driving_motors.start_tank(
                    int(
                        self.calculate_acceleration(speed + corrector, acceleration)
                        * speed_multiplier_left
                    ),
                    int(
                        self.calculate_acceleration(speed - corrector, acceleration)
                        * speed_multiplier_right
                    ),
                )
        # If deceleration is wanted, stop the above loops early to start decelerating
        # The PID-Loop stays the same,
        # the speed only gets decelerated before being put into the motors
        if deceleration != 0:
            while self.deceleration_counter <= 50:
                error_value = degree - self.brick.motion_sensor.get_yaw_angle()
                if abs(error_value) > 180:
                    error_value -= 360
                differential = error_value - last_error
                integral += error_value
                corrector = (
                    integral * i_correction
                    + differential * d_correction
                    + error_value * p_correction
                )
                last_error = error_value
                self.driving_motors.start_tank(
                    self.calculate_deceleration(speed + corrector),
                    self.calculate_deceleration(speed - corrector),
                )
        # The motors come to a full-stop
        self.driving_motors.stop()

    def gyro_turn(
        self,
        degree: int,
        ending_condition: EndingCondition = EndingCondition(),
        p_correction: int = 0,
        i_correction: int = 0,
        d_correction: int = 0,
        attachment_start: list[int] = None,
        attachment_stop: int = 0,
        speed_multiplier: float = 1,
        speed_multiplier_left: float = 1,
        speed_multiplier_right: float = 1,
    ):
        """
        PID-Gyro-Tank-Turn

        Parameters:
        degree: Targetdegree
        ending_condition: Ending Condition to force stop
        p_correction: P-Correction-Value
        i_correction: I-Correction-Value
        d_correction: D-Correction-Value
        attachmentStart: List of Index of Attachment, Time until Start and Speed
        attachmentStop: Time until Stop of Attachment
        speed_multiplier: Factor to multiply speed by.
        speed_multiplier_left: Factor to multiply speed by on left side.
        speed_multiplier_right: Factor to multiply speed by on right side.
        """
        self.check_battery()

        speed_multiplier_left = speed_multiplier * speed_multiplier_left
        speed_multiplier_right = speed_multiplier * speed_multiplier_right

        # Resetting everything
        if attachment_start is None:
            attachment_start = [0, 0, 0]
        self.reset_timer_and_ending_condition()
        last_error = 0
        integral = 0
        attachment_started = False
        attachment_stopped = False
        if p_correction == 0:
            p_correction = self.p_correction_gyro_turn
        if i_correction == 0:
            i_correction = self.i_correction_gyro_turn
        if d_correction == 0:
            d_correction = self.d_correction_gyro_turn
        degree = degree - 360 * floor((degree + 180) / 360)
        # If an Attachement is started or stopped during the movement, start this loop
        # The following code is completely useless (inside the if block),
        # but we have it and i wont remove it.
        if attachment_start[1] != 0 or attachment_stop != 0:
            while (
                not degree - self.turning_degree_tolerance
                < self.brick.motion_sensor.get_yaw_angle()
                < degree + self.turning_degree_tolerance
            ) and not ending_condition.check(self):
                # The new sensor value is retreaved and the error-value calculated
                error_value = degree - self.brick.motion_sensor.get_yaw_angle()

                # This works now. I don't know what you were doing here before!!!!
                if error_value > 180:
                    error_value -= 360
                if error_value <= -180:
                    error_value += 360
                # The necessary values for the PID-Controller get calculated
                differential = error_value - last_error
                integral += last_error
                # The robot corrects according to the PID-Controller
                corrector = (
                    integral * i_correction
                    + differential * d_correction
                    + error_value * p_correction
                )
                last_error = error_value
                # If an attachementStart is planned, check the timer and start the Attachement
                self.driving_motors.start_tank(
                    round((attachment_start[2] - corrector) * speed_multiplier_left),
                    round((attachment_start[2] + corrector) * speed_multiplier_right),
                )
                # If an attachementStart is planned, check the timer and start the Attachement
                if (
                    attachment_start[1] != 0
                    and not attachment_started
                    and self.timer.now() >= attachment_start[1]
                ):
                    self.drive_attachment(attachment_start[0], attachment_start[2])
                    attachment_started = True
                # If an atachementStop is planned, check the timer and stop the Attachement
                if (
                    attachment_stop != 0
                    and not attachment_stopped
                    and self.timer.now() >= attachment_stop
                ):
                    self.stop_attachment()
                    attachment_stopped = True
        # If there won't be any Attachement use, start this loop
        else:
            while (
                not degree - self.turning_degree_tolerance
                <= self.brick.motion_sensor.get_yaw_angle()
                <= degree + self.turning_degree_tolerance
            ) and not ending_condition.check(self):
                # The new sensor value is retreaved and the error-value
                error_value = degree - self.brick.motion_sensor.get_yaw_angle()

                # This works now. I don't know what you were doing here before!!!!
                if error_value > 180:
                    error_value -= 360
                if error_value <= -180:
                    error_value += 360
                # The necessary values for the PID-Controller get calculated
                differential = error_value - last_error
                integral += last_error
                corrector = (
                    integral * i_correction
                    + differential * d_correction
                    + error_value * p_correction
                )
                last_error = error_value
                # The robot corrects according to the PID-Controller
                self.driving_motors.start_tank(
                    round(int(corrector) * speed_multiplier_left),
                    round(int(-corrector) * speed_multiplier_right),
                )
        # The motors come to a full-stop
        self.driving_motors.stop()

    def line_follower(
        self,
        speed: int,
        front_sensor: bool,
        ending_condition: int,
        left_of_line: bool = True,
        p_correction: int = 0,
        i_correction: int = 0,
        d_correction: int = 0,
        attachment_start: list[int] = None,
        attachment_stop: int = 0,
    ):
        """
        PID-Linefollower

        Parameters:
        speed: Speed of Turn
        frontSensor: Use of front sensor
        leftOfLine: Drive left of Line
        ending_condition: Ending Condition
        p_correction: P-Correction-Value
        i_correction: I-Correction-Value
        d_correction: D-Correction-Value
        attachmentStart: List of Index of Attachment, Time until Start and Speed
        attachmentStop: Time until Stop of Attachment
        """
        self.check_battery()
        # Resetting everything
        if attachment_start is None:
            attachment_start = [0, 0, 0]
        self.reset_timer_and_ending_condition()
        last_error = 0
        integral = 0
        speed = -speed
        attachment_started = False
        attachment_stopped = False
        if p_correction == 0:
            p_correction = self.p_correction_line_follower
        if i_correction == 0:
            i_correction = self.i_correction_line_follower
        if d_correction == 0:
            d_correction = self.d_correction_line_follower
        light_sensor = (
            self.front_light_sensor if front_sensor else self.back_light_sensor
        )
        if left_of_line:
            left_factor = -1
        else:
            left_factor = 1
        # If an atachementStop is planned, check the timer and stop the Attachement
        if attachment_start[1] != 0 or attachment_stop != 0:
            while not ending_condition.check(self):
                # The new sensor value is retreaved and the error-value calculated
                error_value = left_factor * (
                    light_sensor.get_reflected_light() - self.light_middle_value
                )
                # The necessary values for the PID-Controller get calculated
                differential = error_value - last_error
                integral += last_error
                corrector = (
                    integral * i_correction
                    + differential * d_correction
                    + error_value * p_correction
                )
                last_error = error_value
                # The robot corrects according to the PID-Controller
                self.driving_motors.start_tank(speed - corrector, speed + corrector)
                # If an attachementStart is planned, check the timer and start the Attachement
                if not attachment_started and self.timer.now() >= attachment_start[1]:
                    self.drive_attachment(attachment_start[0], attachment_start[2])
                    attachment_started = True
                # If an atachementStop is planned, check the timer and stop the Attachement
                if not attachment_stopped and self.timer.now() >= attachment_stop:
                    self.stop_attachment()
                    attachment_stopped = True
        # If there won't be any Attachement use, start this loop
        else:
            while not ending_condition.check(self):
                error_value = left_factor * (
                    light_sensor.get_reflected_light() - self.light_middle_value
                )
                differential = error_value - last_error
                integral += last_error
                corrector = (
                    integral * i_correction
                    + differential * d_correction
                    + error_value * p_correction
                )
                last_error = error_value
                self.driving_motors.start_tank(speed - corrector, speed + corrector)
                if (
                    attachment_start[1] != 0
                    and not attachment_started
                    and self.timer.now() >= attachment_start[1]
                ):
                    self.drive_attachment(attachment_start[0], attachment_start[2])
                    attachment_started = True
                if (
                    attachment_stop != 0
                    and not attachment_stopped
                    and self.timer.now() >= attachment_stop
                ):
                    self.stop_attachment()
                    attachment_stopped = True
        self.driving_motors.stop()


class MasterControlProgram:
    """Master Control Program managing and starting all runs"""

    def __init__(self, brick: PrimeHub, **defaults) -> None:
        """
        init Master Control Program

        parameters:
        brick: Brick of Robot
        """
        self.runs: list[tuple[callable, dict[str, any]]] = []
        self.brick: PrimeHub = brick
        self.defaults = defaults

    def run(self, **defaults):
        """Decorator for a run"""

        def decorator(func):
            self.runs.append((func, defaults))
            return func

        return decorator

    def light_up_display(self, brick: PrimeHub, number: int, max_number: int):
        """Show number on display with styled lines"""
        brightness_70 = const(70)
        if number - 1 < max_number:
            display_as = self.runs[number - 1][1].get("display_as", number)
        else:
            display_as = number
        if display_as == "X":
            brick.light_matrix.off()
            brick.light_matrix.set_pixel(1, 0, brightness=_100)
            brick.light_matrix.set_pixel(1, 1, brightness=_100)
            brick.light_matrix.set_pixel(1, 3, brightness=_100)
            brick.light_matrix.set_pixel(1, 4, brightness=_100)
            brick.light_matrix.set_pixel(2, 2, brightness=_100)
            brick.light_matrix.set_pixel(3, 0, brightness=_100)
            brick.light_matrix.set_pixel(3, 1, brightness=_100)
            brick.light_matrix.set_pixel(3, 3, brightness=_100)
            brick.light_matrix.set_pixel(3, 4, brightness=_100)
        elif display_as == "C":
            brick.light_matrix.off()
            brick.light_matrix.set_pixel(1, 1, brightness=_100)
            brick.light_matrix.set_pixel(1, 2, brightness=_100)
            brick.light_matrix.set_pixel(1, 3, brightness=_100)
            brick.light_matrix.set_pixel(2, 0, brightness=_100)
            brick.light_matrix.set_pixel(2, 4, brightness=_100)
            brick.light_matrix.set_pixel(3, 0, brightness=_100)
            brick.light_matrix.set_pixel(3, 4, brightness=_100)
        elif display_as == "T":
            brick.light_matrix.off()
            brick.light_matrix.set_pixel(1, 0, brightness=_100)
            brick.light_matrix.set_pixel(2, 0, brightness=_100)
            brick.light_matrix.set_pixel(2, 1, brightness=_100)
            brick.light_matrix.set_pixel(2, 2, brightness=_100)
            brick.light_matrix.set_pixel(2, 3, brightness=_100)
            brick.light_matrix.set_pixel(2, 4, brightness=_100)
            brick.light_matrix.set_pixel(3, 0, brightness=_100)
        elif display_as == "R":
            brick.light_matrix.off()
            brick.light_matrix.set_pixel(1, 0, brightness=_100)
            brick.light_matrix.set_pixel(1, 1, brightness=_100)
            brick.light_matrix.set_pixel(1, 2, brightness=_100)
            brick.light_matrix.set_pixel(1, 3, brightness=_100)
            brick.light_matrix.set_pixel(1, 4, brightness=_100)
            brick.light_matrix.set_pixel(2, 0, brightness=_100)
            brick.light_matrix.set_pixel(3, 4, brightness=_100)
            brick.light_matrix.set_pixel(3, 1, brightness=_100)
            brick.light_matrix.set_pixel(2, 2, brightness=_100)
            brick.light_matrix.set_pixel(3, 3, brightness=_100)
        elif display_as == "D":
            brick.light_matrix.off()
            brick.light_matrix.set_pixel(1, 0, brightness=_100)
            brick.light_matrix.set_pixel(1, 1, brightness=_100)
            brick.light_matrix.set_pixel(1, 2, brightness=_100)
            brick.light_matrix.set_pixel(1, 3, brightness=_100)
            brick.light_matrix.set_pixel(1, 4, brightness=_100)
            brick.light_matrix.set_pixel(2, 0, brightness=_100)
            brick.light_matrix.set_pixel(2, 4, brightness=_100)
            brick.light_matrix.set_pixel(3, 1, brightness=_100)
            brick.light_matrix.set_pixel(3, 2, brightness=_100)
            brick.light_matrix.set_pixel(3, 3, brightness=_100)
        elif number == max_number + 1:
            brick.light_matrix.off()
            brick.light_matrix.set_pixel(1, 1, brightness=_100)
            brick.light_matrix.set_pixel(2, 2, brightness=_100)
            brick.light_matrix.set_pixel(3, 3, brightness=_100)

            brick.light_matrix.set_pixel(1, 3, brightness=_100)
            brick.light_matrix.set_pixel(3, 1, brightness=_100)

            brick.light_matrix.set_pixel(0, 1, brightness=brightness_70)
            brick.light_matrix.set_pixel(0, 3, brightness=brightness_70)
            brick.light_matrix.set_pixel(4, 1, brightness=brightness_70)
            brick.light_matrix.set_pixel(4, 3, brightness=brightness_70)
            brick.light_matrix.set_pixel(0, 4, brightness=brightness_70)
            brick.light_matrix.set_pixel(0, 0, brightness=brightness_70)
            brick.light_matrix.set_pixel(0, 2, brightness=brightness_70)
            brick.light_matrix.set_pixel(4, 0, brightness=brightness_70)
            brick.light_matrix.set_pixel(4, 2, brightness=brightness_70)
            brick.light_matrix.set_pixel(4, 4, brightness=brightness_70)
        elif isinstance(display_as, int):
            brick.light_matrix.write(display_as)
        else:
            brick.light_matrix.write(number)
        brick.light_matrix.set_pixel(0, 1, brightness=brightness_70)
        brick.light_matrix.set_pixel(0, 3, brightness=brightness_70)
        brick.light_matrix.set_pixel(4, 1, brightness=brightness_70)
        brick.light_matrix.set_pixel(4, 3, brightness=brightness_70)
        if number == 1:
            brick.light_matrix.set_pixel(0, 4, brightness=brightness_70)
            brick.light_matrix.set_pixel(0, 0, brightness=brightness_70)
            brick.light_matrix.set_pixel(0, 2, brightness=brightness_70)
        if number == max_number:
            brick.light_matrix.set_pixel(4, 0, brightness=brightness_70)
            brick.light_matrix.set_pixel(4, 2, brightness=brightness_70)
            brick.light_matrix.set_pixel(4, 4, brightness=brightness_70)

    def start_run(self, run, **defaults):
        """Start a run by ID

        Args:
            run (int): Run-ID

        Returns:
            Any: Result of run-func
        """
        run_entry = self.runs[run - 1]
        defargs = {}
        defargs.update(self.defaults)
        defargs.update(defaults)
        defargs.update(run_entry[1])
        print("Starting Run {}".format(run))  # pylint: disable=consider-using-f-string
        result = run_entry[0](Run(self.brick, **defargs))
        print("Run {} ended".format(run))  # pylint: disable=consider-using-f-string
        return result

    def turn_light_off(self):
        """
        Turn the light of all color sensors off.
        """
        for x in ["A", "B", "C", "D", "E", "F"]:
            try:
                ColorSensor(x).light_up_all(0)
            except RuntimeError:
                pass

    def start(
        self,
        engines: list[str] = None,
        light_sensors: list[str] = None,
        correction_values: list[float] = None,
        tire_radius: float = 2.3,
        light_black_value: int = 10,
        light_middle_value: int = 50,
        turning_degree_tolerance: int = 2,
        no_debug_menu: bool = False,
    ):
        """
        start Master Control Program

        parameters:
        brick: Brick of Robot
        brick: The Brick of the Robot
        engines: List of Motors (Left, Right, Driveshaft, Gearselector)
        lightSensors: List of Lightsensors (Front, Back)
        correctionValues: List of Correction Values (GyroDrive (p,i,d),
                            LineFollower (p,i,d), GyroTurn (p,i,d))
        tireRadius: Radius of the Robots tires
        lightBlackValue: The Lightvalue of Black
        lightMiddleValue: The middle Lightvalue between Black and White
        turningDegreeTolerance: Tolerance when turning for a degree
        no_debug_menu: Whether to disable the debug menu
        """
        if engines is None:
            engines = ["D", "C", "F", "E"]
        if light_sensors is None:
            light_sensors = ["A", "B"]
        if correction_values is None:
            correction_values = [0.5, 0, 0, 0, 0, 0, 0, 0, 0]
        selected_run = 1
        print("Starting MasterControl")
        self.turn_light_off()
        self.light_up_display(self.brick, selected_run, len(self.runs))
        while True:
            # It checks for button presses to increase, decrease or start the chosen run
            try:
                while True:
                    if (
                        not no_debug_menu
                        and self.brick.left_button.is_pressed()
                        and self.brick.right_button.is_pressed()
                    ):
                        raise EnterDebugMenu()
                    if self.brick.left_button.is_pressed():
                        time_ = 0
                        while self.brick.left_button.is_pressed() and time_ < 3:
                            time_ += 1
                            wait_for_seconds(0.1)
                        if selected_run > 1:
                            selected_run -= 1
                            self.light_up_display(
                                self.brick, selected_run, len(self.runs)
                            )
                    if self.brick.right_button.is_pressed():
                        time_ = 0
                        while self.brick.right_button.is_pressed() and time_ < 3:
                            time_ += 1
                            wait_for_seconds(0.1)
                        if selected_run < len(self.runs) + 1:
                            selected_run += 1
                            self.light_up_display(
                                self.brick, selected_run, len(self.runs)
                            )
            except KeyboardInterrupt as err:
                if selected_run == len(self.runs) + 1:
                    raise SystemExit from err
                try:
                    # Starting the Runs
                    self.start_run(
                        selected_run,
                        engines=engines,
                        light_sensors=light_sensors,
                        correction_values=correction_values,
                        tire_radius=tire_radius,
                        light_black_value=light_black_value,
                        light_middle_value=light_middle_value,
                        turning_degree_tolerance=turning_degree_tolerance,
                    )
                    if not DEBUG_MODE:
                        selected_run += 1
                    self.turn_light_off()
                except KeyboardInterrupt:
                    print("Run stopped forcefully")
                    for port in ["A", "B", "C", "D", "E", "F"]:
                        try:
                            Motor(port).stop()
                        except RuntimeError:
                            pass
                self.light_up_display(self.brick, selected_run, len(self.runs))


mcp = MasterControlProgram(PrimeHub(), debug_mode=DEBUG_MODE)

timer = __Timer()
timer.reset()


@mcp.run()
def run_1(run: Run):
    """Giftschlange Run (Grün)"""
    timer.reset()
    run.gyro_drive(80, 0, ending_condition=Cm(39), p_correction=1.2)
    wait_for_seconds(1)
    # run.gyro_turn(20, p_correction=1, speed_multiplier=1.2)
    run.gyro_turn(45, p_correction=1)
    # Pult gelöst
    run.gyro_drive(-50, 45, ending_condition=Cm(3.25), p_correction=1.2)
    run.gyro_turn(135, p_correction=0.7, speed_multiplier=1.7)
    wait_for_seconds(1)
    run.gyro_drive(-80, 135, ending_condition=Cm(29.0), p_correction=1.2)
    run.gyro_turn(90, p_correction=0.9)
    # gleich heranfahren an Karusell
    run.gyro_drive(-45, 90, ending_condition=Cm(8))
    run.drive_attachment(BACK_RIGHT, -75, True, 1)
    run.drive_attachment(BACK_LEFT, 35, True, 2)
    run.gyro_drive(45, 90, ending_condition=Cm(7))
    run.gyro_turn(135, p_correction=1.4)
    # ab jetz Rückweg
    run.gyro_drive(80, 135, ending_condition=Cm(28), p_correction=1.2)
    run.gyro_turn(180, p_correction=1.4)
    run.gyro_drive(65, 180, ending_condition=Cm(35), p_correction=1.2)
    # run.drive_attachment(BACK_LEFT, 100, True, 2)


@mcp.run()
def run_2(run: Run):
    """Biene Mayo"""
    run.gyro_drive(70, 0, Cm(50.5), p_correction=1.2)
    run.drive_attachment(BACK_RIGHT, -_100, duration=3.1, resistance=True)
    # Einhaken
    run.select_gear(BACK_LEFT)
    run.gyro_drive(-50, 0, Cm(7), p_correction=1.2)
    run.gyro_turn(23, speed_multiplier=2, speed_multiplier_left=0, p_correction=2)
    run.gyro_drive(-50, 23, Cm(6), p_correction=1)
    run.gyro_turn(45, speed_multiplier_right=2, p_correction=2)
    run.drive_attachment(BACK_RIGHT, _100, duration=2.75)
    run.gyro_turn(0, speed_multiplier_left=0, p_correction=1)
    # Kamera abgesetz, weiterfahren
    run.gyro_drive(70, 0, Cm(19), p_correction=1)
    run.drive_attachment(FRONT_RIGHT, -100, duration=2.5)
    run.gyro_drive(70, 0, Cm(4), p_correction=1)
    run.drive_attachment(BACK_LEFT, -100, duration=0.75)
    run.gyro_drive(100, 0, Cm(12), p_correction=1.2)
    # Abbiegen zur Achterbahn
    # run.gyro_turn(35,p_correction=1.2)
    run.drive_attachment(FRONT_LEFT, 100, duration=1.5)
    run.gyro_drive(70, 10, Cm(15), p_correction=1.2)
    # run.gyro_turn(0, p_correction=1.2)
    run.gyro_drive(100, 10, Cm(65), p_correction=1.5)


@mcp.run()
def run_3(run: Run):
    """Third Part of Biene Mayo"""
    run.gyro_drive(80, 0, ending_condition=Cm(40), p_correction=3)
    run.gyro_drive(-100, 0, ending_condition=Cm(30), p_correction=3)


@mcp.run(turning_degree_tolerance=1)
def run_4(run: Run):
    """Tatütata Run (Rot)"""
    run.gyro_drive(speed=100, degree=0, ending_condition=Cm(18), p_correction=1.2)
    run.gyro_drive(speed=50, degree=0, ending_condition=Cm(11), p_correction=1.2)
    run.gyro_drive(speed=-70, degree=0, ending_condition=Cm(15), p_correction=1.2)
    # Druckerpresse reingeschoben, fahren zu Lichtshow
    run.gyro_turn(44, p_correction=0.9)
    run.gyro_drive(speed=90, degree=44, ending_condition=Cm(30), p_correction=1.2)
    run.gyro_drive(speed=50, degree=44, ending_condition=Cm(8), p_correction=1.2)
    run.drive_attachment(FRONT_RIGHT, 100, duration=1)
    run.gyro_drive(speed=-90, degree=44, ending_condition=Cm(10), p_correction=1.2)
    run.drive_attachment(FRONT_RIGHT, 100, duration=1.5)
    # Lichtshow aktiviert, fahren zu Turm
    run.gyro_turn(0, p_correction=0.9)
    run.gyro_drive(speed=90, degree=0, ending_condition=Cm(20.5), p_correction=1.2)
    run.gyro_turn(-45, p_correction=0.9)
    run.gyro_drive(speed=100, degree=-45, ending_condition=Cm(34), p_correction=1.2)
    run.gyro_drive(speed=70, degree=-45, ending_condition=Cm(10), p_correction=1.2)
    run.gyro_turn(45, p_correction=0.6, ending_condition=Sec(3))
    run.gyro_drive(speed=90, degree=45, ending_condition=Cm(20), p_correction=1)
    wait_for_seconds(1)
    run.drive_attachment(FRONT_LEFT, 100, duration=2.5)
    run.drive_attachment(FRONT_LEFT, -100, duration=2.5)
    run.drive_attachment(FRONT_RIGHT, -100, duration=1)
    # Roboter ist ausgerichtet
    if timer.now() < 130:
        run.gyro_drive(speed=-75, degree=45, ending_condition=Cm(25), p_correction=1.2)
        run.drive_attachment(BACK_RIGHT, -100, duration=12.5)
        # Turm hochgefahren
        run.gyro_drive(speed=90, degree=45, ending_condition=Sec(1.5), p_correction=1.2)
        # zurück gefahren
    else:
        run.gyro_drive(speed=-75, degree=45, ending_condition=Cm(12), p_correction=1.2)
        # Blume ermordet
        run.gyro_drive(speed=90, degree=45, ending_condition=Cm(12), p_correction=1.2)
    run.gyro_drive(speed=50, degree=45, ending_condition=Cm(1.5), p_correction=1.2)


@mcp.run(display_as="R")
def run_cleaning(run: Run):
    """Cleaning Wheels"""

    def run_for(sec, speed):
        run.driving_motors.start_at_power(speed, 0)
        wait_for_seconds(sec)

    # run_for(.1, 10)
    run_for(0.1, 30)
    run_for(0.1, 50)
    run_for(0.1, 60)
    run_for(0.2, 70)
    run_for(0.2, 80)
    run_for(0.3, 90)
    #    run_for(1, 100)
    run_for(3, 100)
    run_for(0.2, 90)
    run_for(0.2, 80)
    run_for(0.2, 70)
    run_for(0.2, 60)
    run_for(0.2, 50)
    run_for(0.2, 40)
    run_for(0.2, 30)
    run_for(0.2, 20)
    run_for(0.2, 10)

    run.driving_motors.stop()


@mcp.run(display_as="T", debug_mode=False)
def run_test(run: Run):
    """Run all attachment motors"""
    run.drive_attachment(1, _100, duration=1)
    run.drive_attachment(2, _100, duration=1)
    run.drive_attachment(3, _100, duration=1)
    run.drive_attachment(4, _100, duration=1)


@mcp.run(display_as="C", debug_mode=False)
def run_motorcontrol(run: Run):
    """Motorcontrol"""
    select = 1
    last_select = -1
    motor = FRONT_RIGHT
    try:
        while True:
            if run.brick.left_button.is_pressed():
                select -= 1
                run.brick.left_button.wait_until_released()
                wait_for_seconds(0.1)
            if run.brick.right_button.is_pressed():
                select += 1
                run.brick.right_button.wait_until_released()
                wait_for_seconds(0.1)
            if select < 1:
                select = 4
            if select > 4:
                select = 1
            if last_select != select:
                last_select = select
                # mcp.light_up_display(run.brick, motor, 4)
                mcp.brick.light_matrix.off()
                if select == 1:
                    mcp.brick.light_matrix.set_pixel(0, 0, _100)
                    motor = FRONT_LEFT
                if select == 2:
                    mcp.brick.light_matrix.set_pixel(4, 0, _100)
                    motor = FRONT_RIGHT
                if select == 3:
                    mcp.brick.light_matrix.set_pixel(0, 4, _100)
                    motor = BACK_LEFT
                if select == 4:
                    mcp.brick.light_matrix.set_pixel(4, 4, _100)
                    motor = BACK_RIGHT
    except KeyboardInterrupt:
        speed = _100
        is_inverted = motor in (BACK_RIGHT, FRONT_RIGHT)
        mcp.brick.light_matrix.off()
        mcp.brick.light_matrix.show_image("GO_RIGHT" if is_inverted else "GO_LEFT")
        try:
            while True:
                if (
                    run.brick.left_button.is_pressed()
                    and run.brick.right_button.is_pressed()
                ):
                    return
                if run.brick.right_button.is_pressed():
                    speed = _100
                    mcp.brick.light_matrix.show_image(
                        "GO_RIGHT" if is_inverted else "GO_LEFT"
                    )
                if run.brick.left_button.is_pressed():
                    speed = -_100
                    mcp.brick.light_matrix.show_image(
                        "GO_LEFT" if is_inverted else "GO_RIGHT"
                    )
        except KeyboardInterrupt:
            try:
                run.drive_attachment(motor, speed)
                while True:
                    wait_for_seconds(0.1)
            except KeyboardInterrupt:
                run.drive_shaft.stop()
                wait_for_seconds(1.0)


debug_menu = MasterControlProgram(PrimeHub())


@debug_menu.run(display_as="R")
def restart(run):  # pylint: disable=unused-argument
    """Restart the robot."""
    hub.power_off(True, True)


@debug_menu.run(display_as="D")
def enbug(run):  # pylint: disable=unused-argument
    """Disable debug menu."""
    mcp.defaults["debug_mode"] = False


while True:
    try:
        mcp.start()
    except BatteryLowError as e:
        mcp.brick.light_matrix.write("!")
        mcp.brick.speaker.beep(65, 1)
        raise e
    except EnterDebugMenu as e:
        try:
            debug_menu.start(no_debug_menu=True)
        except SystemExit:
            continue
    except Exception as e:
        mcp.brick.speaker.beep(65, 0.2)
        wait_for_seconds(0.1)
        mcp.brick.speaker.beep(70, 0.2)
        wait_for_seconds(0.1)
        mcp.brick.speaker.beep(75, 0.1)
        wait_for_seconds(0.1)
        mcp.brick.speaker.beep(80, 0.2)
        mcp.brick.light_matrix.write(str(e))
        raise e
