import time
from typing import List

import numpy as np
import pyqtgraph as pg
from numpy import sqrt, ceil
from pyqtgraph.Qt import QtCore, QtWidgets

from app.plotters.IPlot import IPlot
from app.plotters.plotter_utils import IPlotData2D


class Plot2dMatplotlib(IPlot):
    def live_update_demo(self, blit=False):
        x = np.linspace(0, 50.0, num=100)
        X, Y = np.meshgrid(x, x)
        fig = self.plt.figure()
        ax1 = fig.add_subplot(2, 1, 1)
        ax2 = fig.add_subplot(2, 1, 2)

        img = ax1.imshow(X, vmin=-1, vmax=1, interpolation="None", cmap="RdBu")

        (line,) = ax2.plot([], lw=3)
        text = ax2.text(0.8, 0.5, "")

        ax2.set_xlim(x.min(), x.max())
        ax2.set_ylim([-1.1, 1.1])

        fig.canvas.draw()  # note that the first draw comes before setting data

        if blit:
            # cache the background
            axbackground = fig.canvas.copy_from_bbox(ax1.bbox)
            ax2background = fig.canvas.copy_from_bbox(ax2.bbox)

        self.plt.show(block=False)

        t_start = time.time()
        k = 0.0

        for i in np.arange(1000):
            img.set_data(np.sin(X / 3.0 + k) * np.cos(Y / 3.0 + k))
            line.set_data(x, np.sin(x / 3.0 + k))
            tx = "Mean Frame Rate:\n {fps:.3f}FPS".format(
                fps=((i + 1) / (time.time() - t_start))
            )
            text.set_text(tx)
            # print tx
            k += 0.11
            if blit:
                # restore background
                fig.canvas.restore_region(axbackground)
                fig.canvas.restore_region(ax2background)

                # redraw just the points
                ax1.draw_artist(img)
                ax2.draw_artist(line)
                ax2.draw_artist(text)

                # fill in the axes rectangle
                fig.canvas.blit(ax1.bbox)
                fig.canvas.blit(ax2.bbox)

                # in this post http://bastibe.de/2013-05-30-speeding-up-matplotlib.html
                # it is mentionned that blit causes strong memory leakage.
                # however, I did not observe that.

            else:
                # redraw everything
                fig.canvas.draw()

            fig.canvas.flush_events()
            # alternatively you could use
            # plt.pause(0.000000000001)
            # however plt.pause calls canvas.draw(), as can be read here:
            # http://bastibe.de/2013-05-30-speeding-up-matplotlib.html


class Plot2D(IPlot):
    def __init__(self, parent=None, plotsData: List[IPlotData2D] = None):
        super(Plot2D, self).__init__(parent)

        #### Create Gui Elements ###########
        if plotsData is None:
            self.plotsData: List[IPlotData2D] = []
        else:
            self.plotsData: List[IPlotData2D] = plotsData

        self.mainbox = QtWidgets.QWidget()
        self.setCentralWidget(self.mainbox)
        self.mainbox.setLayout(QtWidgets.QVBoxLayout())

        self.canvas = pg.GraphicsLayoutWidget()
        self.mainbox.layout().addWidget(self.canvas)

        self.label = QtWidgets.QLabel()
        self.mainbox.layout().addWidget(self.label)

        colors = ["r", "g", "c", "m", "y", "w"]
        # r, g, b, c, m, y, k, w
        self.plots = []
        self.ydata: List[
            List[List[float]]
        ] = []  # [[[1, 2, 3], [4, 5, 6], [7, 8, 9]], [[1, 2, 3], [4, 5, 6], [7, 8, 9]]]
        self.xdata: List[List[List[float]]] = []
        self.datapoints: List[int] = []

        rows: int = int(ceil(sqrt(len(self.plotsData))))
        cols: int = int(ceil(len(self.plotsData) / rows))
        # for i, plotData in enumerate(self.plotsData):
        for row in range(rows):
            for col in range(cols):
                colspan = (
                    1
                    if (cols * row + col != len(self.plotsData) - 1)
                    else (cols * 2 - col * 2 - 1)
                )
                plotData = self.plotsData[col * rows + row]
                plot = self.canvas.addPlot(
                    title=plotData.title(),
                    labels={
                        "left": plotData.y_axis_labels(),
                        "bottom": plotData.x_axis_labels(),
                    },
                    row=row,
                    col=col * 2,
                    colspan=colspan,
                )
                vb = self.canvas.addViewBox(row=row, col=col * 2 + colspan)
                vb.setMaximumWidth(100)
                legend = pg.LegendItem(pen="r", labelTextSize="12pt")
                legend.setParentItem(vb)
                legend.anchor((0, 0), (0, 0))

                curves = []
                self.ydata.append([])
                self.xdata.append([])
                self.datapoints.append(plotData.dataPointsToPlot())
                for j, title in enumerate(plotData.curveTitles()):
                    self.ydata[-1].append([0.0] * self.datapoints[-1])
                    self.xdata[-1].append([0.0] * self.datapoints[-1])
                    curves.append(plot.plot(name=title, pen=colors[j % len(colors)]))
                    legend.addItem(curves[-1], name=curves[-1].opts["name"])

                self.plots.append(curves)

                if colspan != 1:
                    break

        self.counter = 0
        self.mean_total_fps = 0.0
        self.lastupdate = time.time()
        self.initialtime = self.lastupdate
        self.current_fps = 0

        self.frame_count = 0
        self.start = time.time()

    def begin(self):
        self.show()
        self.my_timer = QtCore.QTimer()
        self.my_timer.timeout.connect(self._update)
        self.my_timer.start(0)
        """
        self.timer = QtCore.QTimer(parent=self)
        self.timer.timeout.connect(self._update)
        self.timer.setSingleShot(True)
        self.timer.start()"""

    def _update(self):
        # print("gap:", time.time() - self.start)
        start = time.time()
        for i, plot in enumerate(self.plots):
            update = self.plotsData[i].getUpdate()
            for j, curve in enumerate(plot):
                # add in new data
                if isinstance(update[j], list):
                    # if a list of data was given, add the whole list
                    for sensorCoordinate in update[j]:
                        self.ydata[i][j].append(sensorCoordinate.value())
                        self.xdata[i][j].append(sensorCoordinate.time())
                else:
                    # if 1 datapoint was given, append it to the previous data
                    self.ydata[i][j].append(update[j].value())
                    self.xdata[i][j].append(update[j].time())

                # shorten data to desired number of data points
                self.ydata[i][j] = self.ydata[i][j][-1 * self.datapoints[i] :]
                self.xdata[i][j] = self.xdata[i][j][-1 * self.datapoints[i] :]

        for i, plot in enumerate(self.plots):
            for j, curve in enumerate(plot):
                curve.setData(self.xdata[i][j], self.ydata[i][j])

        now = time.time()
        dt = now - self.lastupdate
        if dt <= 0:
            dt = 0.000000000001
        self.current_fps += 1.0 / dt
        self.lastupdate = now
        self.mean_total_fps = self.frame_count / (self.lastupdate - self.initialtime)

        self.frame_count += 1
        if self.frame_count % 30 == 0:
            tx = "Mean Frame Rate:  {fps:.3f} FPS\t Current Frame Rate:  {fps2:.3f} FPS".format(
                fps=self.mean_total_fps, fps2=self.current_fps / 30
            )

            self.label.setText(tx)
            self.current_fps = 0

        # print("update:", time.time() - start)
        self.start = time.time()
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self._update)
        self.timer.setSingleShot(True)
        self.timer.start()
