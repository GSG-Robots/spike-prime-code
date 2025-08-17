import time

from .config import cfg
from .enums import SWSensor
import hub
from .menu import ActionMenuItem


class Run(ActionMenuItem):
    """A context manager in which the run is being executed.

    This is implemented to support :py:class:`~gsgr.config.cfg` changes for individual runs.
    """

    def __init__(
        self,
        display_as: int | str,
        color: int,
        run,
        left_sensor: tuple[int, int] | None = None,
        right_sensor: tuple[int, int] | None = None,
    ):
        """
        :param display_as: Passed to :py:class:`~gsgr.menu.MenuItem`. Sets :py:attr:`display_as` initially.
        :param color: Passed to :py:class:`~gsgr.menu.MenuItem`. Sets :py:attr:`color` initially.
        :param config: A context manager to execute the run in. Designed for :py:class:`~gsgr.config.cfg` calls. Sets :py:attr:`context` initially.
        :param run: The run's main function / callback.
        """
        super().__init__(run, display_as, color)
        self.left_sensor: tuple[int, int] | None = left_sensor
        self.right_sensor: tuple[int, int] | None = right_sensor
        self.left_req_dcon = False
        self.right_req_dcon = False

    def prepare(self) -> None:
        cfg.LEFT_SW_SENSOR = self.left_sensor[1] if self.left_sensor is not None else -1
        cfg.RIGHT_SW_SENSOR = self.right_sensor[1] if self.right_sensor is not None else -1
        return super().prepare()

    def update(self, first=False) -> None:
        if self.left_sensor is None and self.right_sensor is None:
            return
        if first:
            self.left_req_dcon = self.left_sensor is not None and not (cfg.LEFT_SW_SENSOR == -1 or (cfg.LEFT_SW_SENSOR == SWSensor.INTEGRATED_LIGHT == self.left_sensor[1]))
            self.right_req_dcon = self.right_sensor is not None and not (cfg.RIGHT_SW_SENSOR == -1 or (cfg.RIGHT_SW_SENSOR == SWSensor.INTEGRATED_LIGHT == self.right_sensor[1]))
        left_con = True
        right_con = True
        if self.left_sensor is not None:
            left_con = cfg.LEFT_SENSOR_TYPE == self.left_sensor[0]
        if self.right_sensor is not None:
            right_con = cfg.RIGHT_SENSOR_TYPE == self.right_sensor[0]
        if self.left_req_dcon:
            left_con = False
            if cfg.LEFT_SENSOR_TYPE is None:
                self.left_req_dcon = False
        if self.right_req_dcon:
            right_con = False
            if cfg.RIGHT_SENSOR_TYPE is None:
                self.right_req_dcon = False
        overlap = 3
        tm = 750
        scale = abs(tm - time.ticks_ms() % (2 * tm)) / tm
        if cfg.LANDSCAPE:
            hub.display.pixel(4, 4, int((not left_con) * 9 * overlap * scale))
            hub.display.pixel(4, 0, int((not right_con) * 9 * overlap * scale))
        else:
            hub.display.pixel(4, 4, int((not left_con) * 9 * overlap * scale))
            hub.display.pixel(0, 4, int((not right_con) * 9 * overlap * scale))
        if left_con and right_con:
            hub.led(self.color)
        else:
            hub.led(9) # hub.led(int(scale * 256), 0, 0)

    def cleanup(self):
        """Patched verison of :py:meth:`MenuItem.cleanup` to stop all motors."""
        cfg.DRIVING_MOTORS.brake()
        cfg.GEAR_SHAFT.float()
        cfg.GEAR_SELECTOR.hold()
