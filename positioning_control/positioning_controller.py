import time
from abc import ABC, abstractmethod
from typing import Union, Dict

from numpy import sin, cos

from calibration.linear_calibration_interface import ILinearCalibratorInterface
from hand_.finger import Finger
from hand_.hand import Hand
from imu.imu_spatial_tracker import IIMUSpatialTracker
from positioning_control.imus_to_hand_adapter import (
    SingleJoint5FingerIMUToHandAdapter,
    IIMUToHandAdapter,
)
from shared.shared_utils import Line3D, Cartesian3D


class IPositioningController(ABC):
    def __init__(
        self,
        thumb: IIMUSpatialTracker,
        pointer: IIMUSpatialTracker,
        middle: IIMUSpatialTracker,
        ring: IIMUSpatialTracker,
        pinky: IIMUSpatialTracker,
        palm: IIMUSpatialTracker,
    ):
        self._thumb: IIMUSpatialTracker = thumb
        self._pointer: IIMUSpatialTracker = pointer
        self._middle: IIMUSpatialTracker = middle
        self._ring: IIMUSpatialTracker = ring
        self._pinky: IIMUSpatialTracker = pinky
        self._palm: IIMUSpatialTracker = palm

    @abstractmethod
    def motorPositionPercentages(self) -> Dict[str, float]:
        raise NotImplemented

    @abstractmethod
    def hand(self) -> Hand:
        raise NotImplemented

    @abstractmethod
    def calibrate(self) -> bool:
        raise NotImplemented

    @abstractmethod
    def isCalibrated(self) -> bool:
        raise NotImplemented

    @abstractmethod
    def thumbIsStreaming(self):
        raise NotImplemented

    @abstractmethod
    def pointerIsStreaming(self):
        raise NotImplemented

    @abstractmethod
    def middleIsStreaming(self):
        raise NotImplemented

    @abstractmethod
    def ringIsStreaming(self):
        raise NotImplemented

    @abstractmethod
    def pinkyIsStreaming(self):
        raise NotImplemented

    @abstractmethod
    def palmIsStreaming(self):
        raise NotImplemented

    def thumb(self) -> IIMUSpatialTracker:
        return self._thumb

    def pointer(self) -> IIMUSpatialTracker:
        return self._pointer

    def middle(self) -> IIMUSpatialTracker:
        return self._middle

    def ring(self) -> IIMUSpatialTracker:
        return self._ring

    def pinky(self) -> IIMUSpatialTracker:
        return self._pinky

    def palm(self) -> IIMUSpatialTracker:
        return self._palm


class SingleJointLinearApproximationPalmRelativePositioningController(
    IPositioningController
):
    def __init__(
        self,
        thumb: IIMUSpatialTracker,
        pointer: IIMUSpatialTracker,
        middle: IIMUSpatialTracker,
        ring: IIMUSpatialTracker,
        pinky: IIMUSpatialTracker,
        palm: IIMUSpatialTracker,
        linear_sensor_calibrator: ILinearCalibratorInterface,
    ):
        super().__init__(thumb, pointer, middle, ring, pinky, palm)
        self.sensor_calibrator = linear_sensor_calibrator
        self.iha: IIMUToHandAdapter = SingleJoint5FingerIMUToHandAdapter(
            thumb, pointer, middle, ring, pinky, palm
        )
        self.hand_lines: Dict[str, Union[None, Line3D]] = {
            "thumb": None,
            "pointer": None,
            "middle": None,
            "ring": None,
            "pinky": None,
        }

        self.fist_calibration_coordinates: Union[None, Hand] = None

    def motorPositionPercentages(self) -> Dict[str, float]:
        """
        fist is 1, outstretched is 0, everything else somewhere in between
        :return:
        """
        current_hand = self.hand()
        to_return = {}
        for k in self.hand_lines.keys():
            to_return[k] = (
                current_hand[k].joints()[0].distance(self.hand_lines[k].initial())
                / self.hand_lines[k].length()
            )
        return to_return

    def hand(self) -> Hand:
        if not self.isCalibrated():
            raise Exception("hand not calibrated yet")
        current_hand = self.iha.hand()

        # ====================================This is for rounding to calibrated line====================================
        coordinates = {
            "thumb": self.hand_lines["thumb"].nearest_coordinate_on_line(
                current_hand.thumb().joints()[0]
            ),
            "pointer": self.hand_lines["pointer"].nearest_coordinate_on_line(
                current_hand.pointer().joints()[0]
            ),
            "middle": self.hand_lines["middle"].nearest_coordinate_on_line(
                current_hand.middle().joints()[0]
            ),
            "ring": self.hand_lines["ring"].nearest_coordinate_on_line(
                current_hand.ring().joints()[0]
            ),
            "pinky": self.hand_lines["pinky"].nearest_coordinate_on_line(
                current_hand.pinky().joints()[0]
            ),
        }

        for k in coordinates.keys():
            if not self.hand_lines[k].is_between_initial_coordinates(
                coordinates[k].x()
            ):
                if coordinates[k].distance(self.hand_lines[k].final()) < coordinates[
                    k
                ].distance(self.hand_lines[k].initial()):
                    coordinates[k] = self.hand_lines[k].final()
                else:
                    coordinates[k] = self.hand_lines[k].initial()
        # ==============================================================================================================

        rounded_hand = Hand(
            Finger([coordinates["thumb"]]),
            Finger([coordinates["pointer"]]),
            Finger([coordinates["middle"]]),
            Finger([coordinates["ring"]]),
            Finger([coordinates["pinky"]]),
            Finger([self._palm.position().toCartesian3D()]),
        )

        return rounded_hand

    def calibrate(self) -> bool:
        # zero in fist position
        self.sensor_calibrator.make_fist()
        self._pointer.zero_position()
        self._middle.zero_position()
        self._ring.zero_position()
        self._pinky.zero_position()
        self._palm.zero_position()

        self.sensor_calibrator.fold_thumb()
        self._thumb.zero_position()
        # thumb_zero = self._thumb.position().toCartesian3D().subtract(self._palm.position().toCartesian3D())

        self.sensor_calibrator.outstretch_hand()
        pointer_fist = self._pointer.position().toCartesian3D()
        middle_fist = self._middle.position().toCartesian3D()
        ring_fist = self._ring.position().toCartesian3D()
        pinky_fist = self._pinky.position().toCartesian3D()
        thumb_folded = self._thumb.position().toCartesian3D()

        self.sensor_calibrator.finished()

        self.fist_calibration_coordinates = Hand(
            Finger([thumb_folded]),
            Finger([pointer_fist]),
            Finger([middle_fist]),
            Finger([ring_fist]),
            Finger([pinky_fist]),
            Finger([Cartesian3D(0, 0, 0)]),
        )

        self.hand_lines["thumb"] = Line3D(Cartesian3D(0, 0, 0), thumb_folded)
        self.hand_lines["pointer"] = Line3D(Cartesian3D(0, 0, 0), pointer_fist)
        self.hand_lines["middle"] = Line3D(Cartesian3D(0, 0, 0), middle_fist)
        self.hand_lines["ring"] = Line3D(Cartesian3D(0, 0, 0), ring_fist)
        self.hand_lines["pinky"] = Line3D(Cartesian3D(0, 0, 0), pinky_fist)

        return True

    def isCalibrated(self) -> bool:
        return (
            self.hand_lines["thumb"] is not None
            and self.hand_lines["pointer"] is not None
            and self.hand_lines["middle"] is not None
            and self.hand_lines["ring"] is not None
            and self.hand_lines["pinky"] is not None
        )

    def thumbIsStreaming(self):
        return self.thumb().timeSinceLastUpdate() < 1

    def pointerIsStreaming(self):
        return self.pointer().timeSinceLastUpdate() < 1

    def middleIsStreaming(self):
        return self.middle().timeSinceLastUpdate() < 1

    def ringIsStreaming(self):
        return self.ring().timeSinceLastUpdate() < 1

    def pinkyIsStreaming(self):
        return self.pinky().timeSinceLastUpdate() < 1

    def palmIsStreaming(self):
        return self.palm().timeSinceLastUpdate() < 1


class SingleJointLinearDistanceToPalmController(
    SingleJointLinearApproximationPalmRelativePositioningController
):
    def __init__(
        self,
        thumb: IIMUSpatialTracker,
        pointer: IIMUSpatialTracker,
        middle: IIMUSpatialTracker,
        ring: IIMUSpatialTracker,
        pinky: IIMUSpatialTracker,
        palm: IIMUSpatialTracker,
        linear_sensor_calibrator: ILinearCalibratorInterface,
    ):
        super().__init__(
            thumb, pointer, middle, ring, pinky, palm, linear_sensor_calibrator
        )

    def hand(self) -> Hand:
        if not self.isCalibrated():
            raise Exception("hand not calibrated yet")
        current_hand = self.iha.hand()

        coordinates = {
            "thumb": current_hand.thumb()
            .joints()[0] - current_hand.palm().joints()[0],
            "pointer": current_hand.pointer()
            .joints()[0] - current_hand.palm().joints()[0],
            "middle": current_hand.middle()
            .joints()[0] - current_hand.palm().joints()[0],
            "ring": current_hand.ring()
            .joints()[0] - current_hand.palm().joints()[0],
            "pinky": current_hand.pinky()
            .joints()[0] - current_hand.palm().joints()[0],
        }

        rounded_hand = Hand(
            Finger([coordinates["thumb"]]),
            Finger([coordinates["pointer"]]),
            Finger([coordinates["middle"]]),
            Finger([coordinates["ring"]]),
            Finger([coordinates["pinky"]]),
            Finger([Cartesian3D(0, 0, 0)]),
        )

        return rounded_hand

    def motorPositionPercentages(self) -> Dict[str, float]:
        """
        fist is 1, outstretched is 0, everything else somewhere in between
        calculated as the distance from the palm imu
        :return: dictionary of motor positions for each finger
        """
        current_hand = self.hand()
        to_return = {}
        for k in self.hand_lines.keys():
            to_return[k] = (
                current_hand[k].joints()[0].distance(current_hand.palm().joints()[0])
                / self.hand_lines[k].length()
            )
        return to_return
