from imu.imu_interface import IIMU
from imu.imu_utils import GyroEuler, AccelerationXYZ


class UDP_IMU(IIMU):
    def begin_udp_server(self):
        pass

    def acceleration(self) -> AccelerationXYZ:
        pass

    def gyro(self) -> GyroEuler:
        pass

