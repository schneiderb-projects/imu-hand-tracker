from abc import abstractmethod
from pyqtgraph.Qt import QtCore, QtWidgets


class IPlot(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(IPlot, self).__init__(parent)

    @abstractmethod
    def _update(self):
        raise NotImplemented

    def begin(self):
        self.show()
        self.my_timer = QtCore.QTimer()
        self.my_timer.timeout.connect(self._update)
        self.my_timer.start(0)
