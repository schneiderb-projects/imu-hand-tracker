from typing import List

from imu.imu_interface import IIMU


class finger:
    def __init__(self, joints: int, imus: List[IIMU]):
        self._joints = joints
        self._imus = imus

    def getIMUCoordinates(self):
        pass
