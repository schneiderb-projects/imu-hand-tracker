import time
from random import random

from calibration.linear_calibration_interface import ILinearCalibratorInterface
from imu.imu_spatial_tracker import MockIMUSpatialTracker
from shared.shared_utils import Cartesian3D


class MockLinearCalibrator(ILinearCalibratorInterface):
    def __init__(
        self,
        thumb: MockIMUSpatialTracker,
        pointer: MockIMUSpatialTracker,
        middle: MockIMUSpatialTracker,
        ring: MockIMUSpatialTracker,
        pinky: MockIMUSpatialTracker,
        palm: MockIMUSpatialTracker,
    ):
        self.thumb: MockIMUSpatialTracker = thumb
        self.pointer: MockIMUSpatialTracker = pointer
        self.middle: MockIMUSpatialTracker = middle
        self.ring: MockIMUSpatialTracker = ring
        self.pinky: MockIMUSpatialTracker = pinky
        self.palm: MockIMUSpatialTracker = palm

    def make_fist(self):
        self.palm.set_delta_position(Cartesian3D(0, 0, 0))
        self.thumb.set_delta_position(Cartesian3D(0, 0, 0))
        self.pointer.set_delta_position(Cartesian3D(0, 0, 0))
        self.middle.set_delta_position(Cartesian3D(0, 0, 0))
        self.ring.set_delta_position(Cartesian3D(0, 0, 0))
        self.pinky.set_delta_position(Cartesian3D(0, 0, 0))

    def outstretch_hand(self):
        self.thumb.set_delta_position(Cartesian3D(1, 2, 3))
        self.pointer.set_delta_position(Cartesian3D(1, 2, 3))
        self.middle.set_delta_position(Cartesian3D(1, 2, 3))
        self.ring.set_delta_position(Cartesian3D(1, 2, 3))
        self.pinky.set_delta_position(Cartesian3D(1, 2, 3))
        self.palm.set_delta_position(Cartesian3D(0, 0, 0))

    def fold_thumb(self):
        self.palm.set_delta_position(Cartesian3D(0, 0, 0))
        self.thumb.set_delta_position(Cartesian3D(0, 0, 0))

    def finished(self):
        pass


class LinearCalibratorRandomDelay(ILinearCalibratorInterface):
    def make_fist(self):
        time.sleep(random() * 2)

    def outstretch_hand(self):
        time.sleep(random() * 2)

    def fold_thumb(self):
        time.sleep(random() * 2)

    def finished(self):
        time.sleep(random() * 2)
