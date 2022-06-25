from calibration.linear_calibration_interface import ILinearCalibratorInterface


class LinearCalibratorConsoleInterface(ILinearCalibratorInterface):
    def make_fist(self):
        input("Make fist")

    def outstretch_hand(self):
        input("make outstretched")

    def fold_thumb(self):
        input("fold thumb")

    def finished(self):
        print("finished")
