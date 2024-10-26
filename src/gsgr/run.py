# def gyro_turn(
#     self,
#     degree: int,
#     ending_condition: EndingCondition = EndingCondition(),
#     p_correction: int = 0,
#     i_correction: int = 0,
#     d_correction: int = 0,
#     attachment_start: list[int] | None = None,
#     attachment_stop: int = 0,
#     speed_multiplier: float = 1,
#     speed_multiplier_left: float = 1,
#     speed_multiplier_right: float = 1,
# ):
#     """
#     PID-Gyro-Tank-Turn

#     Parameters:
#     degree: Targetdegree
#     ending_condition: Ending Condition to force stop
#     p_correction: P-Correction-Value
#     i_correction: I-Correction-Value
#     d_correction: D-Correction-Value
#     attachmentStart: List of Index of Attachment, Time until Start and Speed
#     attachmentStop: Time until Stop of Attachment
#     speed_multiplier: Factor to multiply speed by.
#     speed_multiplier_left: Factor to multiply speed by on left side.
#     speed_multiplier_right: Factor to multiply speed by on right side.
#     """
#     self.check_battery()

#     speed_multiplier_left = speed_multiplier * speed_multiplier_left
#     speed_multiplier_right = speed_multiplier * speed_multiplier_right

#     # Resetting everything
#     if attachment_start is None:
#         attachment_start = [0, 0, 0]
#     degree = degree - self.degree_offset
#     self.reset_timer_and_ending_condition()
#     last_error = 0
#     integral = 0
#     attachment_started = False
#     attachment_stopped = False
#     if p_correction == 0:
#         p_correction = self.p_correction_gyro_turn
#     if i_correction == 0:
#         i_correction = self.i_correction_gyro_turn
#     if d_correction == 0:
#         d_correction = self.d_correction_gyro_turn
#     degree = degree - 360 * floor((degree + 180) / 360)
#     # If an Attachement is started or stopped during the movement, start this loop
#     # The following code is completely useless (inside the if block),
#     # but we have it and i wont remove it.
#     if attachment_start[1] != 0 or attachment_stop != 0:
#         while (
#             not degree - self.turning_degree_tolerance
#             < self.brick.motion_sensor.get_yaw_angle()
#             < degree + self.turning_degree_tolerance
#         ) and not ending_condition.check(self):
#             # The new sensor value is retreaved and the error-value calculated
#             error_value = degree - self.brick.motion_sensor.get_yaw_angle()

#             # This works now. I don't know what you were doing here before!!!!
#             if error_value > 180:
#                 error_value -= 360
#             if error_value <= -180:
#                 error_value += 360
#             # The necessary values for the PID-Controller get calculated
#             differential = error_value - last_error
#             integral += last_error
#             # The robot corrects according to the PID-Controller
#             corrector = (
#                 integral * i_correction
#                 + differential * d_correction
#                 + error_value * p_correction
#             )
#             last_error = error_value
#             # If an attachementStart is planned, check the timer and start the Attachement
#             self.driving_motors.start_tank(
#                 round(
#                     (attachment_start[2] - corrector)
#                     * speed_multiplier_left
#                     * self.global_speed_multiplier
#                 ),
#                 round(
#                     (attachment_start[2] + corrector)
#                     * speed_multiplier_right
#                     * self.global_speed_multiplier
#                 ),
#             )
#             # If an attachementStart is planned, check the timer and start the Attachement
#             if (
#                 attachment_start[1] != 0
#                 and not attachment_started
#                 and self.timer.now() >= attachment_start[1]
#             ):
#                 self.drive_attachment(attachment_start[0], attachment_start[2])
#                 attachment_started = True
#             # If an atachementStop is planned, check the timer and stop the Attachement
#             if (
#                 attachment_stop != 0
#                 and not attachment_stopped
#                 and self.timer.now() >= attachment_stop
#             ):
#                 self.stop_attachment()
#                 attachment_stopped = True
#     # If there won't be any Attachement use, start this loop
#     else:
#         while (
#             not degree - self.turning_degree_tolerance
#             <= self.brick.motion_sensor.get_yaw_angle()
#             <= degree + self.turning_degree_tolerance
#         ) and not ending_condition.check(self):
#             # The new sensor value is retreaved and the error-value
#             error_value = degree - self.brick.motion_sensor.get_yaw_angle()

#             # This works now. I don't know what you were doing here before!!!!
#             if error_value > 180:
#                 error_value -= 360
#             if error_value <= -180:
#                 error_value += 360
#             # The necessary values for the PID-Controller get calculated
#             differential = error_value - last_error
#             integral += last_error
#             corrector = (
#                 integral * i_correction
#                 + differential * d_correction
#                 + error_value * p_correction
#             )
#             last_error = error_value
#             # The robot corrects according to the PID-Controller
#             self.driving_motors.start_tank(
#                 round(
#                     int(corrector)
#                     * speed_multiplier_left
#                     * self.global_speed_multiplier
#                 ),
#                 round(
#                     int(-corrector)
#                     * speed_multiplier_right
#                     * self.global_speed_multiplier
#                 ),
#             )
#     # The motors come to a full-stop
#     self.driving_motors.stop()

# def gyro_bend(
#     self,
#     speed: int,
#     degree: int,
#     radius: float,
#     p_correction: int = 0,
#     i_correction: int = 0,
#     d_correction: int = 0,
#     acceleration: int = 0,
#     deceleration: int = 0,
#     attachment_start: list[int] | None = None,
#     attachment_stop: int = 0,
#     speed_multiplier_right: int = 1,
#     speed_multiplier_left: int = 1,
# ):
#     """
#     PID Gyro-Band

#     Parameters:
#     speed: Topspeed of robot
#     degree: Targetdegree
#     p_correction: P-Correction-Value
#     i_correction: I-Correction-Value
#     d_correction: D-Correction-Value
#     radius: Bend-Radius
#     acceleration: Time for Acceleration
#     deceleration: Distance for Deceleration
#     attachmentStart: List of Index of Attachment, Time until Start and Speed
#     attachmentStop: Time until Stop of Attachment
#     speed_multiplier_left: Factor to multiply speed by on left side.
#     speed_multiplier_right: Factor to multiply speed by on right side.
#     """
#     self.check_battery()
#     # Resetting everything
#     if attachment_start is None:
#         attachment_start = [0, 0, 0]
#     degree = degree - self.degree_offset
#     self.reset_timer_and_ending_condition()
#     last_error = 0
#     integral = 0
#     speed = -speed
#     attachment_started = False
#     attachment_stopped = False
#     if p_correction == 0:
#         p_correction = self.p_correction_gyro_drive
#     if i_correction == 0:
#         i_correction = self.i_correction_gyro_drive
#     if d_correction == 0:
#         d_correction = self.d_correction_gyro_drive
#     if deceleration != 0:
#         ending_value = ending_value - deceleration
#     degree = degree - 360 * floor((degree + 180) / 360)
#     starting_degree = self.brick.motion_sensor.get_yaw_angle()
#     ending_condition = Deg(degree)
#     self.left_motor.set_degrees_counted(0)
#     self.right_motor.set_degrees_counted(0)
#     circumfrence_in_degree = (
#         2
#         * pi
#         * radius
#         * ((ending_condition.value - starting_degree) / 360)
#         / ((self.tire_radius * 2 * pi) / 180)
#     )
#     # If an Attachement is started or stopped during the movement, start this loop
#     if attachment_start[1] != 0 or attachment_stop != 0:
#         while not ending_condition.check(self):
#             # The new sensor value is retreaved and the error-value calculated
#             degree = starting_degree + (
#                 ending_condition.value - starting_degree
#             ) * (
#                 circumfrence_in_degree
#                 / (
#                     self.right_motor.get_degrees_counted()
#                     + self.left_motor.get_degrees_counted()
#                 )
#             )
#             error_value = degree - self.brick.motion_sensor.get_yaw_angle()

#             # This works now. I don't know what you were doing here before!!!!
#             if error_value > 180:
#                 error_value -= 360
#             if error_value <= -180:
#                 error_value += 360
#             # The necessary values for the PID-Controller get calculated
#             differential = error_value - last_error
#             integral += error_value
#             corrector = (
#                 integral * i_correction
#                 + differential * d_correction
#                 + error_value * p_correction
#             )
#             last_error = error_value
#             # The robot corrects according to the PID-Controller and Acceleration
#             self.driving_motors.start_tank(
#                 int(
#                     self.calculate_acceleration(speed + corrector, acceleration)
#                     * speed_multiplier_left
#                     * self.global_speed_multiplier
#                 ),
#                 int(
#                     self.calculate_acceleration(speed - corrector, acceleration)
#                     * speed_multiplier_right
#                     * self.global_speed_multiplier
#                 ),
#             )
#             # If an attachementStart is planned, check the timer and start the Attachement
#             if (
#                 attachment_start[1] != 0
#                 and not attachment_started
#                 and self.timer.now() >= attachment_start[1]
#             ):
#                 self.drive_attachment(attachment_start[0], attachment_start[2])
#                 attachment_started = True
#             # If an atachementStop is planned, check the timer and stop the Attachement
#             if (
#                 attachment_stop != 0
#                 and not attachment_stopped
#                 and self.timer.now() >= attachment_stop
#             ):
#                 self.stop_attachment()
#                 attachment_stopped = True
#     # If there won't be any Attachement use, start this loop
#     else:
#         while not ending_condition.check(self):
#             # The new sensor value is retreaved and the error-value calculated
#             error_value = degree - self.brick.motion_sensor.get_yaw_angle()

#             # This works now. I don't know what you were doing here before!!!!
#             if error_value > 180:
#                 error_value -= 360
#             if error_value <= -180:
#                 error_value += 360
#             # The necessary values for the PID-Controller get calculated
#             differential = error_value - last_error
#             integral += error_value
#             corrector = (
#                 integral * i_correction
#                 + differential * d_correction
#                 + error_value * p_correction
#             )
#             last_error = error_value
#             # The robot corrects according to the PID-Controller
#             self.driving_motors.start_tank(
#                 int(
#                     self.calculate_acceleration(speed + corrector, acceleration)
#                     * speed_multiplier_left
#                     * self.global_speed_multiplier
#                 ),
#                 int(
#                     self.calculate_acceleration(speed - corrector, acceleration)
#                     * speed_multiplier_right
#                     * self.global_speed_multiplier
#                 ),
#             )
#     # If deceleration is wanted, stop the above loops early to start decelerating
#     # The PID-Loop stays the same,
#     # the speed only gets decelerated before being put into the motors
#     if deceleration != 0:
#         while self.deceleration_counter <= 50:
#             error_value = degree - self.brick.motion_sensor.get_yaw_angle()
#             if abs(error_value) > 180:
#                 error_value -= 360
#             differential = error_value - last_error
#             integral += error_value
#             corrector = (
#                 integral * i_correction
#                 + differential * d_correction
#                 + error_value * p_correction
#             )
#             last_error = error_value
#             self.driving_motors.start_tank(
#                 self.calculate_deceleration(speed + corrector),
#                 self.calculate_deceleration(speed - corrector),
#             )
#     # The motors come to a full-stop
#     self.driving_motors.stop()

# def line_follower(
#     self,
#     speed: int,
#     front_sensor: bool,
#     ending_condition: int,
#     left_of_line: bool = True,
#     p_correction: int = 0,
#     i_correction: int = 0,
#     d_correction: int = 0,
#     attachment_start: list[int] | None = None,
#     attachment_stop: int = 0,
# ):
#     """
#     PID-Linefollower

#     Parameters:
#     speed: Speed of Turn
#     frontSensor: Use of front sensor
#     leftOfLine: Drive left of Line
#     ending_condition: Ending Condition
#     p_correction: P-Correction-Value
#     i_correction: I-Correction-Value
#     d_correction: D-Correction-Value
#     attachmentStart: List of Index of Attachment, Time until Start and Speed
#     attachmentStop: Time until Stop of Attachment
#     """
#     self.check_battery()
#     # Resetting everything
#     if attachment_start is None:
#         attachment_start = [0, 0, 0]
#     self.reset_timer_and_ending_condition()
#     last_error = 0
#     integral = 0
#     speed = -speed
#     attachment_started = False
#     attachment_stopped = False
#     if p_correction == 0:
#         p_correction = self.p_correction_line_follower
#     if i_correction == 0:
#         i_correction = self.i_correction_line_follower
#     if d_correction == 0:
#         d_correction = self.d_correction_line_follower
#     light_sensor = (
#         self.front_light_sensor if front_sensor else self.back_light_sensor
#     )
#     if left_of_line:
#         left_factor = -1
#     else:
#         left_factor = 1
#     # If an atachementStop is planned, check the timer and stop the Attachement
#     if attachment_start[1] != 0 or attachment_stop != 0:
#         while not ending_condition.check(self):
#             # The new sensor value is retreaved and the error-value calculated
#             error_value = left_factor * (
#                 light_sensor.get_reflected_light() - self.light_middle_value
#             )
#             # The necessary values for the PID-Controller get calculated
#             differential = error_value - last_error
#             integral += last_error
#             corrector = (
#                 integral * i_correction
#                 + differential * d_correction
#                 + error_value * p_correction
#             )
#             last_error = error_value
#             # The robot corrects according to the PID-Controller
#             self.driving_motors.start_tank(speed - corrector, speed + corrector)
#             # If an attachementStart is planned, check the timer and start the Attachement
#             if not attachment_started and self.timer.now() >= attachment_start[1]:
#                 self.drive_attachment(attachment_start[0], attachment_start[2])
#                 attachment_started = True
#             # If an atachementStop is planned, check the timer and stop the Attachement
#             if not attachment_stopped and self.timer.now() >= attachment_stop:
#                 self.stop_attachment()
#                 attachment_stopped = True
#     # If there won't be any Attachement use, start this loop
#     else:
#         while not ending_condition.check(self):
#             error_value = left_factor * (
#                 light_sensor.get_reflected_light() - self.light_middle_value
#             )
#             differential = error_value - last_error
#             integral += last_error
#             corrector = (
#                 integral * i_correction
#                 + differential * d_correction
#                 + error_value * p_correction
#             )
#             last_error = error_value
#             self.driving_motors.start_tank(speed - corrector, speed + corrector)
#             if (
#                 attachment_start[1] != 0
#                 and not attachment_started
#                 and self.timer.now() >= attachment_start[1]
#             ):
#                 self.drive_attachment(attachment_start[0], attachment_start[2])
#                 attachment_started = True
#             if (
#                 attachment_stop != 0
#                 and not attachment_stopped
#                 and self.timer.now() >= attachment_stop
#             ):
#                 self.stop_attachment()
#                 attachment_stopped = True
#     self.driving_motors.stop()
