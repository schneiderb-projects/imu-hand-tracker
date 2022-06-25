import os
from time import sleep
from typing import Dict

from PyQt5.QtCore import QThread, Qt
from PyQt5.QtWidgets import QMainWindow, QListWidget
from PyQt5.QtWidgets import QCheckBox

from app.plotters.plotter_utils import (
    PlotPositionControllerData2D,
    PlotPositioningControllerEnum,
    PlotData3D,
)
from calibration.linear_calibration_interface import IQtCalibratorInterface
from imu.imu_interface import IIMU
from app.plotters.Plot2D import Plot2D
from app.plotters.Plot3D import Plot3D, Plot3DWindow
from positioning_control.positioning_controller import (
    IPositioningController,
)

os.system("./generate_new_imu_gui.sh")
from app.imu_gui import Ui_MainWindow


class Window(QMainWindow, Ui_MainWindow):
    def __init__(
        self,
        positioning_controller: IPositioningController,
        thumb_imu: IIMU,
        pointer_imu: IIMU,
        middle_imu: IIMU,
        ring_imu: IIMU,
        pinky_imu: IIMU,
        palm_imu: IIMU,
        calibrator: IQtCalibratorInterface = None,
        parent=None,
    ):
        super().__init__(parent)

        self.thumb_imu: IIMU = thumb_imu
        self.pointer_imu: IIMU = pointer_imu
        self.middle_imu: IIMU = middle_imu
        self.ring_imu: IIMU = ring_imu
        self.pinky_imu: IIMU = pinky_imu
        self.palm_imu: IIMU = palm_imu

        self.imu_datapoints: Dict[str, int] = {}
        self.current_selected_imu = None

        self.positioning_controller = positioning_controller
        self.setupUi(self)
        self.setupButtons()
        self.setupPlotTabSignals()
        self.beginCalibratedCheckboxLoop()
        self.beginConnectionCheckLoop()

        if calibrator is not None:
            calibrator.set_qt_interface(self.btn_next, self.textBrowser_system_messages)

    def setupPlotTabSignals(self):
        def toInt(string: str):
            try:
                toReturn = int(string)
                return toReturn
            except ValueError:
                self.lineEdit_data_points.setText(
                    "Invalid entry: " + self.lineEdit_data_points.text()
                )
                return None

        def save_new_data_points():
            asInt = toInt(self.lineEdit_data_points.text())
            if asInt is None:
                return

            if self.current_selected_imu is not None:
                self.imu_datapoints[self.current_selected_imu] = asInt
            self.lineEdit_data_points.clearFocus()

        def listWidget_text_changed(listWidget: QListWidget, text: str):
            if listWidget.isActiveWindow() and text != "":
                self.lineEdit_data_points.setText(str(self.imu_datapoints[text]))
                self.current_selected_imu = text

        self.listWidget_select.currentTextChanged.connect(
            lambda text: listWidget_text_changed(self.listWidget_select, text)
        )

        self.listWidget_selected.currentTextChanged.connect(
            lambda text: listWidget_text_changed(self.listWidget_selected, text)
        )
        self.btn_save_data_points.clicked.connect(save_new_data_points)
        self.lineEdit_data_points.returnPressed.connect(save_new_data_points)

    def setupButtons(self):
        def launch_calibrate():
            thread = QThread(self)
            thread.run = self.positioning_controller.calibrate
            thread.start()

        self.btn_calibrate.clicked.connect(launch_calibrate)
        self.btn_plot_2d.clicked.connect(self.runPlot2D)
        self.btn_plot_3d.clicked.connect(self.runPlot3D)

    def addImuToListWidget(self, imu: str):
        if (
            len(self.listWidget_select.findItems(imu + " acc", Qt.MatchExactly))
            + len(self.listWidget_selected.findItems(imu + " acc", Qt.MatchExactly))
            == 0
        ):
            self.listWidget_select.addItem(imu + " acc")
            self.imu_datapoints[imu + " acc"] = 100

            self.listWidget_select.addItem(imu + " pos")
            self.imu_datapoints[imu + " pos"] = 100

            self.listWidget_select.addItem(imu + " gyro")
            self.imu_datapoints[imu + " gyro"] = 100

    def removeImuToListWidget(self, imu: str):
        def findListWidgetIndexByText(listWidget: QListWidget, title: str):
            return listWidget.row(listWidget.findItems(title, Qt.MatchExactly)[0])

        if len(self.listWidget_select.findItems(imu + " acc", Qt.MatchExactly)) > 0:
            self.listWidget_select.takeItem(
                findListWidgetIndexByText(self.listWidget_select, imu + " acc")
            )
        if len(self.listWidget_select.findItems(imu + " pos", Qt.MatchExactly)) > 0:
            self.listWidget_select.takeItem(
                findListWidgetIndexByText(self.listWidget_select, imu + " pos")
            )
        if len(self.listWidget_select.findItems(imu + " gyro", Qt.MatchExactly)) > 0:
            self.listWidget_select.takeItem(
                findListWidgetIndexByText(self.listWidget_select, imu + " gyro")
            )

        if len(self.listWidget_selected.findItems(imu + " acc", Qt.MatchExactly)) > 0:
            self.listWidget_selected.takeItem(
                findListWidgetIndexByText(self.listWidget_selected, imu + " acc")
            )
        if len(self.listWidget_selected.findItems(imu + " pos", Qt.MatchExactly)) > 0:
            self.listWidget_selected.takeItem(
                findListWidgetIndexByText(self.listWidget_selected, imu + " pos")
            )
        if len(self.listWidget_selected.findItems(imu + " gyro", Qt.MatchExactly)) > 0:
            self.listWidget_selected.takeItem(
                findListWidgetIndexByText(self.listWidget_selected, imu + " gyro")
            )

    def runPlot2D(self):
        plotsData = []

        def determine_type(text: str) -> PlotPositioningControllerEnum:
            if "acc" in text:
                return PlotPositioningControllerEnum.ACCELERATION
            elif "pos" in text:
                return PlotPositioningControllerEnum.POSITION
            elif "gyro" in text:
                return PlotPositioningControllerEnum.GYRO
            raise Exception("uh oh don't know what kinda plot that is: " + str(text))

        for x in [
            self.listWidget_selected.item(x)
            for x in range(self.listWidget_selected.count())
        ]:
            if "thumb" in x.text():
                plotsData.append(
                    PlotPositionControllerData2D(
                        self.positioning_controller,
                        self.thumb_imu,
                        self.pointer_imu,
                        self.middle_imu,
                        self.ring_imu,
                        self.pinky_imu,
                        self.palm_imu,
                        thumb_curves=[determine_type(x.text())],
                        points_to_plot=self.imu_datapoints[x.text()],
                    )
                )
            if "pointer" in x.text():
                plotsData.append(
                    PlotPositionControllerData2D(
                        self.positioning_controller,
                        self.thumb_imu,
                        self.pointer_imu,
                        self.middle_imu,
                        self.ring_imu,
                        self.pinky_imu,
                        self.palm_imu,
                        pointer_curves=[determine_type(x.text())],
                        points_to_plot=self.imu_datapoints[x.text()],
                    )
                )
            if "middle" in x.text():
                plotsData.append(
                    PlotPositionControllerData2D(
                        self.positioning_controller,
                        self.thumb_imu,
                        self.pointer_imu,
                        self.middle_imu,
                        self.ring_imu,
                        self.pinky_imu,
                        self.palm_imu,
                        middle_curves=[determine_type(x.text())],
                        points_to_plot=self.imu_datapoints[x.text()],
                    )
                )
            if "ring" in x.text():
                plotsData.append(
                    PlotPositionControllerData2D(
                        self.positioning_controller,
                        self.thumb_imu,
                        self.pointer_imu,
                        self.middle_imu,
                        self.ring_imu,
                        self.pinky_imu,
                        self.palm_imu,
                        ring_curves=[determine_type(x.text())],
                        points_to_plot=self.imu_datapoints[x.text()],
                    )
                )
            if "pinky" in x.text():
                plotsData.append(
                    PlotPositionControllerData2D(
                        self.positioning_controller,
                        self.thumb_imu,
                        self.pointer_imu,
                        self.middle_imu,
                        self.ring_imu,
                        self.pinky_imu,
                        self.palm_imu,
                        pinky_curves=[determine_type(x.text())],
                        points_to_plot=self.imu_datapoints[x.text()],
                    )
                )
            if "palm" in x.text():
                plotsData.append(
                    PlotPositionControllerData2D(
                        self.positioning_controller,
                        self.thumb_imu,
                        self.pointer_imu,
                        self.middle_imu,
                        self.ring_imu,
                        self.pinky_imu,
                        self.palm_imu,
                        palm_curves=[determine_type(x.text())],
                        points_to_plot=self.imu_datapoints[x.text()],
                    )
                )

        plot2d = Plot2D(
            plotsData=plotsData,
            parent=self,
        )
        plot2d.begin()

    def runPlot3D(self):
        p3dw = Plot3DWindow(
            Plot3D(PlotData3D(self.positioning_controller)), parent=self
        )
        p3dw.begin()

    def beginCalibratedCheckboxLoop(self):
        def checkboxLoop():
            self.checkBox_calibrated.setChecked(
                self.positioning_controller.isCalibrated()
            )
            sleep(1)

        thread = QThread(self)
        thread.run = checkboxLoop
        thread.finished.connect(self.beginCalibratedCheckboxLoop)
        thread.start()

    def beginConnectionCheckLoop(self):
        def change_and_add_remove_from_selectables(
            checkbox: QCheckBox, is_streaming: str, name: str
        ):
            previous = checkbox.isChecked()
            checkbox.setChecked(is_streaming)
            if not previous and is_streaming:
                self.addImuToListWidget(name)

            if previous and not is_streaming:
                self.removeImuToListWidget(name)

        def checkboxLoop():
            change_and_add_remove_from_selectables(
                self.checkBox_thumb,
                self.positioning_controller.thumbIsStreaming(),
                "thumb",
            )
            change_and_add_remove_from_selectables(
                self.checkBox_pointer,
                self.positioning_controller.pointerIsStreaming(),
                "pointer",
            )
            change_and_add_remove_from_selectables(
                self.checkBox_middle,
                self.positioning_controller.middleIsStreaming(),
                "middle",
            )
            change_and_add_remove_from_selectables(
                self.checkBox_ring,
                self.positioning_controller.ringIsStreaming(),
                "ring",
            )
            change_and_add_remove_from_selectables(
                self.checkBox_pinky,
                self.positioning_controller.pinkyIsStreaming(),
                "pinky",
            )
            change_and_add_remove_from_selectables(
                self.checkBox_palm,
                self.positioning_controller.palmIsStreaming(),
                "palm",
            )
            sleep(1)

        thread = QThread(self)
        thread.run = checkboxLoop
        thread.finished.connect(self.beginConnectionCheckLoop)
        thread.start()
