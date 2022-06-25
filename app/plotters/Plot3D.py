import sys
import time
from random import random
from typing import List, Dict

from PyQt5 import QtWidgets

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg

from mpl_toolkits.mplot3d import Axes3D
from matplotlib import pyplot as plt
import matplotlib

from app.plotters.IPlot import IPlot
from app.plotters.plotter_utils import IPlotData3D
from shared.shared_utils import Cartesian3D

matplotlib.use("Qt5Agg")


class Plot3D(FigureCanvasQTAgg):
    def __init__(self, plotData: IPlotData3D):
        self.lines: Dict = {}
        self.plotData: IPlotData3D = plotData
        self.map = plt.figure()
        self.timeOfLastDraw: float = 0
        self.renderDelay: float = 0.05
        self.setup()

        super(Plot3D, self).__init__(self.map)

    def setup(self):
        self.map.canvas.mpl_connect("button_press_event", lambda: exit(0))

        map_ax = Axes3D(self.map)
        map_ax.autoscale(enable=True, axis="both", tight=True)

        # # # Setting the axes properties
        map_ax.set_xlim3d([-10.0, 10.0])
        map_ax.set_ylim3d([-10.0, 10.0])
        map_ax.set_zlim3d([-10.0, 10.0])

        for name in self.plotData.curveTitles():
            (hl,) = map_ax.plot3D([0], [0], [0], label=name)
            self.lines[name] = hl

        map_ax.legend()

    def update_line(self, hl, new_data: List[Cartesian3D]):
        xd = [coord.x() for coord in new_data]
        yd = [coord.y() for coord in new_data]
        zd = [coord.z() for coord in new_data]

        hl.set_xdata(xd)
        hl.set_ydata(yd)
        hl.set_3d_properties(zd)

    def update_plot(self):
        data = self.plotData.getUpdate()
        if time.time() - self.timeOfLastDraw < self.renderDelay:
            time.sleep(max(0.0, self.renderDelay - (time.time() - self.timeOfLastDraw)))

        for i, title in enumerate(self.plotData.curveTitles()):
            self.update_line(self.lines[title], data[i])

        self.draw()
        self.timeOfLastDraw: float = time.time()


class Plot3DWindow(IPlot):
    def __init__(self, plot3d: Plot3D, parent=None):
        super(Plot3DWindow, self).__init__(parent)
        self.plot3d = plot3d

        # Create the matplotlib FigureCanvas object,
        # which defines a single set of axes as self.axes.
        self.setCentralWidget(plot3d)
        self.show()

    def _update(self):
        self.plot3d.update_plot()
