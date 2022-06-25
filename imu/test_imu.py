import time

from imu.imu_angle_tracker import IMUAngleTracker
from imu.imu_position_tracker import (
    TrackPositionFromAcceleration,
    IMUPositionTracker,
)
from imu.imu_spatial_tracker import IMUSpatialTracker, IIMUSpatialTracker
from imu.imu_utils import SensorCoordinate, AccelerationXYZ, GyroEuler
from imu.imu_receivers.mock_imu import MockIMU
from shared.shared_utils import EulerAngle, Cartesian3D, Line2DFrom2Points


def testTrackPositionFromAcceleration():
    pos = TrackPositionFromAcceleration()
    pos.update(SensorCoordinate(0, 0))
    pos.update(SensorCoordinate(1, 2))

    expected_vel = Line2DFrom2Points(0, 0, 1, 2).bounded_integral(0, 1)
    expected_pos = (
        Line2DFrom2Points(0, 0, 1, 2)
        .integral(known_coordinate=(0, 0))
        .bounded_integral(0, 1)
    )
    assert pos.delta().value() == expected_pos

    pos.update(SensorCoordinate(2, 2))

    # double integral of mx + b = (b*x**2)/2 + (m*x**3)/6
    expected_vel += Line2DFrom2Points(1, 2, 2, 2).bounded_integral(1, 2)
    expected_pos += (
        Line2DFrom2Points(1, 2, 2, 2)
        .integral(known_coordinate=(2, expected_vel))
        .bounded_integral(1, 2)
    )
    assert pos.delta().value() == expected_pos
    pos.update(SensorCoordinate(3, 3))
    expected_vel += Line2DFrom2Points(2, 2, 3, 3).bounded_integral(2, 3)
    expected_pos += (
        Line2DFrom2Points(2, 2, 3, 3)
        .integral(known_coordinate=(3, expected_vel))
        .bounded_integral(2, 3)
    )
    assert pos.delta().value() == expected_pos
    pos.update(SensorCoordinate(4, 0))
    expected_vel += Line2DFrom2Points(3, 3, 4, 0).bounded_integral(3, 4)
    expected_pos += (
        Line2DFrom2Points(3, 3, 4, 0)
        .integral(known_coordinate=(4, expected_vel))
        .bounded_integral(3, 4)
    )
    assert pos.delta().value() == expected_pos
    pos.update(SensorCoordinate(5, -1))
    expected_vel += Line2DFrom2Points(4, 0, 5, -1).bounded_integral(4, 5)
    expected_pos += (
        Line2DFrom2Points(4, 0, 5, -1)
        .integral(known_coordinate=(5, expected_vel))
        .bounded_integral(4, 5)
    )
    assert pos.delta() == SensorCoordinate(5, expected_pos)
    pos.update(SensorCoordinate(6, 9))
    expected_vel += Line2DFrom2Points(5, -1, 6, 9).bounded_integral(5, 6)
    expected_pos += (
        Line2DFrom2Points(5, -1, 6, 9)
        .integral(known_coordinate=(6, expected_vel))
        .bounded_integral(5, 6)
    )
    assert pos.delta().value() == expected_pos

    pos.zero()
    assert pos.delta() == SensorCoordinate(6, 0)
    print("TrackPositionFromAcceleration asserts passed")


def testIMUPositionTracker():
    mock_imu = MockIMU()
    acc = AccelerationXYZ()
    ipt = IMUPositionTracker(mock_imu)

    acc.update_x(SensorCoordinate(1, 2))
    acc.update_y(SensorCoordinate(1, 2))
    acc.update_z(SensorCoordinate(1, 2))
    mock_imu.update(acceleration=acc)

    ipt.zero()

    acc.update_x(SensorCoordinate(2, 2))
    acc.update_y(SensorCoordinate(2, 2))
    acc.update_z(SensorCoordinate(2, 2))
    mock_imu.update(acceleration=acc)

    expected_vel = Line2DFrom2Points(1, 2, 2, 2).bounded_integral(1, 2)
    expected_pos = (
        Line2DFrom2Points(1, 2, 2, 2)
        .integral(known_coordinate=(1, 0))
        .bounded_integral(1, 2)
    )
    assert ipt.delta().toCartesian3D() == Cartesian3D(
        expected_pos, expected_pos, expected_pos
    )

    expected_vel += Line2DFrom2Points(2, 2, 3, 3).bounded_integral(2, 3)
    expected_pos += (
        Line2DFrom2Points(2, 2, 3, 3)
        .integral(known_coordinate=(3, expected_vel))
        .bounded_integral(2, 3)
    )
    acc.update(3, 3, 3, 3)
    mock_imu.update(acceleration=acc)
    assert ipt.delta().toCartesian3D() == Cartesian3D(
        expected_pos, expected_pos, expected_pos
    )

    acc.update_x(SensorCoordinate(4, 0))
    acc.update_y(SensorCoordinate(4, 0))
    acc.update_z(SensorCoordinate(4, 0))
    mock_imu.update(acceleration=acc)
    expected_vel += Line2DFrom2Points(3, 3, 4, 0).bounded_integral(3, 4)
    expected_pos += (
        Line2DFrom2Points(3, 3, 4, 0)
        .integral(known_coordinate=(4, expected_vel))
        .bounded_integral(3, 4)
    )
    assert ipt.delta().toCartesian3D() == Cartesian3D(
        expected_pos, expected_pos, expected_pos
    )

    acc.update_x(SensorCoordinate(5, -1))
    acc.update_y(SensorCoordinate(5, -1))
    acc.update_z(SensorCoordinate(5, -1))
    mock_imu.update(acceleration=acc)
    expected_vel += Line2DFrom2Points(4, 0, 5, -1).bounded_integral(4, 5)
    expected_pos += (
        Line2DFrom2Points(4, 0, 5, -1)
        .integral(known_coordinate=(5, expected_vel))
        .bounded_integral(4, 5)
    )
    assert ipt.delta().toCartesian3D() == Cartesian3D(
        expected_pos, expected_pos, expected_pos
    )

    acc.update_x(SensorCoordinate(6, 9))
    acc.update_y(SensorCoordinate(6, -3))
    acc.update_z(SensorCoordinate(6, -2))
    mock_imu.update(acceleration=acc)

    expected_pos_x = expected_pos + Line2DFrom2Points(5, -1, 6, 9).integral(
        known_coordinate=(5, expected_vel)
    ).bounded_integral(5, 6)
    expected_pos_y = expected_pos + Line2DFrom2Points(5, -1, 6, -3).integral(
        known_coordinate=(5, expected_vel)
    ).bounded_integral(5, 6)
    expected_pos_z = expected_pos + Line2DFrom2Points(5, -1, 6, -2).integral(
        known_coordinate=(5, expected_vel)
    ).bounded_integral(5, 6)

    assert ipt.delta().toCartesian3D() == Cartesian3D(
        expected_pos_x,
        expected_pos_y,
        expected_pos_z,
    )

    ipt.zero()

    assert ipt.delta().toCartesian3D() == Cartesian3D(0, 0, 0)

    print("SensorCoordinate asserts passed")


def testSensorCoordinate():
    gyro = GyroEuler()
    gyro.update_roll(SensorCoordinate(0, 0))
    gyro.update_pitch(SensorCoordinate(0, 1))
    gyro.update_yaw(SensorCoordinate(0, 2))

    assert SensorCoordinate(0, 0) == SensorCoordinate(0, 0)
    assert gyro.angles()["roll"] == [SensorCoordinate(0, 0)]
    assert gyro.angles()["pitch"] == [SensorCoordinate(0, 1)]
    assert gyro.angles()["yaw"] == [SensorCoordinate(0, 2)]

    print("IMUPositionTracker asserts passed")


def testIMUGyroTracker():
    mock_imu = MockIMU()
    gyro = GyroEuler()
    igt = IMUAngleTracker(mock_imu)

    gyro.update_roll(SensorCoordinate(0, 0))
    gyro.update_pitch(SensorCoordinate(0, 1))
    gyro.update_yaw(SensorCoordinate(0, 2))

    mock_imu.update(gyro=gyro)

    assert igt.angle() == EulerAngle(0, 1, 2)

    gyro.update(1, 4, 5, 6)
    mock_imu.update(gyro=gyro)

    assert igt.angle() == EulerAngle(4, 5, 6)

    igt.zero()

    assert igt.angle() == EulerAngle(0, 0, 0)

    gyro.update(10, 10, 10, 10)
    mock_imu.update(gyro=gyro)

    assert igt.angle() == EulerAngle(6, 5, 4)

    print("IMUGyroTracker asserts passed")


def testIMUSpatialTracker():
    # Note to self: this function has a 1ms delay in it. it is not just really slow. that's intention.
    mock_imu = MockIMU()
    gyro = GyroEuler()
    acc = AccelerationXYZ()
    ist: IIMUSpatialTracker = IMUSpatialTracker(mock_imu)

    acc.update(1, 2, 2, 2)

    mock_imu.update(acceleration=acc)
    ist.zero_position()

    gyro.update(0, 0, 1, 2)
    acc.update(2, 2, 2, 2)

    mock_imu.update(acceleration=acc, gyro=gyro)

    expected_pos = (
        Line2DFrom2Points(1, 2, 2, 2)
        .integral(known_coordinate=(1, 0))
        .bounded_integral(1, 2)
    )

    assert ist.angle() == EulerAngle(0, 1, 2)
    assert ist.position().toCartesian3D() == Cartesian3D(
        expected_pos, expected_pos, expected_pos
    )

    ist.zero_angle()

    assert ist.angle() == EulerAngle(0, 0, 0)

    ist.zero_position()
    assert ist.position().toCartesian3D() == Cartesian3D(0, 0, 0)

    assert ist.timeSinceLastUpdate() < 0.1

    gyro.update(5, 0, 1, 2)
    acc.update(5, 2, 2, 2)

    time.sleep(0.1)

    assert 0.11 > ist.timeSinceLastUpdate() > 0.1

    print("IMUSpatialTracker asserts passed")


def test():
    testTrackPositionFromAcceleration()
    testIMUPositionTracker()
    testIMUGyroTracker()
    testIMUSpatialTracker()
    testSensorCoordinate()


if __name__ == "__main__":
    test()
