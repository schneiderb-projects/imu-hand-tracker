import sys
from PyQt5.QtWidgets import QApplication

from calibration.qt_calibration_interface import QtCalibrator
from app.main_gui import Window
from app.plotters.plotter_utils import periodic_position_function
from imu.imu_spatial_tracker import IMUSpatialTracker
from imu.imu_receivers.mock_imu import FunctionIMU
from positioning_control.positioning_controller import (
    SingleJointLinearDistanceToPalmController,
)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    func_x = lambda x: periodic_position_function(x, 2, 1)
    func_y = lambda x: periodic_position_function(x, -2, 1)
    func_z = lambda x: periodic_position_function(x, -1, 1)
    imus = [
        FunctionIMU(
            lambda x: periodic_position_function(x, 5, 1),
            lambda x: periodic_position_function(x, -4, 1),
            lambda x: periodic_position_function(x, -3, 1),
        ),
        FunctionIMU(
            lambda x: periodic_position_function(x, -4, 1),
            lambda x: periodic_position_function(x, -3, 1),
            lambda x: periodic_position_function(x, -7, 1),
        ),
        FunctionIMU(
            lambda x: periodic_position_function(x, 1, 1),
            lambda x: periodic_position_function(x, 2, 1),
            lambda x: periodic_position_function(x, 1, 1),
        ),
        FunctionIMU(
            lambda x: periodic_position_function(x, 5, 1),
            lambda x: periodic_position_function(x, 2, 1),
            lambda x: periodic_position_function(x, -1, 1),
        ),
        FunctionIMU(
            lambda x: periodic_position_function(x, 2, 1),
            lambda x: periodic_position_function(x, -2, 1),
            lambda x: periodic_position_function(x, -1, 1),
        ),
        FunctionIMU(lambda x: 0, lambda x: 0, lambda x: 0),
    ]

    qtc = QtCalibrator()
    sjlprpc = SingleJointLinearDistanceToPalmController(
        IMUSpatialTracker(imus[0]),
        IMUSpatialTracker(imus[1]),
        IMUSpatialTracker(imus[2]),
        IMUSpatialTracker(imus[3]),
        IMUSpatialTracker(imus[4]),
        IMUSpatialTracker(imus[5]),
        qtc,
    )
    win = Window(
        sjlprpc, imus[0], imus[1], imus[2], imus[3], imus[4], imus[5], calibrator=qtc
    )
    win.show()
    sys.exit(app.exec())
