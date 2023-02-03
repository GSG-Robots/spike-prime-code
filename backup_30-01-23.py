# LEGO type:standard slot: 0 autostart

"""
backup of old master control program
"""

from math import fabs, floor, pi
from spike import PrimeHub, Motor, ColorSensor, MotorPair
from spike.control import wait_for_seconds, wait_until, Timer


print("Starting entire program")


FRONT_RIGHT = 3
FRONT_LEFT = 4
BACK_RIGHT = 1
BACK_LEFT = 2


class Run:
    def __init__(
        self,
        brick: PrimeHub,
        engines: list[str] = ["D", "C", "B", "E"],
        lightSensors: list[str] = ["A", "F"],
        correctionValues: list[float] = [0.5, 0, 0, 0, 0, 0, 1, 1, 1],
        tireRadius: float = 2.6,
        lightBlackValue: int = 10,
        lightMiddleValue: int = 50,
        turningDegreeTolerance: int = 2,
    ):
        """
        Initiation of Run

        Parameters:
        brick: The Brick of the Robot
        engines: List of Motors (Left, Right, Driveshaft, Gearselector)
        lightSensors: List of Lightsensors (Front, Back)
        correctionValues: List of Correction Values (GyroDrive (p,i,d), LineFollower (p,i,d), GyroTurn (p,i,d))
        tireRadius: Radius of the Robots tires
        lightBlackValue: The Lightvalue of Black
        lightMiddleValue: The middle Lightvalue between Black and White
        turningDegreeTolerance: Tolerance when turning for a degree
        """
        self.leftMotor = Motor(engines[0])
        self.rightMotor = Motor(engines[1])
        self.drivingMotors = MotorPair(engines[0], engines[1])
        self.driveShaft = Motor(engines[2])
        self.gearSelector = Motor(engines[3])
        self.frontLightSensor = ColorSensor(lightSensors[0])
        self.backLightSensor = ColorSensor(lightSensors[1])
        self.p_correctionGyroDrive = correctionValues[0]
        self.i_correctionGyroDrive = correctionValues[1]
        self.d_correctionGyroDrive = correctionValues[2]
        self.p_correctionLineFollower = correctionValues[6]
        self.i_correctionLineFollower = correctionValues[7]
        self.d_correctionLineFollower = correctionValues[8]
        self.p_correctionGyroTurn = correctionValues[3]
        self.i_correctionGyroTurn = correctionValues[4]
        self.d_correctionGyroTurn = correctionValues[5]
        self.selectedGear = 1
        self.timer = Timer()
        self.tireRadius = tireRadius
        self.lightBlackValue = lightBlackValue
        self.lightMiddleValue = lightMiddleValue
        self.brick = brick
        self.turningDegreeTolerance = turningDegreeTolerance
        self.accelerationCounter = 0
        self.decelerationCounter = 0
        self.attachmentStarted = False
        self.attachmentStopped = False
        self.brick.motion_sensor.reset_yaw_angle()
        if (
            self.gearSelector.get_position() <= 90
            or self.gearSelector.get_position() >= 270
        ):
            self.gearSelector.run_to_position(0, "shortest path", 100)
        else:
            self.gearSelector.run_to_position(0, "counterclockwise", 100)

    def selectGear(self, targetGear: int):
        """
        Gear Selection

        Parameters:
        targetGear: Wanted Gear (4:Front-Left, 3:Back-Left, 1:Front-Right, 2:Back-Right)
        """

        if self.selectedGear < targetGear:
            self.gearSelector.run_to_position(
                int(58 * (targetGear - 1)), "clockwise", 100
            )
        elif self.selectedGear > targetGear:
            self.gearSelector.run_to_position(
                int(58 * (targetGear - 1)), "counterclockwise", 100
            )
        self.selectedGear = targetGear

    def driveAttachment(
        self,
        attachmentIndex: int,
        speed: int,
        resistance: bool = False,
        duration: float = 0,
        degree: float = 0,
    ):
        """
        Driving a chosen attachment, either for given time/distance or passively in the background

        Parameters:
        attachmentIndex: Position of Attachment (4:Back-Left, 1:Back-Left, 2:Front-Left, 3:Back-Right)
        speed: Speed of Motor
        duration: Duration of Movement in Seconds
        degree: Distance of Movement in Degrees
        resistance: Move until hitting resistance
        """
        self.driveShaft.stop()
        self.selectGear(attachmentIndex)
        if duration != 0:
            self.driveShaft.run_for_seconds(duration, speed)
        elif degree != 0:
            self.driveShaft.run_for_degrees(
                int(degree * (speed / fabs(speed))), int(fabs(speed))
            )
        else:
            self.driveShaft.start(speed)
            if resistance:
                self.driveShaft.set_stall_detection(True)
                wait_until(self.driveShaft.was_stalled)
                self.driveShaft.stop()
                self.driveShaft.set_stall_detection(False)

    def stopAttachment(self):
        self.driveShaft.stop()

    def resetTimerAndEndingCondition(self):
        """
        Resets Ending Conditions and Timer
        """
        self.timer.reset()
        self.leftMotor.set_degrees_counted(0)
        self.rightMotor.set_degrees_counted(0)
        self.accelerationCounter = 0
        self.decelerationCounter = 0
        self.attachmentStarted = False
        self.attachmentStopped = False

    def CheckEndingCondition(self, endingCondition: int, endingValue: int):
        """
        Check if Ending Condition is reached

        Parameters:
        endingCondition: Type of Condition (0:Cm, 1:Seconds, 2: Line, 3:Degree)
        endingValue: Value of Condition for Cm, Seconds and Degree
        """
        if endingCondition == 0:
            # print(self.rightMotor.get_degrees_counted())
            # print(self.leftMotor.get_degrees_counted())
            print(
                (
                    (
                        abs(self.rightMotor.get_degrees_counted())
                        + abs(self.leftMotor.get_degrees_counted())
                    )
                    / 360
                )
                * pi
                * self.tireRadius
            )
            if (
                (
                    abs(self.rightMotor.get_degrees_counted())
                    + abs(self.leftMotor.get_degrees_counted())
                )
                / 360
            ) * pi * self.tireRadius >= endingValue:
                # self.leftMotor.set_degrees_counted(0)
                # self.rightMotor.set_degrees_counted(0)
                return False
        elif endingCondition == 1:
            print(self.timer.now())
            if self.timer.now() >= endingValue:
                return False
        elif endingCondition == 2:
            if (
                self.frontLightSensor.get_reflected_light() < self.lightBlackValue + 5
                or self.backLightSensor.get_reflected_light() < self.lightBlackValue + 5
            ):
                return False
        elif endingCondition == 3:
            if (
                endingValue - self.turningDegreeTolerance
                <= self.brick.motion_sensor.get_yaw_angle()
                <= endingValue + self.turningDegreeTolerance
            ):
                return False
        return True

    def CalculateAcceleration(self, speed: float, duration: float):
        """
        Calculate Acceleration

        Parameters:
        speed: given speed
        duration: time of acceleration
        """
        if self.accelerationCounter < 50:
            if self.timer.now() >= ((self.accelerationCounter * duration) / 50):
                self.accelerationCounter += 1
            return (speed * self.accelerationCounter) / 50
        return int(speed)

    def CalculateDeceleration(self, speed: int, endSpeed: float, distance: float):
        """
        Calculate Deceleration

        Parameters:
        speed: given speed
        endSpeed: final speed to finish on
        distane: distance of deceleration
        """
        if (
            (
                (
                    self.rightMotor.get_degrees_counted()
                    + self.rightMotor.get_degrees_counted()
                )
                / 720
            )
        ) >= fabs((self.decelerationCounter * distance / 50)):
            self.decelerationCounter += 1
        return int((speed * (50 - self.decelerationCounter)) / 50)

    def GyroDrive(
        self,
        speed: int,
        degree: int,
        endingCondition: int,
        endingValue: int = 0,
        p_correction: int = 0,
        i_correction: int = 0,
        d_correction: int = 0,
        acceleration: int = 0,
        deceleration: int = 0,
        attachmentStart: list[int] = [0, 0, 0],
        attachmentStop: int = 0,
    ):
        """
        PID Gyro-Drive

        Parameters:
        speed: Topspeed of robot
        degree: Targetdegree
        p_correction: P-Correction-Value
        i_correction: I-Correction-Value
        d_correction: D-Correction-Value
        endingCondition: Ending Condition Mode
        endingValue: Value for Ending Condition
        acceleration: Time for Acceleration
        deceleration: Distance for Deceleration
        attachmentStart: List of Index of Attachment, Time until Start and Speed
        attachmentStop: Time until Stop of Attachment
        """
        self.resetTimerAndEndingCondition()
        lastError = 0
        integral = 0
        speed = -speed
        attachmentStarted = False
        attachmentStopped = False
        if p_correction == 0:
            p_correction = self.p_correctionGyroDrive
        if i_correction == 0:
            i_correction = self.i_correctionGyroDrive
        if d_correction == 0:
            d_correction = self.d_correctionGyroDrive
        endingValue = endingValue - deceleration
        if endingCondition == 3:
            endingValue = endingValue - 360 * floor((degree + 180) / 360)
        degree = degree - 360 * floor((degree + 180) / 360)
        if attachmentStart[1] != 0 or attachmentStop != 0:
            while self.CheckEndingCondition(endingCondition, endingValue):
                errorValue = degree - self.brick.motion_sensor.get_yaw_angle()
                if abs(errorValue) > 180:
                    errorValue -= 360
                differential = errorValue - lastError
                integral += errorValue
                corrector = (
                    integral * i_correction
                    + differential * d_correction
                    + errorValue * p_correction
                )
                lastError = errorValue
                self.drivingMotors.start_tank(
                    int(self.CalculateAcceleration(speed + corrector, acceleration)),
                    int(self.CalculateAcceleration(speed - corrector, acceleration)),
                )
                if (
                    attachmentStart[1] != 0
                    and not attachmentStarted
                    and self.timer.now() >= attachmentStart[1]
                ):
                    self.driveAttachment(attachmentStart[0], attachmentStart[2])
                    attachmentStarted = True
                if (
                    attachmentStop != 0
                    and not attachmentStopped
                    and self.timer.now() >= attachmentStop
                ):
                    self.stopAttachment()
                    attachmentStopped = True
        else:
            while self.CheckEndingCondition(endingCondition, endingValue):
                errorValue = degree - self.brick.motion_sensor.get_yaw_angle()
                if abs(errorValue) > 180:
                    errorValue -= 360
                differential = errorValue - lastError
                integral += errorValue
                corrector = (
                    integral * i_correction
                    + differential * d_correction
                    + errorValue * p_correction
                )
                lastError = errorValue
                self.drivingMotors.start_tank(
                    int(self.CalculateAcceleration(speed + corrector, acceleration)),
                    int(self.CalculateAcceleration(speed - corrector, acceleration)),
                )
        if deceleration != 0:
            while self.decelerationCounter <= 50:
                errorValue = degree - self.brick.motion_sensor.get_yaw_angle()
                if abs(errorValue) > 180:
                    errorValue -= 360
                differential = errorValue - lastError
                integral += errorValue
                corrector = (
                    integral * i_correction
                    + differential * d_correction
                    + errorValue * p_correction
                )
                lastError = errorValue
                self.drivingMotors.start_tank(
                    self.CalculateDeceleration(speed + corrector),
                    self.CalculateDeceleration(speed - corrector),
                )
        self.drivingMotors.stop()

    def GyroTurn(
        self,
        degree: int,
        p_correction: int = 0,
        i_correction: int = 0,
        d_correction: int = 0,
        attachmentStart: list[int] = [0, 0, 0],
        attachmentStop: int = 0,
    ):
        """
        PID-Gyro-Tank-Turn

        Parameters:
        degree: Targetdegree
        p_correction: P-Correction-Value
        i_correction: I-Correction-Value
        d_correction: D-Correction-Value
        attachmentStart: List of Index of Attachment, Time until Start and Speed
        attachmentStop: Time until Stop of Attachment
        """
        lastError = 0
        integral = 0
        attachmentStarted = False
        attachmentStopped = False
        if p_correction == 0:
            p_correction = self.p_correctionGyroTurn
        if i_correction == 0:
            i_correction = self.i_correctionGyroTurn
        if d_correction == 0:
            d_correction = self.d_correctionGyroTurn
        degree = degree - 360 * floor((degree + 180) / 360)
        if attachmentStart[1] != 0 or attachmentStop != 0:
            while (
                not degree - self.turningDegreeTolerance
                < self.brick.motion_sensor.get_yaw_angle()
                < degree + self.turningDegreeTolerance
            ):
                errorValue = degree - self.brick.motion_sensor.get_yaw_angle()
                if abs(errorValue) > 180:
                    errorValue -= 360
                differential = errorValue - lastError
                integral += lastError
                corrector = (
                    integral * i_correction
                    + differential * d_correction
                    + errorValue * p_correction
                )
                lastError = errorValue
                self.drivingMotors.start_tank(
                    attachmentStart[2] - corrector, attachmentStart[2] + corrector
                )
                if (
                    attachmentStart[1] != 0
                    and not attachmentStarted
                    and self.timer.now() >= attachmentStart[1]
                ):
                    self.driveAttachment(attachmentStart[0], attachmentStart[2])
                    attachmentStarted = True
                if (
                    attachmentStop != 0
                    and not attachmentStopped
                    and self.timer.now() >= attachmentStop
                ):
                    self.stopAttachment()
                    attachmentStopped = True
        else:
            while (
                not degree - self.turningDegreeTolerance
                <= self.brick.motion_sensor.get_yaw_angle()
                <= degree + self.turningDegreeTolerance
            ):
                errorValue = degree - self.brick.motion_sensor.get_yaw_angle()
                if abs(errorValue) > 180:
                    errorValue -= 360
                differential = errorValue - lastError
                integral += lastError
                corrector = (
                    integral * i_correction
                    + differential * d_correction
                    + errorValue * p_correction
                )
                lastError = errorValue
                self.drivingMotors.start_tank(int(corrector), int(-corrector))
        self.drivingMotors.stop()

    def LineFollower(
        self,
        speed: int,
        frontSensor: bool,
        endingCondition: int,
        endingValue: int = 0,
        leftOfLine: bool = True,
        p_correction: int = 0,
        i_correction: int = 0,
        d_correction: int = 0,
        attachmentStart: list[int] = [0, 0, 0],
        attachmentStop: int = 0,
    ):
        """
        PID-Linefollower

        Parameters:
        speed: Speed of Turn
        frontSensor: Use of front sensor
        leftOfLine: Drive left of Line
        endingCondition: Ending Condition Mode
        endingValue: Value for Ending Condition
        p_correction: P-Correction-Value
        i_correction: I-Correction-Value
        d_correction: D-Correction-Value
        attachmentStart: List of Index of Attachment, Time until Start and Speed
        attachmentStop: Time until Stop of Attachment
        """
        self.resetTimerAndEndingCondition()
        lastError = 0
        integral = 0
        speed = -speed
        attachmentStarted = False
        attachmentStopped = False
        if p_correction == 0:
            p_correction = self.p_correctionLineFollower
        if i_correction == 0:
            i_correction = self.i_correctionLineFollower
        if d_correction == 0:
            d_correction = self.d_correctionLineFollower

        if endingCondition == 3:
            endingValue = endingValue - 360 * floor((degree + 180) / 360)
        lightSensor = self.frontLightSensor if frontSensor else self.backLightSensor
        if leftOfLine:
            leftFactor = -1
        else:
            leftFactor = 1
        if attachmentStart[1] != 0 or attachmentStop != 0:
            while self.CheckEndingCondition(endingCondition, endingValue):
                errorValue = leftFactor * (
                    lightSensor.get_reflected_light() - self.lightMiddleValue
                )
                differential = errorValue - lastError
                integral += lastError
                corrector = (
                    integral * i_correction
                    + differential * d_correction
                    + errorValue * p_correction
                )
                lastError = errorValue
                self.drivingMotors.start_tank(speed - corrector, speed + corrector)
                if not attachmentStarted and self.timer.now() >= attachmentStart[1]:
                    self.driveAttachment(attachmentStart[0], attachmentStart[2])
                    attachmentStarted = True
                if not attachmentStopped and self.timer.now() >= attachmentStop:
                    self.stopAttachment()
                    attachmentStopped = True
        else:
            while self.CheckEndingCondition(endingCondition, endingValue):
                errorValue = leftFactor * (
                    lightSensor.get_reflected_light() - self.lightMiddleValue
                )
                differential = errorValue - lastError
                integral += lastError
                corrector = (
                    integral * i_correction
                    + differential * d_correction
                    + errorValue * p_correction
                )
                lastError = errorValue
                self.drivingMotors.start_tank(speed - corrector, speed + corrector)
                if (
                    attachmentStart[1] != 0
                    and not attachmentStarted
                    and self.timer.now() >= attachmentStart[1]
                ):
                    self.driveAttachment(attachmentStart[0], attachmentStart[2])
                    attachmentStarted = True
                if (
                    attachmentStop != 0
                    and not attachmentStopped
                    and self.timer.now() >= attachmentStop
                ):
                    self.stopAttachment()
                    attachmentStopped = True
        self.drivingMotors.stop()


def LightUpDisplay(brick: PrimeHub, number=int, maxNumber=int):
    brightness = 70
    brick.light_matrix.write(number)
    brick.light_matrix.set_pixel(0, 1, brightness=brightness)
    brick.light_matrix.set_pixel(0, 3, brightness=brightness)
    brick.light_matrix.set_pixel(4, 1, brightness=brightness)
    brick.light_matrix.set_pixel(4, 3, brightness=brightness)
    if number == 1:
        brick.light_matrix.set_pixel(0, 4, brightness=brightness)
        brick.light_matrix.set_pixel(0, 0, brightness=brightness)
        brick.light_matrix.set_pixel(0, 2, brightness=brightness)
    if number == maxNumber:
        brick.light_matrix.set_pixel(4, 0, brightness=brightness)
        brick.light_matrix.set_pixel(4, 2, brightness=brightness)
        brick.light_matrix.set_pixel(4, 4, brightness=brightness)


def MasterControlProgram(
    brick: PrimeHub,
    numberOfRuns: int,
    immedeatePlay: int = 0,
    engines: list[str] = ["D", "C", "B", "E"],
    lightSensors: list[str] = ["A", "F"],
    correctionValues: list[float] = [0.5, 0, 0, 0, 0, 0, 0, 0, 0],
    tireRadius: float = 2.3,
    lightBlackValue: int = 10,
    lightMiddleValue: int = 50,
    turningDegreeTolerance: int = 2,
):
    """
    Master Control Program managing and starting all runs

    parameters:
    brick: Brick of Robot
    numberOfRuns: Number of Runs
    immedeatePlay: 0 starts MainScreen, other numbers immedeately start respective Run
    brick: The Brick of the Robot
    engines: List of Motors (Left, Right, Driveshaft, Gearselector)
    lightSensors: List of Lightsensors (Front, Back)
    correctionValues: List of Correction Values (GyroDrive (p,i,d), LineFollower (p,i,d), GyroTurn (p,i,d))
    tireRadius: Radius of the Robots tires
    lightBlackValue: The Lightvalue of Black
    lightMiddleValue: The middle Lightvalue between Black and White
    turningDegreeTolerance: Tolerance when turning for a degree
    """

    selectedRun = 1
    if immedeatePlay == 0:
        print("Starting MC")
        LightUpDisplay(brick, selectedRun, numberOfRuns)
        while True:
            if brick.left_button.is_pressed():
                while True:
                    if brick.right_button.is_pressed():
                        brick.left_button.wait_until_released()
                        brick.right_button.wait_until_released()
                        print("Play run ", selectedRun)
                        MasterControlProgram(
                            brick,
                            numberOfRuns,
                            selectedRun,
                            engines,
                            lightSensors,
                            correctionValues,
                            tireRadius,
                            lightBlackValue,
                            lightMiddleValue,
                            turningDegreeTolerance,
                        )
                        if selectedRun < numberOfRuns:
                            selectedRun += 1
                            LightUpDisplay(brick, selectedRun, numberOfRuns)
                        break
                    elif not brick.left_button.is_pressed():
                        if selectedRun > 1:
                            selectedRun -= 1
                            LightUpDisplay(brick, selectedRun, numberOfRuns)
                        break

            if brick.right_button.is_pressed():
                while True:
                    if brick.left_button.is_pressed():
                        brick.right_button.wait_until_released()
                        brick.left_button.wait_until_released()
                        print("Play run ", selectedRun)
                        MasterControlProgram(
                            brick,
                            numberOfRuns,
                            selectedRun,
                            engines,
                            lightSensors,
                            correctionValues,
                            tireRadius,
                            lightBlackValue,
                            lightMiddleValue,
                            turningDegreeTolerance,
                        )
                        if selectedRun < numberOfRuns:
                            selectedRun += 1
                            LightUpDisplay(brick, selectedRun, numberOfRuns)
                        break
                    elif not brick.right_button.is_pressed():
                        if selectedRun < numberOfRuns:
                            selectedRun += 1
                            LightUpDisplay(brick, selectedRun, numberOfRuns)
                        break

    elif immedeatePlay == 1:
        run1 = Run(
            brick,
            engines,
            lightSensors,
            correctionValues,
            tireRadius,
            lightBlackValue,
            lightMiddleValue,
            turningDegreeTolerance,
        )
        ######################################################################################################### Run 1
        print("Starting Run 1")
        run1.GyroDrive(
            speed=-60, degree=0, endingCondition=0, endingValue=32, p_correction=4
        )
        run1.GyroDrive(
            speed=35, degree=2, endingCondition=1, endingValue=1.2, p_correction=4
        )
        run1.GyroTurn(degree=-48, p_correction=5)
        run1.GyroDrive(
            speed=-60, degree=-48, endingCondition=0, endingValue=31, p_correction=3
        )
        run1.GyroTurn(degree=32, p_correction=4)
        wait_for_seconds(0.5)

        run1.GyroDrive(speed=-50, degree=45, endingCondition=0, endingValue=28)
        run1.GyroDrive(speed=40, degree=45, endingCondition=1, endingValue=1.1)
        run1.GyroDrive(speed=-50, degree=45, endingCondition=0, endingValue=13)
        run1.GyroDrive(speed=40, degree=45, endingCondition=1, endingValue=1.1)
        run1.GyroDrive(speed=-50, degree=45, endingCondition=0, endingValue=13)
        run1.GyroDrive(speed=25, degree=45, endingCondition=1, endingValue=1.1)

        run1.GyroTurn(degree=-100, p_correction=2)  # 110
        wait_for_seconds(0.5)

        run1.GyroDrive(speed=-40, degree=-125, endingCondition=0, endingValue=3)  # 135
        wait_for_seconds(0.5)
        run1.driveAttachment(FRONT_LEFT, -100, duration=1)
        run1.GyroDrive(speed=40, degree=-135, endingCondition=1, endingValue=1.4)
        run1.GyroTurn(degree=-185, p_correction=3)

        MotorPair("D", "C").move(-60, "cm", speed=100)
        # run1.GyroDrive(speed=-100, degree=-165, endingCondition=0, endingValue=38)

        print("Ended Run 1")

    elif immedeatePlay == 2:
        run2 = Run(
            brick,
            engines,
            lightSensors,
            correctionValues,
            tireRadius,
            lightBlackValue,
            lightMiddleValue,
            turningDegreeTolerance,
        )
        ######################################################################################################### Run 2
        print("Starting Run 2")
        run2.GyroDrive(
            speed=-60, degree=-4, endingCondition=0, endingValue=66, p_correction=3
        )
        run2.GyroDrive(
            speed=70,
            degree=5,
            endingCondition=1,
            endingValue=2,
            acceleration=2,
            p_correction=3,
        )
        wait_for_seconds(0.5)
        run2.GyroTurn(degree=15, p_correction=2)
        run2.GyroDrive(
            speed=-20, degree=15, endingCondition=0, endingValue=2, p_correction=5
        )
        run2.GyroTurn(degree=30, p_correction=2)
        run2.GyroDrive(
            speed=-70, degree=30, endingCondition=0, endingValue=15, p_correction=5
        )
        run2.GyroTurn(degree=-20, p_correction=2)
        run2.GyroDrive(
            speed=-100, degree=-20, endingCondition=0, endingValue=90, p_correction=4
        )  ## 70

        # ALIGNMENT

        wait_for_seconds(0.8)
        run2.GyroTurn(degree=90, p_correction=4)
        run2.GyroDrive(speed=50, degree=90, endingCondition=1, endingValue=1.2)

        print("Ending Run 2")

    elif immedeatePlay == 3:
        run3 = Run(
            brick,
            engines,
            lightSensors,
            correctionValues,
            tireRadius,
            lightBlackValue,
            lightMiddleValue,
            turningDegreeTolerance,
        )
        ######################################################################################################### Run 3
        print("Starting Run 3")

        run3.GyroDrive(
            speed=-60,
            degree=0,
            endingCondition=0,
            endingValue=10,
            acceleration=1,
            p_correction=0.4,
        )
        run3.driveAttachment(FRONT_RIGHT, 50, duration=1)
        run3.GyroDrive(speed=-50, degree=0, endingCondition=0, endingValue=2.75)
        run3.GyroTurn(degree=30, p_correction=2)
        run3.GyroDrive(speed=-40, degree=30, endingCondition=0, endingValue=8)
        run3.GyroTurn(degree=0, p_correction=1)
        run3.driveAttachment(FRONT_RIGHT, -70, duration=0.75)
        run3.GyroDrive(
            speed=-35,
            degree=-3,
            endingCondition=0,
            endingValue=16,
            acceleration=1,
            p_correction=0.6,
        )
        run3.driveAttachment(BACK_RIGHT, -100, duration=1.5)
        run3.driveAttachment(BACK_RIGHT, 100, duration=1.5)
        run3.driveAttachment(BACK_RIGHT, -100, duration=1.5)
        run3.driveAttachment(BACK_RIGHT, 100, duration=1.5)
        run3.driveAttachment(BACK_RIGHT, -100, duration=1.5)
        run3.driveAttachment(BACK_RIGHT, 100, duration=1.5)

        run3.GyroDrive(
            speed=-10, degree=-0.75, endingCondition=0, endingValue=10, p_correction=0.6
        )
        run3.driveAttachment(FRONT_RIGHT, 100, duration=1)
        wait_for_seconds(0.1)
        run3.GyroDrive(speed=50, degree=0, endingCondition=1, endingValue=1.5)
        run3.GyroTurn(degree=30, p_correction=0.8)
        run3.GyroDrive(speed=100, degree=30, endingCondition=1, endingValue=3.5)

        # ALIGNMENT

        wait_for_seconds(0.5)
        run3.GyroTurn(degree=85, p_correction=3)
        print("Ending Run 3")

    elif immedeatePlay == 4:
        run4 = Run(
            brick,
            engines,
            lightSensors,
            correctionValues,
            tireRadius,
            lightBlackValue,
            lightMiddleValue,
            turningDegreeTolerance,
        )
        ######################################################################################################### Run 4#

        # Gradzahlen und Strecken anpassen!

        run4.GyroDrive(speed=-60, degree=0, endingCondition=0, endingValue=19.75)
        wait_for_seconds(0.5)
        run4.GyroTurn(degree=-31, p_correction=2.1)
        wait_for_seconds(0.5)
        run4.GyroDrive(speed=-40, degree=-45, endingCondition=0, endingValue=6)
        run4.driveAttachment(FRONT_LEFT, 70, duration=0.75)
        wait_for_seconds(0.25)
        run4.GyroTurn(degree=-10, p_correction=1.5)
        wait_for_seconds(0.25)
        run4.GyroDrive(speed=-65, degree=-10, endingCondition=0, endingValue=22)
        run4.GyroTurn(degree=-87, p_correction=1)
        wait_for_seconds(0.25)
        run4.driveAttachment(FRONT_RIGHT, 70, duration=0.5)
        run4.GyroDrive(
            speed=-80, degree=-90, endingCondition=0, endingValue=31, p_correction=1.2
        )
        run4.driveAttachment(FRONT_RIGHT, -70, duration=0.7)
        wait_for_seconds(0.25)
        run4.GyroDrive(speed=15, degree=-90, endingCondition=1, endingValue=2.9)
        wait_for_seconds(0.25)
        run4.driveAttachment(FRONT_RIGHT, 70, duration=0.5)
        run4.GyroDrive(speed=35, degree=-90, endingCondition=1, endingValue=1.1)

        # SF:
        # run4.GyroTurn(degree=-130, p_correction=1.5)
        # run4.GyroDrive(speed=60, degree=-130, endingCondition=1, endingValue=2.3)
        # wait_for_seconds(0.25)
        # run4.GyroDrive(speed=-60, degree=-130, endingCondition=1, endingValue=2.3)
        # run4.GyroTurn(degree=-87, p_correction=1)

        # Auto:
        # run4.driveAttachment(1, -100, duration=1)
        # run4.GyroTurn(degree=-30, p_correction=1)
        # run4.GyroDrive(speed=-60, degree=-27, endingCondition=0, endingValue=20)
        # run4.driveAttachment(4, 70, duration=0.75)

    elif immedeatePlay == 5:
        run5 = Run(
            brick,
            engines,
            lightSensors,
            correctionValues,
            tireRadius,
            lightBlackValue,
            lightMiddleValue,
            turningDegreeTolerance,
        )
        run5.driveAttachment(1, 50, duration=1)
        run5.driveAttachment(2, 50, duration=1)
        run5.driveAttachment(3, 50, duration=1)
        run5.driveAttachment(4, 50, duration=1)

    elif immedeatePlay > numberOfRuns:
        brick.light_matrix.write("!")
        wait_for_seconds(2)


MasterControlProgram(PrimeHub(), numberOfRuns=5)
