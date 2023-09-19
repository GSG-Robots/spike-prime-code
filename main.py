# LEGO type:standard slot:0 autostart
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
    """Ending Condition: Infinite and Base for other Ending Conditions"""

    def check(self, run):
        """Returns if the EndingCondition is fulfilled"""
        # this ugly thing is used because pylint wants me to use the run arg.
        return not bool(run)  # returns False, so it runs infinite.


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

    def __init__(self, value: int) -> None:
        self.value = value

    def check(self, run):
        return run.timer.now() >= self.value


class Line(EndingCondition):
    """Ending Condition: Line"""

    def check(self, run):
        return (
            run.front_light_sensor.get_reflected_light() < run.light_black_value + 5
            or run.back_light_sensor.get_reflected_light() < run.light_black_value + 5
        )


class Deg(EndingCondition):
    """Ending Condition: Degrees"""

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
        self.select_gear(hold_attachment)

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
                print(self.brick.motion_sensor.get_yaw_angle())
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

    def __init__(self, brick: PrimeHub) -> None:
        """
        init Master Control Program

        parameters:
        brick: Brick of Robot
        """
        self.runs: list[tuple[callable, dict[str, any]]] = []
        self.brick: PrimeHub = brick

    def run(self, **defaults):
        """Decorator for a run"""

        def decorator(func):
            self.runs.append((func, defaults))
            return func

        return decorator

    def light_up_display(self, brick: PrimeHub, number=int, max_number=int):
        """Show number on display with styled lines"""
        brightness = 70
        brick.light_matrix.write(number)
        brick.light_matrix.set_pixel(0, 1, brightness=brightness)
        brick.light_matrix.set_pixel(0, 3, brightness=brightness)
        brick.light_matrix.set_pixel(4, 1, brightness=brightness)
        brick.light_matrix.set_pixel(4, 3, brightness=brightness)
        if number == max_number + 1:
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
        """Start a run by ID

        Args:
            run (int): Run-ID

        Returns:
            Any: Result of run-func
        """
        run_entry = self.runs[run - 1]
        defargs = {}
        defargs.update(defaults)
        defargs.update(run_entry[1])
        print("Starting Run {}".format(run))  # pylint: disable=consider-using-f-string
        result = run_entry[0](Run(self.brick, **defargs))
        print("Ended Run {}".format(run))  # pylint: disable=consider-using-f-string
        return result

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
        while True:
            try:
                while True:
                    if self.brick.left_button.is_pressed():
                        # self.brick.left_button.wait_until_released()
                        time = 0
                        while self.brick.left_button.is_pressed() and time < 3:
                            time += 1
                            wait_for_seconds(0.1)
                        if selected_run > 1:
                            selected_run -= 1
                            self.light_up_display(
                                self.brick, selected_run, len(self.runs)
                            )
                    if self.brick.right_button.is_pressed():
                        # self.brick.right_button.wait_until_released()
                        time = 0
                        while self.brick.right_button.is_pressed() and time < 3:
                            time += 1
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
def run_1(run: Run):
    """Green Run"""
    run.gyro_drive(speed=100, degree=0, ending_condition=Cm(24), p_correction=4)
    run.gyro_turn(-45, p_correction=0.75)
    run.gyro_drive(speed=100, degree=-45, ending_condition=Cm(28), p_correction=2)
    run.gyro_turn(45, p_correction=.5)
    run.gyro_drive(speed=30, degree=45, ending_condition=Cm(11), p_correction=.5)
    run.drive_attachment(FRONT_RIGHT, -70, duration=1)
    run.gyro_drive(speed=-40, degree=45, ending_condition=Cm(13.5), p_correction=4)
    run.gyro_turn(42.5, p_correction=1)
    run.drive_attachment(BACK_LEFT, 100, duration=1)
    run.drive_attachment(BACK_LEFT, -100, duration=0.5)
    run.gyro_drive(speed=100, degree=45, ending_condition=Cm(5), p_correction=4)
    run.drive_attachment(BACK_LEFT, 100, duration=0.5)
    run.gyro_turn(-5, p_correction=1)
    run.gyro_drive(speed=-100, degree=-10, ending_condition=Cm(4), p_correction=4)
    run.gyro_turn(50, p_correction=1)
    run.gyro_turn(-25, p_correction=1)
    run.gyro_drive(speed=-100, degree=-25, ending_condition=Cm(75), p_correction=4)
    
    # reset (remove in prod)
    run.drive_attachment(BACK_LEFT, -100, duration=1)


@mcp.run()
def run_2(run: Run):
    """Blue Run"""
    run.drive_attachment(FRONT_LEFT, 50, duration=2)
    run.gyro_drive(speed=80, degree=0, ending_condition=Cm(37), p_correction=4)
    run.drive_attachment(FRONT_LEFT, -50, duration=2)
    run.gyro_drive(speed=-80, degree=0, ending_condition=Cm(10), p_correction=4)
    run.gyro_turn(-45, p_correction=1)
    run.gyro_drive(speed=80, degree=-45, ending_condition=Cm(2), p_correction=4)
    run.drive_attachment(FRONT_LEFT, 50, duration=2)
    run.gyro_drive(speed=-80, degree=-45, ending_condition=Cm(2), p_correction=4)
    run.gyro_turn(0, p_correction=1)
    run.gyro_drive(speed=-80, degree=0, ending_condition=Cm(24), p_correction=4)
    run.gyro_turn(-50, p_correction=1)
    run.gyro_drive(speed=80, degree=-50, ending_condition=Cm(32), p_correction=4)

@mcp.run()
def run_3(run: Run):
    """Red Run"""
    run.drive_attachment(FRONT_LEFT, 100, duration=2)
    run.drive_attachment(FRONT_LEFT, -100, duration=1)

@mcp.run()
def test(run: Run):  
    """Run all attachment motors"""
    run.drive_attachment(1, 100, duration=1)
    run.drive_attachment(2, 100, duration=1)
    run.drive_attachment(3, 100, duration=1)
    run.drive_attachment(4, 100, duration=1)

mcp.start()
