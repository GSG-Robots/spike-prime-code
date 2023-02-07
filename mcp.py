# LEGO type:standard slot:3 autostart
"""
Current Program, uses PEP8 conform names and has the new MasterControlProgram class
This is work in progress so there is no docstr on new elements.
"""
from math import fabs, floor, pi
from spike import PrimeHub, Motor, ColorSensor, MotorPair
from spike.control import wait_for_seconds, wait_until, Timer

FRONT_RIGHT = 3
FRONT_LEFT = 4
BACK_RIGHT = 1
BACK_LEFT = 2


class EndingCondition:
    def check(self, run):
        # this ugly thing is used because pylint wants me to use the run arg.
        return not bool(run)  # returns False, so it runs infinite.


class OrCond(EndingCondition):
    def __init__(
        self, condition_a: EndingCondition, condition_b: EndingCondition
    ) -> None:
        self.condition_a = condition_a
        self.condition_b = condition_b

    def check(self, run):
        return self.condition_a.check(run) or self.condition_b.check(run)


class AndCond(EndingCondition):
    def __init__(
        self, condition_a: EndingCondition, condition_b: EndingCondition
    ) -> None:
        self.condition_a = condition_a
        self.condition_b = condition_b

    def check(self, run):
        return self.condition_a.check(run) and self.condition_b.check(run)


class Cm(EndingCondition):
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
    def __init__(self, value: int) -> None:
        self.value = value

    def check(self, run):
        return run.timer.now() >= self.value


class Line(EndingCondition):
    def check(self, run):
        return (
            run.front_light_sensor.get_reflected_light() < run.light_black_value + 5
            or run.back_light_sensor.get_reflected_light() < run.light_black_value + 5
        )


class Deg(EndingCondition):
    def __init__(self, value: int) -> None:
        self.value = value

    def check(self, run):
        return (
            self.value - run.turning_degree_tolerance
            <= run.brick.motion_sensor.get_yaw_angle()
            <= self.value + run.turning_degree_tolerance
        )


class Run:
    def __init__(
        self,
        brick: PrimeHub,
        engines: list[str] = None,
        light_sensors: list[str] = None,
        correction_values: list[float] = None,
        tire_radius: float = 2.6,
        light_black_value: int = 10,
        light_middle_value: int = 50,
        turning_degree_tolerance: int = 2,
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
        """
        if engines is None:
            engines = ["D", "C", "B", "E"]
        if light_sensors is None:
            light_sensors = ["A", "F"]
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
        self.timer = Timer()
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
        if (
            self.gear_selector.get_position() <= 90
            or self.gear_selector.get_position() >= 270
        ):
            self.gear_selector.run_to_position(0, "shortest path", 100)
        else:
            self.gear_selector.run_to_position(0, "counterclockwise", 100)

    def select_gear(self, target_gear: int):
        """
        Gear Selection

        Parameters:
        targetGear: Wanted Gear (4:Front-Left, 3:Back-Left, 1:Front-Right, 2:Back-Right)
        """

        if self.selected_gear < target_gear:
            self.gear_selector.run_to_position(
                int(58 * (target_gear - 1)), "clockwise", 100
            )
        elif self.selected_gear > target_gear:
            self.gear_selector.run_to_position(
                int(58 * (target_gear - 1)), "counterclockwise", 100
            )
        self.selected_gear = target_gear

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
        self.drive_shaft.stop()
        self.select_gear(attachment_index)
        if duration != 0:
            self.drive_shaft.run_for_seconds(duration, speed)
        elif degree != 0:
            self.drive_shaft.run_for_degrees(
                int(degree * (speed / fabs(speed))), int(fabs(speed))
            )
        else:
            self.drive_shaft.start(speed)
            if resistance:
                self.drive_shaft.set_stall_detection(True)
                wait_until(self.drive_shaft.was_stalled)
                self.drive_shaft.stop()
                self.drive_shaft.set_stall_detection(False)

    def stop_attachment(self):
        """Stop attachment drive"""
        self.drive_shaft.stop()

    def reset_timer_and_ending_condition(self):
        """
        Resets Ending Conditions and Timer
        """
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
        if self.acceleration_counter < 50:
            if self.timer.now() >= ((self.acceleration_counter * duration) / 50):
                self.acceleration_counter += 1
            return (speed * self.acceleration_counter) / 50
        return int(speed)

    def calculate_deceleration(
        self, speed: int
    ):  # , end_speed: float, distance: float):
        """
        Calculate Deceleration

        Parameters:
        speed: given speed
        endSpeed: final speed to finish on
        distane: distance of deceleration
        """
        raise NotImplementedError("deceleration does not work")
        # if (
        #    (
        #        (
        #            self.right_motor.get_degrees_counted()
        #            + self.right_motor.get_degrees_counted()
        #        )
        #        / 720
        #    )
        # ) >= fabs((self.deceleration_counter * distance / 50)):
        #    self.deceleration_counter += 1
        # return int((speed * (50 - self.deceleration_counter)) / 50)

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
        """
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
        if deceleration:
            raise NotImplementedError("gyro drive cant do deceleraation")
        # ending_value = ending_value - deceleration
        degree = degree - 360 * floor((degree + 180) / 360)
        if isinstance(ending_condition, Deg):
            ending_condition.value = ending_condition.value - 360 * floor(
                (degree + 180) / 360
            )
        if attachment_start[1] != 0 or attachment_stop != 0:
            while not ending_condition.check(self):
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
                    int(self.calculate_acceleration(speed + corrector, acceleration)),
                    int(self.calculate_acceleration(speed - corrector, acceleration)),
                )
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
        else:
            while not ending_condition.check(self):
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
                    int(self.calculate_acceleration(speed + corrector, acceleration)),
                    int(self.calculate_acceleration(speed - corrector, acceleration)),
                )
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
        """
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
        if attachment_start[1] != 0 or attachment_stop != 0:
            while (
                not degree - self.turning_degree_tolerance
                < self.brick.motion_sensor.get_yaw_angle()
                < degree + self.turning_degree_tolerance
            ) and not ending_condition.check(self):
                error_value = degree - self.brick.motion_sensor.get_yaw_angle()
                if abs(error_value) > 180:
                    error_value -= 360
                differential = error_value - last_error
                integral += last_error
                corrector = (
                    integral * i_correction
                    + differential * d_correction
                    + error_value * p_correction
                )
                last_error = error_value
                self.driving_motors.start_tank(
                    attachment_start[2] - corrector, attachment_start[2] + corrector
                )
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
        else:
            while (
                not degree - self.turning_degree_tolerance
                <= self.brick.motion_sensor.get_yaw_angle()
                <= degree + self.turning_degree_tolerance
            ) and not ending_condition.check(self):
                error_value = degree - self.brick.motion_sensor.get_yaw_angle()
                if abs(error_value) > 180:
                    error_value -= 360
                differential = error_value - last_error
                integral += last_error
                corrector = (
                    integral * i_correction
                    + differential * d_correction
                    + error_value * p_correction
                )
                last_error = error_value
                self.driving_motors.start_tank(int(corrector), int(-corrector))
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
        if isinstance(ending_condition, Deg):
            raise NotImplementedError("Linefollower cant do deg.")
        # if ending_condition == 3:
        #    ending_value = ending_value - 360 * floor((degree + 180) / 360)
        light_sensor = (
            self.front_light_sensor if front_sensor else self.back_light_sensor
        )
        if left_of_line:
            left_factor = -1
        else:
            left_factor = 1
        if attachment_start[1] != 0 or attachment_stop != 0:
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
                if not attachment_started and self.timer.now() >= attachment_start[1]:
                    self.drive_attachment(attachment_start[0], attachment_start[2])
                    attachment_started = True
                if not attachment_stopped and self.timer.now() >= attachment_stop:
                    self.stop_attachment()
                    attachment_stopped = True
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

    def __init__(self, brick) -> None:
        """
        init Master Control Program

        parameters:
        brick: Brick of Robot
        """
        self.runs: list[tuple[callable, dict[str, any]]] = []
        self.brick = brick

    def run(self, **defaults):
        def decorator(func):
            self.runs.append((func, defaults))
            return func

        return decorator

    def light_up_display(self, brick: PrimeHub, number=int, max_number=int):
        brightness = 70
        brick.light_matrix.write(number)
        brick.light_matrix.set_pixel(0, 1, brightness=brightness)
        brick.light_matrix.set_pixel(0, 3, brightness=brightness)
        brick.light_matrix.set_pixel(4, 1, brightness=brightness)
        brick.light_matrix.set_pixel(4, 3, brightness=brightness)
        if number == 0:
            brick.light_matrix.off()
            brick.light_matrix.set_pixel(1, 1, brightness=100)
            brick.light_matrix.set_pixel(2, 2, brightness=100)
            brick.light_matrix.set_pixel(3, 3, brightness=100)

            brick.light_matrix.set_pixel(1, 3, brightness=100)
            brick.light_matrix.set_pixel(3, 1, brightness=100)

            brick.light_matrix.set_pixel(0, 1, brightness=brightness)
            brick.light_matrix.set_pixel(0, 3, brightness=brightness)
            brick.light_matrix.set_pixel(4, 1, brightness=brightness)
            brick.light_matrix.set_pixel(4, 3, brightness=brightness)
            brick.light_matrix.set_pixel(0, 4, brightness=brightness)
            brick.light_matrix.set_pixel(0, 0, brightness=brightness)
            brick.light_matrix.set_pixel(0, 2, brightness=brightness)
            brick.light_matrix.set_pixel(4, 0, brightness=brightness)
            brick.light_matrix.set_pixel(4, 2, brightness=brightness)
            brick.light_matrix.set_pixel(4, 4, brightness=brightness)
        if number == 1:
            brick.light_matrix.set_pixel(0, 4, brightness=brightness)
            brick.light_matrix.set_pixel(0, 0, brightness=brightness)
            brick.light_matrix.set_pixel(0, 2, brightness=brightness)
        if number == max_number:
            brick.light_matrix.set_pixel(4, 0, brightness=brightness)
            brick.light_matrix.set_pixel(4, 2, brightness=brightness)
            brick.light_matrix.set_pixel(4, 4, brightness=brightness)

    def start_run(self, run, **defaults):
        run_entry = self.runs[run - 1]
        defargs = {}
        defargs.update(defaults)
        defargs.update(run_entry[1])
        return run_entry[0](Run(self.brick, **defargs))

    def start(
        self,
        engines: list[str] = None,
        light_sensors: list[str] = None,
        correction_values: list[float] = None,
        tire_radius: float = 2.3,
        light_black_value: int = 10,
        light_middle_value: int = 50,
        turning_degree_tolerance: int = 2,
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
        """
        if engines is None:
            engines = ["D", "C", "B", "E"]
        if light_sensors is None:
            light_sensors = ["A", "F"]
        if correction_values is None:
            correction_values = [0.5, 0, 0, 0, 0, 0, 0, 0, 0]
        selected_run = 1
        print("Starting MC")
        self.light_up_display(self.brick, selected_run, len(self.runs))
        # while True:
        #    if self.brick.left_button.is_pressed():
        #        while True:
        #            if self.brick.right_button.is_pressed():
        #                self.brick.left_button.wait_until_released()
        #                self.brick.right_button.wait_until_released()
        #                print("Play run ", selected_run)
        #                self.start_run(
        #                    selected_run,
        #                    engines=engines,
        #                    light_sensors=light_sensors,
        #                    correction_values=correction_values,
        #                    tire_radius=tire_radius,
        #                    light_black_value=light_black_value,
        #                    light_middle_value=light_middle_value,
        #                    turning_degree_tolerance=turning_degree_tolerance,
        #                )
        #                if selected_run < len(self.runs):
        #                    selected_run += 1
        #                    self.light_up_display(
        #                        self.brick, selected_run, len(self.runs)
        #                    )
        #                break
        #            elif not self.brick.left_button.is_pressed():
        #                if selected_run > 1:
        #                    selected_run -= 1
        #                    self.light_up_display(
        #                        self.brick, selected_run, len(self.runs)
        #                    )
        #                break

        #    if self.brick.right_button.is_pressed():
        #        while True:
        #            if self.brick.left_button.is_pressed():
        #                self.brick.right_button.wait_until_released()
        #                self.brick.left_button.wait_until_released()
        #                print("Play run ", selected_run)
        #                self.start_run(
        #                    selected_run,
        #                    engines=engines,
        #                    light_sensors=light_sensors,
        #                    correction_values=correction_values,
        #                    tire_radius=tire_radius,
        #                    light_black_value=light_black_value,
        #                    light_middle_value=light_middle_value,
        #                    turning_degree_tolerance=turning_degree_tolerance,
        #                )
        #                if selected_run < len(self.runs):
        #                    selected_run += 1
        #                    self.light_up_display(
        #                        self.brick, selected_run, len(self.runs)
        #                    )
        #                break
        #            elif not self.brick.right_button.is_pressed():
        #                if selected_run < len(self.runs):
        #                    selected_run += 1
        #                    self.light_up_display(
        #                        self.brick, selected_run, len(self.runs)
        #                    )
        #                break
        # Nicht löschen, ich arbeite noch daran:
        while True:
            try:
                while True:
                    if self.brick.left_button.is_pressed():
                        self.brick.left_button.wait_until_released()
                        if selected_run > 0:
                            selected_run -= 1
                            self.light_up_display(
                                self.brick, selected_run, len(self.runs)
                            )
                    if self.brick.right_button.is_pressed():
                        self.brick.right_button.wait_until_released()
                        if selected_run < len(self.runs):
                            selected_run += 1
                            self.light_up_display(
                                self.brick, selected_run, len(self.runs)
                            )
            except KeyboardInterrupt as err:
                if selected_run == 0:
                    raise SystemExit from err
                try:
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
                except KeyboardInterrupt:
                    print("Run stopped")
                    for port in ["A", "B", "C", "D", "E", "F"]:
                        try:
                            Motor(port).stop()
                        except RuntimeError:
                            pass
                    continue


mcp = MasterControlProgram(PrimeHub())


@mcp.run()
def run_1(run1: Run):
    """Run 1"""
    print("Starting Run 1")
    run1.gyro_drive(speed=100, degree=0, ending_condition=Cm(32), p_correction=4)
    run1.gyro_drive(speed=50, degree=0, ending_condition=Cm(5), p_correction=4)
    run1.gyro_drive(speed=-100, degree=2, ending_condition=Cm(11), p_correction=4)
    run1.gyro_turn(degree=-40, p_correction=5)

    run1.gyro_drive(speed=100, degree=-48, ending_condition=Cm(37), p_correction=3)
    run1.gyro_turn(degree=29, p_correction=3)
    wait_for_seconds(0.5)

    run1.gyro_drive(speed=100, degree=32, ending_condition=Cm(28))
    run1.gyro_drive(speed=-50, degree=32, ending_condition=Cm(7))
    run1.gyro_drive(speed=100, degree=32, ending_condition=Cm(15))
    run1.gyro_drive(speed=-50, degree=32, ending_condition=Cm(11))
    run1.gyro_drive(speed=100, degree=32, ending_condition=Cm(22))

    run1.gyro_drive(speed=-80, degree=30, ending_condition=Cm(10))

    run1.gyro_turn(degree=-110, p_correction=2)
    run1.gyro_drive(speed=80, degree=30, ending_condition=Cm(3))
    run1.drive_attachment(FRONT_LEFT, speed=-100, duration=1)
    wait_for_seconds(0.5)

    run1.gyro_drive(speed=-80, degree=-110, ending_condition=Cm(3))
    run1.gyro_turn(degree=-185, p_correction=2)

    run1.gyro_drive(speed=100, degree=-185, ending_condition=Cm(40))
    print("Ended Run 1")


@mcp.run()
def run_2(run2: Run):
    """Run 2"""
    print("Starting Run 2")
    run2.gyro_drive(speed=-100, degree=-5, ending_condition=Cm(55))
    run2.gyro_drive(speed=-50, degree=-5, ending_condition=Cm(5))
    # run2.gyro_drive(speed=100, degree=-5, ending_condition=Cm(10))
    # run2.gyro_turn(degree=-15, p_correction=3)

    # run2.gyro_drive(
    #     speed=60, degree=-4, ending_condition=0, ending_value=66, p_correction=3
    # )
    # run2.gyro_drive(
    #     speed=-70,
    #     degree=5,
    #     ending_condition=1,
    #     ending_value=2,
    #     acceleration=2,
    #     p_correction=3,
    # )
    # wait_for_seconds(0.5)
    # run2.gyro_turn(degree=15, p_correction=2)
    # run2.gyro_drive(
    #     speed=20, degree=15, ending_condition=0, ending_value=2, p_correction=5
    # )
    # run2.gyro_turn(degree=30, p_correction=2)
    # run2.gyro_drive(
    #     speed=70, degree=30, ending_condition=0, ending_value=15, p_correction=5
    # )
    # run2.gyro_turn(degree=-20, p_correction=2)
    # run2.gyro_drive(
    #     speed=100, degree=-20, ending_condition=0, ending_value=90, p_correction=4
    # )

    # # ALIGNMENT

    # wait_for_seconds(0.8)
    # run2.gyro_turn(degree=90, p_correction=4)
    # run2.gyro_drive(speed=-50, degree=90, ending_condition=1, ending_value=1.2)


@mcp.run()
def run_3(run3: Run):
    """Run 3"""
    run3.gyro_drive(
        speed=60,
        degree=0,
        ending_condition=0,
        ending_value=10,
        acceleration=1,
        p_correction=0.4,
    )
    run3.drive_attachment(FRONT_RIGHT, 50, duration=1)
    run3.gyro_drive(speed=50, degree=0, ending_condition=0, ending_value=2.75)
    run3.gyro_turn(degree=30, p_correction=2)
    run3.gyro_drive(speed=40, degree=30, ending_condition=0, ending_value=8)
    run3.gyro_turn(degree=0, p_correction=1)
    run3.drive_attachment(FRONT_RIGHT, -70, duration=0.75)
    run3.gyro_drive(
        speed=35,
        degree=-3,
        ending_condition=0,
        ending_value=16,
        acceleration=1,
        p_correction=0.6,
    )
    run3.drive_attachment(BACK_RIGHT, -100, duration=1.5)
    run3.drive_attachment(BACK_RIGHT, 100, duration=1.5)
    run3.drive_attachment(BACK_RIGHT, -100, duration=1.5)
    run3.drive_attachment(BACK_RIGHT, 100, duration=1.5)
    run3.drive_attachment(BACK_RIGHT, -100, duration=1.5)
    run3.drive_attachment(BACK_RIGHT, 100, duration=1.5)

    run3.gyro_drive(
        speed=10, degree=-0.75, ending_condition=0, ending_value=10, p_correction=0.6
    )
    run3.drive_attachment(FRONT_RIGHT, 100, duration=1)
    wait_for_seconds(0.1)
    run3.gyro_drive(speed=-50, degree=0, ending_condition=1, ending_value=1.5)
    run3.gyro_turn(degree=30, p_correction=0.8)
    run3.gyro_drive(speed=-100, degree=30, ending_condition=1, ending_value=3.5)

    # ALIGNMENT
    wait_for_seconds(0.5)
    run3.gyro_turn(degree=85, p_correction=3)


@mcp.run()
def run_4(run4: Run):
    """Run 4"""
    run4.drive_attachment(FRONT_RIGHT, 100, duration=0.5)
    run4.gyro_drive(speed=100, degree=0, ending_condition=Cm(47), p_correction=5)
    run4.gyro_turn(degree=-35, p_correction=2)
    run4.gyro_drive(speed=100, degree=-35, ending_condition=Cm(30))
    run4.gyro_turn(degree=-87, p_correction=2)
    run4.gyro_drive(speed=100, degree=-87, ending_condition=Cm(30))
    run4.drive_attachment(FRONT_RIGHT, -100, duration=0.6)
    run4.gyro_drive(speed=-20, degree=-85, ending_condition=Cm(5))
    run4.drive_attachment(FRONT_RIGHT, 100, duration=0.5)
    run4.gyro_drive(speed=-20, degree=-85, ending_condition=Cm(7))
    run4.gyro_turn(degree=-130, p_correction=2)
    run4.gyro_drive(speed=-100, degree=-125, ending_condition=Cm(30))
    run4.gyro_drive(speed=100, degree=-125, ending_condition=Cm(25))
    run4.gyro_turn(degree=-90, p_correction=2)

    # run4.drive_attachment(FRONT_LEFT, 70, duration=0.75)
    # wait_for_seconds(0.25)
    # run4.gyro_turn(degree=-10, p_correction=1.5)
    # wait_for_seconds(0.25)
    # run4.gyro_drive(speed=65, degree=-10, ending_condition=0, ending_value=22)
    # run4.gyro_turn(degree=-87, p_correction=1)
    # wait_for_seconds(0.25)
    # run4.drive_attachment(FRONT_RIGHT, 70, duration=0.5)
    # run4.gyro_drive(speed=80, degree=-90, ending_condition=0, ending_value=31, p_correction=1.2)
    # run4.drive_attachment(FRONT_RIGHT, -70, duration=0.7)
    # wait_for_seconds(0.25)
    # run4.gyro_drive(speed=-15, degree=-90, ending_condition=1, ending_value=2.9)
    # wait_for_seconds(0.25)
    # run4.drive_attachment(FRONT_RIGHT, 70, duration=0.5)
    # run4.gyro_drive(speed=-35, degree=-90, ending_condition=1, ending_value=1.1)

    # SF:
    # run4.gyro_turn(degree=-130, p_correction=1.5)
    # run4.gyro_drive(speed=60, degree=-130, ending_condition=1, ending_value=2.3)
    # wait_for_seconds(0.25)
    # run4.gyro_drive(speed=-60, degree=-130, ending_condition=1, ending_value=2.3)
    # run4.gyro_turn(degree=-87, p_correction=1)

    # Auto:
    # run4.drive_attachment(1, -100, duration=1)
    # run4.gyro_turn(degree=-30, p_correction=1)
    # run4.gyro_drive(speed=-60, degree=-27, ending_condition=0, ending_value=20)
    # run4.drive_attachment(4, 70, duration=0.75)


mcp.start()