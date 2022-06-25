import time
from abc import ABC
from typing import Union

from calibration.linear_calibration_interface import ILinearCalibratorInterface
from PyQt5 import QtWidgets


class IQtCalibratorInterface(ILinearCalibratorInterface, ABC):
    def set_qt_interface(
        self, continue_button: QtWidgets.QPushButton, text_display: QtWidgets.QTextEdit
    ):
        raise NotImplemented


class QtCalibrator(IQtCalibratorInterface):
    def __init__(self):
        self._next = False
        self.text_display: Union[None, QtWidgets.QTextEdit] = None

    def set_qt_interface(
        self, continue_button: QtWidgets.QPushButton, text_display: QtWidgets.QTextEdit
    ):
        continue_button.clicked.connect(self.next)
        self.text_display = text_display

    def next(self):
        self._next = True

    def make_fist(self):
        self.text_display.append("Calibration Message: Make fist\n")
        while not self._next:
            time.sleep(0.01)
        self._next = False

    def outstretch_hand(self):
        self.text_display.append("Calibration Message: Outstretch fingers\n")
        while not self._next:
            time.sleep(0.01)
        self._next = False

    def fold_thumb(self):
        self.text_display.append("Calibration Message: Fold thumb\n")
        while not self._next:
            time.sleep(0.01)
        self._next = False

    def finished(self):
        self.text_display.append("Calibration Message: Calibration complete\n")
