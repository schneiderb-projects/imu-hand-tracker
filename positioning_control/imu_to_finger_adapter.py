from abc import ABC, abstractmethod

from hand_.finger import Finger, Cartesian3D
from imu.imu_spatial_tracker import IIMUSpatialTracker


class IIMUToFingerAdapter(ABC):
    @abstractmethod
    def finger(self) -> Finger:
        raise NotImplemented


class SingleJointIMUToFingerAdapter(IIMUToFingerAdapter, ABC):
    def __init__(self, ist: IIMUSpatialTracker):
        self.ist = ist

    def finger(self) -> Finger:
        position: Cartesian3D = self.ist.position().toCartesian3D()
        return Finger([position])
