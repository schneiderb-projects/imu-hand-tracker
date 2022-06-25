from abc import ABC, abstractmethod

from hand_.hand import Hand
from imu.imu_spatial_tracker import IIMUSpatialTracker
from positioning_control.imu_to_finger_adapter import (
    SingleJointIMUToFingerAdapter,
)


class IIMUToHandAdapter(ABC):
    @abstractmethod
    def hand(self) -> Hand:
        raise NotImplemented


class SingleJoint5FingerIMUToHandAdapter(IIMUToHandAdapter):
    def __init__(
        self,
        thumb: IIMUSpatialTracker,
        pointer: IIMUSpatialTracker,
        middle: IIMUSpatialTracker,
        ring: IIMUSpatialTracker,
        pinky: IIMUSpatialTracker,
        palm: IIMUSpatialTracker,
    ):
        self.thumb: SingleJointIMUToFingerAdapter = SingleJointIMUToFingerAdapter(thumb)
        self.pointer: SingleJointIMUToFingerAdapter = SingleJointIMUToFingerAdapter(
            pointer
        )
        self.middle: SingleJointIMUToFingerAdapter = SingleJointIMUToFingerAdapter(
            middle
        )
        self.ring: SingleJointIMUToFingerAdapter = SingleJointIMUToFingerAdapter(ring)
        self.pinky: SingleJointIMUToFingerAdapter = SingleJointIMUToFingerAdapter(pinky)
        self.palm: SingleJointIMUToFingerAdapter = SingleJointIMUToFingerAdapter(palm)

    def hand(self) -> Hand:
        return Hand(
            self.thumb.finger(),
            self.pointer.finger(),
            self.middle.finger(),
            self.ring.finger(),
            self.pinky.finger(),
            self.palm.finger(),
        )
