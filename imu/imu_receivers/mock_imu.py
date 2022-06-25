import threading
from abc import ABC
import time
from typing import Callable

from imu.imu_interface import IIMU
from imu.imu_utils import GyroEuler, AccelerationXYZ


class FunctionIMU(IIMU):
    def __init__(
        self,
        function_x: Callable[[float], float],
        function_y: Callable[[float], float],
        function_z: Callable[[float], float],
        time_scalar: float = 1,
    ):
        super().__init__()
        self.function_x = function_x
        self.function_y = function_y
        self.function_z = function_z
        self._acc = AccelerationXYZ()
        self._gyro = GyroEuler()
        self.start = time.time()
        self.time_scalar = time_scalar

        t = threading.Thread(target=self.loop)
        t.setDaemon(True)
        t.start()

    def loop(self):
        self.emit_acceleration_alert()
        self.emit_gyro_alert()
        t = threading.Thread(target=self.loop)
        t.setDaemon(True)
        t.start()

    def acceleration(self) -> AccelerationXYZ:
        t = (time.time() - self.start) * self.time_scalar
        self._acc.update(t, self.function_x(t), self.function_y(t), self.function_z(t))
        return self._acc

    def gyro(self) -> GyroEuler:
        t = (time.time() - self.start) * self.time_scalar
        self._gyro.update(t, self.function_x(t), self.function_y(t), self.function_z(t))
        return self._gyro


class MockIMU(IIMU, ABC):
    def __init__(self):
        super().__init__()
        self._gyro: GyroEuler = GyroEuler()
        self._acceleration: AccelerationXYZ = AccelerationXYZ()
        self.time = 0

    def acceleration(self) -> AccelerationXYZ:
        """
        get dictionary containing the list of acceleration sensor values over time for each axis.
        :return: dictionary containing the list of acceleration sensor values over time for each axis.
        """
        return self._acceleration

    def gyro(self) -> GyroEuler:
        """
        get dictionary containing the list of gyro sensor values over time for each axis.
        :return: dictionary containing the list of gyro sensor values over time for each axis.
        """
        return self._gyro

    def update(self, acceleration: AccelerationXYZ = None, gyro: GyroEuler = None):
        if gyro is not None:
            self._gyro = gyro
            self.emit_gyro_alert()

        if acceleration is not None:
            self._acceleration = acceleration
            self.emit_acceleration_alert()
