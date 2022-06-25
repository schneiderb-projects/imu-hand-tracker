import time
from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Union, Dict

import numpy as np
from numpy import pi, sin, cos

from hand_.hand import Hand
from imu.imu_interface import IIMU
from imu.imu_spatial_tracker import IIMUSpatialTracker
from positioning_control.positioning_controller import IPositioningController
from shared.shared_utils import SensorCoordinate, Cartesian3D


class IPlotData3D(ABC):
    @abstractmethod
    def getUpdate(self) -> List[List[Cartesian3D]]:
        raise NotImplemented

    @abstractmethod
    def title(self) -> str:
        raise NotImplemented

    @abstractmethod
    def curveTitles(self) -> [str]:
        raise NotImplemented

    @abstractmethod
    def y_axis_label(self) -> str:
        raise NotImplemented

    @abstractmethod
    def x_axis_label(self) -> str:
        raise NotImplemented

    @abstractmethod
    def z_axis_label(self) -> str:
        raise NotImplemented


class IPlotData2D(ABC):
    @abstractmethod
    def getUpdate(self) -> List[Union[SensorCoordinate, List[SensorCoordinate]]]:
        raise NotImplemented

    @abstractmethod
    def title(self) -> str:
        raise NotImplemented

    @abstractmethod
    def curveTitles(self) -> [str]:
        raise NotImplemented

    @abstractmethod
    def dataPointsToPlot(self) -> int:
        raise NotImplemented

    @abstractmethod
    def y_axis_labels(self) -> str:
        raise NotImplemented

    @abstractmethod
    def x_axis_labels(self) -> str:
        raise NotImplemented


class PlotPositioningControllerEnum(Enum):
    ACCELERATION = 0
    GYRO = 1
    POSITION = 2


class PlotPositionControllerData2D(IPlotData2D):
    def __init__(
        self,
        positioningController: IPositioningController,
        thumb_imu: IIMU,
        pointer_imu: IIMU,
        middle_imu: IIMU,
        ring_imu: IIMU,
        pinky_imu: IIMU,
        palm_imu: IIMU,
        thumb_curves: List[PlotPositioningControllerEnum] = [],
        pointer_curves: List[PlotPositioningControllerEnum] = [],
        middle_curves: List[PlotPositioningControllerEnum] = [],
        ring_curves: List[PlotPositioningControllerEnum] = [],
        pinky_curves: List[PlotPositioningControllerEnum] = [],
        palm_curves: List[PlotPositioningControllerEnum] = [],
        points_to_plot=100,
    ):
        self.positioningController: IPositioningController = positioningController

        self.thumb_imu: IIMU = thumb_imu
        self.pointer_imu: IIMU = pointer_imu
        self.middle_imu: IIMU = pointer_imu
        self.ring_imu: IIMU = thumb_imu
        self.pinky_imu: IIMU = pointer_imu
        self.palm_imu: IIMU = thumb_imu

        self.imus: Dict[str, IIMU] = {
            "thumb": thumb_imu,
            "pointer": pointer_imu,
            "middle": middle_imu,
            "ring": ring_imu,
            "pinky": pinky_imu,
            "palm": palm_imu,
        }
        self.plots: Dict[str, List[PlotPositioningControllerEnum]] = {
            "thumb": thumb_curves,
            "pointer": pointer_curves,
            "middle": middle_curves,
            "ring": ring_curves,
            "pinky": pinky_curves,
            "palm": palm_curves,
        }
        self.imus_spatial_trackers: Dict[str, IIMUSpatialTracker] = {
            "thumb": self.positioningController.thumb(),
            "pointer": self.positioningController.pointer(),
            "middle": self.positioningController.middle(),
            "ring": self.positioningController.ring(),
            "pinky": self.positioningController.pinky(),
            "palm": self.positioningController.palm(),
        }
        self.points_to_plot = points_to_plot
        self.initialTime = time.time()
        self.titles: List[str] = []
        self._title = ""

        for key in self.plots.keys():
            if PlotPositioningControllerEnum.POSITION in self.plots[key]:
                self.titles.append("pos x")
                self.titles.append("pos y")
                self.titles.append("pos z")
                self._title += ("" if self._title == "" else ",  ") + key + " position"

            if PlotPositioningControllerEnum.ACCELERATION in self.plots[key]:
                self.titles.append("acc x")
                self.titles.append("acc y")
                self.titles.append("acc z")
                self._title += (
                    ("" if self._title == "" else ",  ") + key + " acceleration"
                )

            if PlotPositioningControllerEnum.GYRO in self.plots[key]:
                self.titles.append("roll")
                self.titles.append("pitch")
                self.titles.append("yaw")
                self._title += ("" if self._title == "" else ",  ") + key + " gyro"

        self._title += " vs. time (s)"

    def getUpdate(self) -> List[Union[SensorCoordinate, List[SensorCoordinate]]]:
        start = time.time()
        toReturn: List[Union[SensorCoordinate, List[SensorCoordinate]]] = []
        for key in self.plots.keys():
            if PlotPositioningControllerEnum.POSITION in self.plots[key]:
                position = self.imus_spatial_trackers[key].position()
                t = time.time() - self.initialTime
                toReturn.append(position.x())
                toReturn.append(position.y())
                toReturn.append(position.z())

            if PlotPositioningControllerEnum.ACCELERATION in self.plots[key]:
                acc = self.imus[key].acceleration()
                toReturn.append(
                    SensorCoordinate(acc.x()[-1].time(), acc.x()[-1].value())
                )
                toReturn.append(
                    SensorCoordinate(acc.y()[-1].time(), acc.y()[-1].value())
                )
                toReturn.append(
                    SensorCoordinate(acc.z()[-1].time(), acc.z()[-1].value())
                )

            if PlotPositioningControllerEnum.GYRO in self.plots[key]:
                angle = self.imus_spatial_trackers[key].angle()
                t = time.time() - self.initialTime
                toReturn.append(SensorCoordinate(t, angle.roll()))
                toReturn.append(SensorCoordinate(t, angle.pitch()))
                toReturn.append(SensorCoordinate(t, angle.yaw()))

        # print("get update: " + str(time.time() - start))

        return toReturn

    def title(self) -> str:
        return self._title

    def curveTitles(self) -> [str]:
        return self.titles

    def dataPointsToPlot(self) -> int:
        return self.points_to_plot

    def y_axis_labels(self) -> str:
        return "magnitude"

    def x_axis_labels(self) -> str:
        return "time (s)"


def periodic_position_function(x, scalar, delay):
    if x < 4 * pi * delay:
        return 0

    if x % (4 * pi) < 2 * pi:
        return sin(x) * scalar
    else:
        return -sin(x) * scalar


class PlotData3D(IPlotData3D):
    def __init__(self, positioning_controller: IPositioningController):
        self.positioning_controller = positioning_controller

    def getUpdate(self) -> List[List[Cartesian3D]]:
        hand: Hand = self.positioning_controller.hand()
        return [
            [hand.palm().joints()[0], hand.thumb().joints()[0]],
            [hand.palm().joints()[0], hand.pointer().joints()[0]],
            [hand.palm().joints()[0], hand.middle().joints()[0]],
            [hand.palm().joints()[0], hand.ring().joints()[0]],
            [hand.palm().joints()[0], hand.pinky().joints()[0]],
        ]

    def title(self) -> str:
        raise NotImplemented

    def curveTitles(self) -> [str]:
        return [
            "palm -> thumb",
            "palm -> pointer",
            "palm -> middle",
            "palm -> ring",
            "palm -> pinky",
        ]

    def y_axis_label(self) -> str:
        raise NotImplemented

    def x_axis_label(self) -> str:
        raise NotImplemented

    def z_axis_label(self) -> str:
        raise NotImplemented
