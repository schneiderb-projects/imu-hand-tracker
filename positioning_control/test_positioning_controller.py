from numpy import sqrt

from calibration.mock_calibrators import MockLinearCalibrator
from hand_.finger import Finger
from imu.imu_spatial_tracker import MockIMUSpatialTracker
from positioning_control.imu_to_finger_adapter import SingleJointIMUToFingerAdapter
from positioning_control.imus_to_hand_adapter import SingleJoint5FingerIMUToHandAdapter
from positioning_control.positioning_controller import (
    SingleJointLinearApproximationPalmRelativePositioningController, SingleJointLinearDistanceToPalmController,
)
from shared.shared_utils import Cartesian3D


def test_SingleJointIMUToFingerAdapter():
    mist = MockIMUSpatialTracker()
    sjifa = SingleJointIMUToFingerAdapter(mist)

    mist.set_delta_position(Cartesian3D(0, 1, 2))
    assert sjifa.finger() == Finger([Cartesian3D(0, 1, 2)])

    mist.set_delta_position(Cartesian3D(5, 0, 0))
    assert sjifa.finger() == Finger([Cartesian3D(5, 0, 0)])

    print("SingleJointIMUToFingerAdapter asserts passed")


def test_SingleJoint5FingerIMUToHandAdapter():
    thumb = MockIMUSpatialTracker()
    pointer = MockIMUSpatialTracker()
    middle = MockIMUSpatialTracker()
    ring = MockIMUSpatialTracker()
    pinky = MockIMUSpatialTracker()
    palm = MockIMUSpatialTracker()

    sj5fiha = SingleJoint5FingerIMUToHandAdapter(
        thumb, pointer, middle, ring, pinky, palm
    )

    thumb.set_delta_position(Cartesian3D(0, 1, 2))
    pointer.set_delta_position(Cartesian3D(3, 4, 5))
    middle.set_delta_position(Cartesian3D(6, 7, 8))
    ring.set_delta_position(Cartesian3D(9, 10, 11))
    pinky.set_delta_position(Cartesian3D(12, 13, 14))
    palm.set_delta_position(Cartesian3D(15, 16, 17))

    assert sj5fiha.hand().thumb().joints() == [Cartesian3D(0, 1, 2)]
    assert sj5fiha.hand().pointer().joints() == [Cartesian3D(3, 4, 5)]
    assert sj5fiha.hand().middle().joints() == [Cartesian3D(6, 7, 8)]
    assert sj5fiha.hand().ring().joints() == [Cartesian3D(9, 10, 11)]
    assert sj5fiha.hand().pinky().joints() == [Cartesian3D(12, 13, 14)]
    assert sj5fiha.hand().palm().joints() == [Cartesian3D(15, 16, 17)]

    print("SingleJoint5FingerIMUToHandAdapter asserts passed")

def test_SingleJointLinearDistanceToPalmController():
    thumb = MockIMUSpatialTracker()
    pointer = MockIMUSpatialTracker()
    middle = MockIMUSpatialTracker()
    ring = MockIMUSpatialTracker()
    pinky = MockIMUSpatialTracker()
    palm = MockIMUSpatialTracker()

    sjlprpc = SingleJointLinearDistanceToPalmController(
        thumb,
        pointer,
        middle,
        ring,
        pinky,
        palm,
        MockLinearCalibrator(thumb, pointer, middle, ring, pinky, palm),
    )

    assert sjlprpc.thumb() == thumb
    assert sjlprpc.pointer() == pointer
    assert sjlprpc.middle() == middle
    assert sjlprpc.ring() == ring
    assert sjlprpc.pinky() == pinky
    assert sjlprpc.palm() == palm

    thumb.set_delta_position(Cartesian3D(0, 1, 2))
    pointer.set_delta_position(Cartesian3D(3, 4, 5))
    middle.set_delta_position(Cartesian3D(6, 7, 8))
    ring.set_delta_position(Cartesian3D(9, 10, 11))
    pinky.set_delta_position(Cartesian3D(12, 13, 14))
    palm.set_delta_position(Cartesian3D(15, 16, 17))

    sjlprpc.calibrate()

    assert sjlprpc.motorPositionPercentages() == {
        "thumb": 1,
        "pointer": 1,
        "middle": 1,
        "ring": 1,
        "pinky": 1,
    }

    thumb.set_delta_position(Cartesian3D(0, 1, 2))
    pointer.set_delta_position(Cartesian3D(3, 4, 5))
    middle.set_delta_position(Cartesian3D(6, 7, 8))
    ring.set_delta_position(Cartesian3D(9, 10, 11))
    pinky.set_delta_position(Cartesian3D(12, 13, 14))

    assert sjlprpc.motorPositionPercentages() == {
        "thumb": sqrt(1 ** 2 + 2 ** 2) / sqrt(1 + 2 ** 2 + 3 ** 2),
        "pointer": sqrt(3 ** 2 + 4 ** 2 + 5 ** 2) / sqrt(1 + 2 ** 2 + 3 ** 2),
        "middle": sqrt(6 ** 2 + 7 ** 2 + 8 ** 2) / sqrt(1 + 2 ** 2 + 3 ** 2),
        "ring": sqrt(9 ** 2 + 10 ** 2 + 11 ** 2) / sqrt(1 + 2 ** 2 + 3 ** 2),
        "pinky": sqrt(12 ** 2 + 13 ** 2 + 14 ** 2) / sqrt(1 + 2 ** 2 + 3 ** 2),
    }

    palm.set_delta_position(Cartesian3D(1, 2, 3))

    assert sjlprpc.motorPositionPercentages() == {
        "thumb": sqrt((0 - 1) ** 2 + (1 - 2) ** 2 + (2 - 3) ** 2) / sqrt(1 + 2 ** 2 + 3 ** 2),
        "pointer": sqrt((3 - 1) ** 2 + (4 - 2) ** 2 + (5 - 3) ** 2) / sqrt(1 + 2 ** 2 + 3 ** 2),
        "middle": sqrt((6 - 1) ** 2 + (7 - 2) ** 2 + (8 - 3) ** 2) / sqrt(1 + 2 ** 2 + 3 ** 2),
        "ring": sqrt((9 - 1) ** 2 + (10 - 2) ** 2 + (11 - 3) ** 2) / sqrt(1 + 2 ** 2 + 3 ** 2),
        "pinky": sqrt((12 - 1) ** 2 + (13 - 2) ** 2 + (14 - 3) ** 2) / sqrt(1 + 2 ** 2 + 3 ** 2),
    }

    assert sjlprpc.hand().palm().joints()[0] == Cartesian3D(0, 0, 0)
    assert sjlprpc.hand().thumb().joints()[0] == Cartesian3D(0, 1, 2) - Cartesian3D(1, 2, 3)
    assert sjlprpc.hand().pointer().joints()[0] == Cartesian3D(3, 4, 5) - Cartesian3D(1, 2, 3)
    assert sjlprpc.hand().middle().joints()[0] == Cartesian3D(6, 7, 8) - Cartesian3D(1, 2, 3)
    assert sjlprpc.hand().ring().joints()[0] == Cartesian3D(9, 10, 11) - Cartesian3D(1, 2, 3)
    assert sjlprpc.hand().pinky().joints()[0] == Cartesian3D(12, 13, 14) - Cartesian3D(1, 2, 3)



    print("SingleJointLinearPalmRelativePositioningController asserts passed")


def test_SingleJointLinearPalmRelativePositioningController():
    thumb = MockIMUSpatialTracker()
    pointer = MockIMUSpatialTracker()
    middle = MockIMUSpatialTracker()
    ring = MockIMUSpatialTracker()
    pinky = MockIMUSpatialTracker()
    palm = MockIMUSpatialTracker()

    sjlprpc = SingleJointLinearApproximationPalmRelativePositioningController(
        thumb,
        pointer,
        middle,
        ring,
        pinky,
        palm,
        MockLinearCalibrator(thumb, pointer, middle, ring, pinky, palm),
    )

    assert sjlprpc.thumb() == thumb
    assert sjlprpc.pointer() == pointer
    assert sjlprpc.middle() == middle
    assert sjlprpc.ring() == ring
    assert sjlprpc.pinky() == pinky
    assert sjlprpc.palm() == palm

    thumb.set_delta_position(Cartesian3D(0, 1, 2))
    pointer.set_delta_position(Cartesian3D(3, 4, 5))
    middle.set_delta_position(Cartesian3D(6, 7, 8))
    ring.set_delta_position(Cartesian3D(9, 10, 11))
    pinky.set_delta_position(Cartesian3D(12, 13, 14))
    palm.set_delta_position(Cartesian3D(15, 16, 17))

    sjlprpc.calibrate()

    assert sjlprpc.hand()["thumb"] == Finger([Cartesian3D(1, 2, 3)])
    assert sjlprpc.hand()["pointer"] == Finger([Cartesian3D(1, 2, 3)])
    assert sjlprpc.hand()["middle"] == Finger([Cartesian3D(1, 2, 3)])
    assert sjlprpc.hand()["ring"] == Finger([Cartesian3D(1, 2, 3)])
    assert sjlprpc.hand()["pinky"] == Finger([Cartesian3D(1, 2, 3)])

    assert sjlprpc.motorPositionPercentages() == {
        "thumb": 1,
        "pointer": 1,
        "middle": 1,
        "ring": 1,
        "pinky": 1,
    }

    thumb.set_delta_position(Cartesian3D(0, 0, 0))
    pointer.set_delta_position(Cartesian3D(0.5, 1, 1.5))
    middle.set_delta_position(Cartesian3D(0.5 - 2, 1 + 1, 1.5))
    ring.set_delta_position(Cartesian3D(1.0 / 4.0 + 9, 2.0 / 4.0, 3.0 / 4.0 - 3))
    pinky.set_delta_position(Cartesian3D(50, 50, 50))

    assert sjlprpc.hand()["thumb"] == Finger([Cartesian3D(0.0, 0.0, 0.0)])
    assert sjlprpc.hand()["pointer"] == Finger([Cartesian3D(0.5, 1.0, 1.5)])
    assert sjlprpc.hand()["middle"] == Finger([Cartesian3D(0.5, 1.0, 1.5)])
    assert sjlprpc.hand()["ring"] == Finger([Cartesian3D(0.25, 0.5, 0.75)])
    assert sjlprpc.hand()["pinky"] == Finger([Cartesian3D(1, 2, 3)])

    assert sjlprpc.motorPositionPercentages() == {
        "thumb": 0,
        "pointer": 0.5,
        "middle": 0.5,
        "ring": 0.25,
        "pinky": 1,
    }

    ring.set_delta_position(Cartesian3D(-50, -50, -50))

    assert sjlprpc.hand()["ring"] == Finger([Cartesian3D(0, 0, 0)])

    assert sjlprpc.motorPositionPercentages() == {
        "thumb": 0,
        "pointer": 0.5,
        "middle": 0.5,
        "ring": 0,
        "pinky": 1,
    }

    print("SingleJointLinearPalmRelativePositioningController asserts passed")


def test():
    test_SingleJointIMUToFingerAdapter()
    test_SingleJoint5FingerIMUToHandAdapter()
    test_SingleJointLinearPalmRelativePositioningController()
    test_SingleJointLinearDistanceToPalmController()


if __name__ == "__main__":
    test()
