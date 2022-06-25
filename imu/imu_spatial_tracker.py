import time
from abc import ABC, abstractmethod

from numpy import exp

from imu.imu_angle_tracker import IMUAngleTracker
from imu.imu_interface import IIMU
from imu.imu_position_tracker import IMUPositionTracker
from imu.imu_utils import EulerAngle
from shared.shared_utils import Cartesian3D, SensorCoordinate3D, SensorCoordinate


class IIMUSpatialTracker(ABC):
    @abstractmethod
    def zero_angle(self):
        raise NotImplemented

    @abstractmethod
    def zero_position(self):
        raise NotImplemented

    @abstractmethod
    def position(self) -> SensorCoordinate3D:
        raise NotImplemented

    @abstractmethod
    def angle(self) -> EulerAngle:
        raise NotImplemented

    @abstractmethod
    def timeSinceLastUpdate(self):
        """
        :return: time since last data received (in seconds)

        """
        raise NotImplemented


class IMUSpatialTracker(IIMUSpatialTracker):
    def __init__(self, imu: IIMU):
        self.imu = imu
        self._angle: IMUAngleTracker = IMUAngleTracker(self.imu)
        self._position: IMUPositionTracker = IMUPositionTracker(self.imu)

    def zero_angle(self):
        self._angle.zero()

    def zero_position(self):
        self._position.zero()

    def position(self) -> SensorCoordinate3D:
        return self._position.delta()

    def angle(self) -> EulerAngle:
        return self._angle.angle()

    def timeSinceLastUpdate(self):
        return max(
            self._angle.timeSinceLastUpdate(), self._position.timeSinceLastUpdate()
        )


class MockIMUSpatialTracker(IIMUSpatialTracker):
    def __init__(self):
        self._delta_position: SensorCoordinate3D = SensorCoordinate3D(
            SensorCoordinate(0, 0), SensorCoordinate(0, 0), SensorCoordinate(0, 0)
        )
        self._delta_angle: EulerAngle = EulerAngle(0, 0, 0)

    def set_delta_position(self, position: Cartesian3D):
        t = time.time()
        self._delta_position = SensorCoordinate3D(
            SensorCoordinate(t, position.x()),
            SensorCoordinate(t, position.y()),
            SensorCoordinate(t, position.z()),
        )

    def set_delta_angle(self, angle: EulerAngle):
        self._delta_angle = angle

    def angle(self) -> EulerAngle:
        return self._delta_angle

    def position(self) -> SensorCoordinate3D:
        return self._delta_position

    def zero_angle(self):
        self._delta_angle: EulerAngle = EulerAngle(0, 0, 0)

    def zero_position(self):
        self._delta_position: Cartesian3D = Cartesian3D(0, 0, 0)

    def timeSinceLastUpdate(self):
        return exp(-(time.time() % 20)) + 0.5
