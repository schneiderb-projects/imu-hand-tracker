import sys
from abc import ABC
from datetime import time
from typing import List, Union

import numpy as np

from calibration.mock_calibrators import LinearCalibratorRandomDelay
from app.plotters.Plot2D import Plot2D
from app.plotters.Plot3D import Plot3D, Plot3DWindow
from pyqtgraph.Qt import QtWidgets

from app.plotters.plotter_utils import (
    IPlotData2D,
    PlotPositionControllerData2D,
    PlotPositioningControllerEnum,
    periodic_position_function,
    PlotData3D,
)
from imu.imu_spatial_tracker import IMUSpatialTracker
from imu.imu_receivers.mock_imu import FunctionIMU
from positioning_control.positioning_controller import (
    SingleJointLinearApproximationPalmRelativePositioningController,
)
from shared.shared_utils import SensorCoordinate
import time


def test_plot2DWithPeriodicIMUs():
    app = QtWidgets.QApplication(sys.argv)
    func_x = lambda x: periodic_position_function(x, 20, 1)
    func_y = lambda x: periodic_position_function(x, -20, 1)
    func_z = lambda x: 0

    imus = [
        FunctionIMU(func_x, func_y, func_z),
        FunctionIMU(func_x, func_y, func_z),
        FunctionIMU(func_x, func_y, func_z),
        FunctionIMU(func_x, func_y, func_z),
        FunctionIMU(func_x, func_y, func_z),
        FunctionIMU(func_x, func_y, func_z),
    ]

    sjlprpc = SingleJointLinearApproximationPalmRelativePositioningController(
        IMUSpatialTracker(imus[0]),
        IMUSpatialTracker(imus[1]),
        IMUSpatialTracker(imus[2]),
        IMUSpatialTracker(imus[3]),
        IMUSpatialTracker(imus[4]),
        IMUSpatialTracker(imus[5]),
        LinearCalibratorRandomDelay(),
    )
    sjlprpc.calibrate()
    plot2d = Plot2D(
        plotsData=[
            PlotPositionControllerData2D(
                sjlprpc,
                imus[0],
                imus[1],
                imus[2],
                imus[3],
                imus[4],
                imus[5],
                thumb_curves=[
                    PlotPositioningControllerEnum.ACCELERATION,
                    PlotPositioningControllerEnum.POSITION,
                ],
                points_to_plot=500,
            )
            # PlotDataPositionController2D(sjlprpc, pinky_curves=[PlotPositioningControllerEnum.GYRO]),
            # PlotDataPositionController2D(sjlprpc, middle_curves=[PlotPositioningControllerEnum.POSITION])
        ]
    )
    plot2d.begin()
    sys.exit(app.exec_())


def test_plot2DSinPlots():
    app = QtWidgets.QApplication(sys.argv)
    plot2d = Plot2D(plotsData=[SinPlotData(4, 7, 200)] * 3)
    plot2d.begin()
    plot2d.show()
    sys.exit(app.exec_())


class SinPlotData(IPlotData2D, ABC):
    def __init__(self, curves: int, x_scalar: float, numDataPoints: int):
        self.x_scalar = x_scalar
        self.curves: int = curves
        self.numDataPoints: int = numDataPoints
        self.start = time.time()
        self._y_axis_labels: List[str] = []
        for x in range(curves):
            self._y_axis_labels.append("y values - plot #" + str(x))

    def getUpdate(self) -> List[Union[SensorCoordinate, List[SensorCoordinate]]]:
        toReturn: List[Union[SensorCoordinate, List[SensorCoordinate]]] = []
        t = time.time() - self.start
        for i in range(self.curves):
            toReturn.append(
                [
                    SensorCoordinate(t, np.sin(t * self.x_scalar) + i),
                    SensorCoordinate(
                        t + 0.000001, np.sin((t + 0.000001) * self.x_scalar) + i
                    ),
                ]
            )

        return toReturn

    def title(self) -> str:
        return str(self.curves) + " Sin Plot"

    def curveTitles(self) -> [str]:
        toreturn = []
        for x in range(self.curves):
            toreturn.append(str(x))

        return toreturn

    def dataPointsToPlot(self) -> int:
        return self.numDataPoints

    def y_axis_labels(self) -> str:
        return "magnitude"

    def x_axis_labels(self) -> str:
        return "time (s)"


def test_plot3DRandomData():
    p3d = Plot3D(PlotData3D())

    app = QtWidgets.QApplication(sys.argv)
    w = Plot3DWindow(p3d)
    w.begin()
    # this example sometimes throws SIGABRT when closing. Not really a problem, I just don't kill "thread" correctly,
    # but its not really relevant, so I'm just ignore it.
    sys.exit(app.exec_())


if __name__ == "__main__":
    # test_plot2DSinPlots()
    # test_plot3DRandomData()
    test_plot2DWithPeriodicIMUs()
