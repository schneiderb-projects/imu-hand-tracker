from abc import abstractmethod, ABC
from typing import List, Callable

from imu.imu_utils import AccelerationXYZ, GyroEuler, IIMUFilter


class IMUListener:
    # TODO: add function typing
    def __init__(
        self,
        acceleration_callback: Callable[[AccelerationXYZ], None] = None,
        gyro_callback: Callable[[GyroEuler], None] = None,
    ):
        if acceleration_callback is not None:
            self.acceleration_changed = acceleration_callback

        if gyro_callback is not None:
            self.gyro_changed = gyro_callback

    def acceleration_changed(self, acceleration_coordinates: AccelerationXYZ):
        """
        call back function for when acceleration coordinates are updated
        :param acceleration_coordinates: dictionary containing the list of acceleration sensor values over time for each axis
        """
        pass

    def gyro_changed(self, gyro_coordinates: GyroEuler):
        """
        call back function for when gyro coordinates are updated
        :param gyro_coordinates: dictionary containing the list of gyro sensor values over time for each axis.
        """
        pass


class IIMU(ABC):
    def __init__(self, imu_filter: List[IIMUFilter] = None):
        if filter is None:
            self.filter = lambda a, b: [a, b]
        else:
            self.filter = imu_filter
        self._subscribers: List[IMUListener] = []

    @abstractmethod
    def acceleration(self) -> AccelerationXYZ:
        """
        get dictionary containing the list of acceleration sensor values over time for each axis.
        :return: dictionary containing the list of acceleration sensor values over time for each axis.
        """
        raise NotImplemented

    @abstractmethod
    def gyro(self) -> GyroEuler:
        """
        get dictionary containing the list of gyro sensor values over time for each axis.
        :return: dictionary containing the list of gyro sensor values over time for each axis.
        """
        raise NotImplemented

    def subscribe(self, listener: IMUListener):
        self._subscribers.append(listener)

    def emit_acceleration_alert(self):
        for subscriber in self._subscribers:
            subscriber.acceleration_changed(self.acceleration())

    def emit_gyro_alert(self):
        for subscriber in self._subscribers:
            subscriber.gyro_changed(self.gyro())
