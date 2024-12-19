from .utils import Timer
from .configuration import config
from .math import clamp, sigmoid


def gyro_drive_pid(
    parent,
    degree_target: int,
    p_correction: float | None = None,
    i_correction: float | None = None,
    d_correction: float | None = None,
    gyro_tolerance: int | None = None,
):
    """Gyro Drive PID

    :param parent: Parent corrector
    :type parent: Iterator[tuple[int, int]]
    
    :param degree_target: Direction to drive in
    :type degree_target: int
    
    :param p_correction: p correction value. Defaults to gsgr.configuration.config.p_correction.
    :type p_correction: float | None
    
    :param i_correction: i correction value. Defaults to gsgr.configuration.config.i_correction.
    :type i_correction: float | None
    
    :param d_correction: d correction value. Defaults to gsgr.configuration.config.d_correction.
    :type d_correction: float | None
    
    :param gyro_tolerance: tolerance for target degree. Defaults to gsgr.configuration.config.gyro_tolerance.
    :type gyro_tolerance: int | None

    :rtype: Iterator[tuple[int, int]]
    """
    target = degree_target
    while target < -180:
        target += 360
    while target > 180:
        target -= 360
    last_error = 0
    error_sum = 0
    p_correction = config.p_correction if p_correction is None else p_correction
    i_correction = config.i_correction if i_correction is None else i_correction
    d_correction = config.d_correction if d_correction is None else d_correction
    gyro_tolerance = config.gyro_tolerance if gyro_tolerance is None else gyro_tolerance

    while True:
        left, right = next(parent)
        tar, cur = target, config.degree_o_meter.oeioei
        error_value = min((tar - cur, tar - cur - 360, tar - cur + 360), key=abs)
        differential = error_value - last_error
        error_sum += error_value
        if abs(error_value) < gyro_tolerance:
            error_sum = 0
            differential = 0
        corrector = (
            error_sum * i_correction
            + differential * d_correction
            + error_value * p_correction
        )
        last_error = error_value
        yield (left + corrector, right - corrector)


def speed(left, right=None):
    right = right if right is not None else left
    while True:
        yield (left, right)


def gyro_turn_pid(
    parent,
    degree_target: int,
    p_correction: float | None = None,
    i_correction: float | None = None,
    d_correction: float | None = None,
    gyro_tolerance: int | None = None,
):
    target = degree_target
    while target < -180:
        target += 360
    while target > 180:
        target -= 360
    last_error = 0
    error_sum = 0
    p_correction = config.p_correction if p_correction is None else p_correction
    i_correction = config.i_correction if i_correction is None else i_correction
    d_correction = config.d_correction if d_correction is None else d_correction
    gyro_tolerance = config.gyro_tolerance if gyro_tolerance is None else gyro_tolerance

    while True:
        left, right = next(parent)
        tar, cur = target, config.degree_o_meter.oeioei
        error_value = min((tar - cur, tar - cur - 360, tar - cur + 360), key=abs)
        differential = error_value - last_error
        error_sum += error_value
        if error_value < gyro_tolerance:
            error_sum = 0
            differential = 0
        corrector = (
            error_sum * i_correction
            + differential * d_correction
            + error_value * p_correction
        )
        last_error = error_value
        yield (corrector * (left / 100), -corrector * (right / 100))


def pause(parent, start: int, duration: int):
    timer = Timer()
    while True:
        if start < timer.elapsed < (start + duration):
            yield (0, 0)
        yield next(parent)


def accelerate(parent, for_, start_at = None):
    while True:
        left, right = next(parent)
        if start_at is not None and next(start_at) < 100:
            yield left, right
        else:
            speed_mutiplier = clamp(next(for_)/ 100, 0.5, 1)
            print(speed_mutiplier)
            yield (left * speed_mutiplier, right * speed_mutiplier)
            
def decelerate(parent, from_, for_):
    while True:
        left, right = next(parent)
        if next(from_) < 100:
            yield left, right
        else:
            speed_mutiplier = 1 - clamp(next(for_)/ 100, 0.5, 1)
            yield (left * speed_mutiplier, right * speed_mutiplier)
        
# def accelerate_sec(parent, duration: int, start: int = 0):
#     timer = Timer()
#     while True:
#         left, right = next(parent)
#         speed_mutiplier = clamp(max(timer.elapsed - start, 0) / duration, 0, 1)
#         yield (left * speed_mutiplier, right * speed_mutiplier)


# def decelerate_sec(parent, duration: int, start: int = 0):
#     timer = Timer()
#     while True:
#         left, right = next(parent)
#         speed_mutiplier = 1 - clamp(max(timer.elapsed - start, 0) / duration, 0, 1)
#         yield (left * speed_mutiplier, right * speed_mutiplier)


def sigmoid_accelerate_sec(
    parent, duration: int, smooth: int = 6, stretch: bool = True
):
    timer = Timer()
    cutoff = sigmoid(-smooth) if stretch else 0
    while True:
        left, right = next(parent)
        now = timer.elapsed
        speed_mutiplier = clamp(
            round(
                (sigmoid((clamp(now / duration, 0, 1) * 2 * smooth) - smooth) - cutoff)
                / (1 - cutoff),
                2,
            ),
            0,
            1,
        )
        yield (left * speed_mutiplier, right * speed_mutiplier)
