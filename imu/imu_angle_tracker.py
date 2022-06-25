import time

from imu.imu_interface import IIMU, IMUListener
from imu.imu_utils import GyroEuler, EulerAngle


class IMUAngleTracker:
    def __init__(self, imu: IIMU):
        self.imu = imu
        self.imu.subscribe(IMUListener(gyro_callback=self.update_gyro))

        self._angle = EulerAngle(0, 0, 0)
        self._zero_angle = EulerAngle(0, 0, 0)
        self.lastUpdated = 0

    def update_gyro(self, gyro: GyroEuler):
        self._angle = gyro.angle()
        self.lastUpdated = time.time()

    def angle(self) -> EulerAngle:
        return EulerAngle(
            self._angle.roll() - self._zero_angle.roll(),
            self._angle.pitch() - self._zero_angle.pitch(),
            self._angle.yaw() - self._zero_angle.yaw(),
        )

    def zero(self):
        self._zero_angle = EulerAngle(
            self._angle.roll(), self._angle.pitch(), self._angle.yaw()
        )

    def timeSinceLastUpdate(self):
        return time.time() - self.lastUpdated
