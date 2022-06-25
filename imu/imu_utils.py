from abc import ABC, abstractmethod
from typing import List, Dict, Tuple

from shared.shared_utils import EulerAngle, SensorCoordinate


class AccelerationXYZ:
    def __init__(self):
        self._x: List[SensorCoordinate] = []
        self._y: List[SensorCoordinate] = []
        self._z: List[SensorCoordinate] = []

    def x(self) -> List[SensorCoordinate]:
        return self._x

    def y(self) -> List[SensorCoordinate]:
        return self._y

    def z(self) -> List[SensorCoordinate]:
        return self._z

    def update_x(self, s: SensorCoordinate):
        self._x.append(s)

    def update_y(self, s: SensorCoordinate):
        self._y.append(s)

    def update_z(self, s: SensorCoordinate):
        self._z.append(s)

    def update(self, time: float, x: float, y: float, z: float):
        self.update_x(SensorCoordinate(time, x))
        self.update_y(SensorCoordinate(time, y))
        self.update_z(SensorCoordinate(time, z))


class GyroEuler:
    def __init__(self):
        self._roll: List[SensorCoordinate] = []
        self._pitch: List[SensorCoordinate] = []
        self._yaw: List[SensorCoordinate] = []

    def angle(self) -> EulerAngle:
        return EulerAngle(
            self._roll[-1].value(), self._pitch[-1].value(), self._yaw[-1].value()
        )

    def angles(self) -> Dict[str, List[SensorCoordinate]]:
        return {"roll": self._roll, "pitch": self._pitch, "yaw": self._yaw}

    def update_roll(self, s: SensorCoordinate):
        self._roll.append(s)

    def update_pitch(self, s: SensorCoordinate):
        self._pitch.append(s)

    def update_yaw(self, s: SensorCoordinate):
        self._yaw.append(s)

    def update(self, time: float, roll: float, pitch: float, yaw: float):
        self.update_roll(SensorCoordinate(time, roll))
        self.update_pitch(SensorCoordinate(time, pitch))
        self.update_yaw(SensorCoordinate(time, yaw))


class IIMUFilter(ABC):
    @abstractmethod
    def apply(
        self, acc: AccelerationXYZ, gyro: GyroEuler
    ) -> Tuple[AccelerationXYZ, GyroEuler]:
        raise NotImplemented
