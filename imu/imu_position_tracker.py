import time
from typing import List, Union, Dict, Callable

from imu.imu_interface import IIMU, IMUListener
from imu.imu_utils import AccelerationXYZ, SensorCoordinate
from shared.shared_utils import Cartesian3D, Line2DFrom2Points, SensorCoordinate3D


class IMUPositionTrackerListener:
    def __init__(self, callback: Callable[[], None]):
        self.callback = callback


class IMUPositionTracker:
    def __init__(self, imu: IIMU):
        self.imu: IIMU = imu
        self.imu.subscribe(IMUListener(acceleration_callback=self.update_acceleration))
        self.acceleration: AccelerationXYZ = AccelerationXYZ()
        self._delta_position: Dict[str, Union[TrackPositionFromAcceleration, None]] = {
            "x": TrackPositionFromAcceleration(),
            "y": TrackPositionFromAcceleration(),
            "z": TrackPositionFromAcceleration(),
        }

        self.current_index: Dict[str, int] = {"x": 0, "y": 0, "z": 0}
        self.timeOfLastUpdate = 0

    def delta(self) -> SensorCoordinate3D:
        return SensorCoordinate3D(
            self._delta_position["x"].delta(),
            self._delta_position["y"].delta(),
            self._delta_position["z"].delta(),
        )

    def update_acceleration(self, acceleration: AccelerationXYZ):
        start = time.time()
        self.acceleration = acceleration
        if len(acceleration.x()) != self.current_index["x"]:
            for x in acceleration.x()[self.current_index["x"] : len(acceleration.x())]:
                self._delta_position["x"].update(x)
            self.current_index["x"] = len(acceleration.x())

        if len(acceleration.y()) != self.current_index["y"]:
            for y in acceleration.y()[self.current_index["y"] : len(acceleration.y())]:
                self._delta_position["y"].update(y)
            self.current_index["y"] = len(acceleration.y())

        if len(acceleration.z()) != self.current_index["z"]:
            for z in acceleration.z()[self.current_index["z"] : len(acceleration.z())]:
                self._delta_position["z"].update(z)
            self.current_index["z"] = len(acceleration.z())

        self.timeOfLastUpdate = time.time()

    def zero(self):
        self._delta_position["x"].zero()
        self._delta_position["y"].zero()
        self._delta_position["z"].zero()

    def timeSinceLastUpdate(self):
        return time.time() - self.timeOfLastUpdate


class TrackPositionFromAcceleration:
    def __init__(self):
        self.coordinates: List[SensorCoordinate] = []
        self._delta: SensorCoordinate = SensorCoordinate(0, 0)
        self._velocity: float = 0

    def update(self, additional_coordinates: SensorCoordinate):
        if (
            len(self.coordinates) > 1
            and self.coordinates[-1].time() >= additional_coordinates.time()
        ):
            raise Exception("Time of new coordinates must be strictly increasing")
        self.coordinates.append(additional_coordinates)
        if len(self.coordinates) > 1:
            new_position = self._delta.value() + self.bounded_double_integral_of_line(
                self.coordinates[-2], self.coordinates[-1]
            )
            self._delta = SensorCoordinate(additional_coordinates.time(), new_position)

    def zero(self):
        self._delta = SensorCoordinate(self.coordinates[-1].time(), 0)
        self._velocity = 0

    def delta(self) -> SensorCoordinate:
        return self._delta

    def bounded_double_integral_of_line(
        self, previous_position: SensorCoordinate, current_position: SensorCoordinate
    ) -> float:
        """
        calculate the bounded double integral of the line connecting the 2 coordinates
        :param previous_position: past position, bottom bound of the integral
        :param current_position: current position, top bound of the integral
        :return: the bounded integral of a line connection the 2 coordinates
        """
        # delta  = BoundedIntegral(f[n]) from previous_position.get_time() to current_position.get_time()
        #       = area of triangle on top + area of rectangle on bottom
        #    |
        #    |     -------
        # y  |    /       \      <= linear interpolation of sensor sampled at times a, b, c, d
        #    |----         \         = f(x) => BoundedIntegral(f[n]) from 0 to d = sigma(lines connecting samples)
        #    +---|-|------|-|---
        #        a b      c d
        #           t
        line = Line2DFrom2Points(
            previous_position.time(),
            previous_position.value(),
            current_position.time(),
            current_position.value(),
        )
        # return line.integral().bounded_integral(previous_position.time(), current_position.time())
        self._velocity += line.bounded_integral(
            previous_position.time(), current_position.time()
        )
        return line.integral(
            known_coordinate=(current_position.time(), self._velocity)
        ).bounded_integral(previous_position.time(), current_position.time())


# class IMUPositionTracker:
#     def __init__(self, imu: IIMU):
#         self.imu: IIMU = imu
#         self.imu.subscribe(IMUListener(acceleration_callback=self.update_acceleration))
#         self.acceleration: AccelerationXYZ = AccelerationXYZ()
#         self._delta_position: Dict[str, Union[TrackPositionFromAcceleration, None]] = {
#             "x": TrackPositionFromAcceleration(),
#             "y": TrackPositionFromAcceleration(),
#             "z": TrackPositionFromAcceleration(),
#         }
#
#         self.current_index: Dict[str, int] = {"x": 0, "y": 0, "z": 0}
#         self.lastUpdated = 0
#
#     def delta(self) -> Cartesian3D:
#         return Cartesian3D(
#             self._delta_position["x"].delta(),
#             self._delta_position["y"].delta(),
#             self._delta_position["z"].delta(),
#         )
#
#     def update_acceleration(self, acceleration: AccelerationXYZ):
#         start = time.time()
#         self.acceleration = acceleration
#         if len(acceleration.x()) != self.current_index["x"]:
#             for x in acceleration.x()[self.current_index["x"] : len(acceleration.x())]:
#                 self._delta_position["x"].update(x)
#             self.current_index["x"] = len(acceleration.x())
#
#         if len(acceleration.y()) != self.current_index["y"]:
#             for y in acceleration.y()[self.current_index["y"] : len(acceleration.y())]:
#                 self._delta_position["y"].update(y)
#             self.current_index["y"] = len(acceleration.y())
#
#         if len(acceleration.z()) != self.current_index["z"]:
#             for z in acceleration.z()[self.current_index["z"] : len(acceleration.z())]:
#                 self._delta_position["z"].update(z)
#             self.current_index["z"] = len(acceleration.z())
#
#         self.lastUpdated = time.time()
#
#         # ("update_acc:", time.time() - start)
#
#     def subscribe(self, listener: IMUPositionTrackerListener):
#         pass
#
#     def zero(self):
#         self._delta_position["x"].zero()
#         self._delta_position["y"].zero()
#         self._delta_position["z"].zero()
#
#     def timeSinceLastUpdate(self):
#         return time.time() - self.lastUpdated
# class TrackPositionFromAcceleration:
#     def __init__(self):
#         self.coordinates: List[SensorCoordinate] = []
#         self._delta: float = 0
#         self._velocity: float = 0
#
#     def update(self, additional_coordinates: SensorCoordinate):
#         if (
#             len(self.coordinates) > 1
#             and self.coordinates[-1].time() >= additional_coordinates.time()
#         ):
#             raise Exception("Time of new coordinates must be strictly increasing")
#         self.coordinates.append(additional_coordinates)
#         if len(self.coordinates) > 1:
#             self._delta += self.bounded_double_integral_of_line(
#                 self.coordinates[-2], self.coordinates[-1]
#             )
#
#     def zero(self):
#         self._delta = 0
#         self._velocity = 0
#
#     def delta(self):
#         return self._delta
#
#     def bounded_double_integral_of_line(
#         self, previous_position: SensorCoordinate, current_position: SensorCoordinate
#     ) -> float:
#         """
#         calculate the bounded double integral of the line connecting the 2 coordinates
#         :param previous_position: past position, bottom bound of the integral
#         :param current_position: current position, top bound of the integral
#         :return: the bounded integral of a line connection the 2 coordinates
#         """
#         # delta  = BoundedIntegral(f[n]) from previous_position.get_time() to current_position.get_time()
#         #       = area of triangle on top + area of rectangle on bottom
#         #    |
#         #    |     -------
#         # y  |    /       \      <= linear interpolation of sensor sampled at times a, b, c, d
#         #    |----         \         = f(x) => BoundedIntegral(f[n]) from 0 to d = sigma(lines connecting samples)
#         #    +---|-|------|-|---
#         #        a b      c d
#         #           t
#         line = Line2DFrom2Points(
#             previous_position.time(),
#             previous_position.value(),
#             current_position.time(),
#             current_position.value(),
#         )
#         # return line.integral().bounded_integral(previous_position.time(), current_position.time())
#         self._velocity += line.bounded_integral(
#             previous_position.time(), current_position.time()
#         )
#         return line.integral(
#             known_coordinate=(current_position.time(), self._velocity)
#         ).bounded_integral(previous_position.time(), current_position.time())
