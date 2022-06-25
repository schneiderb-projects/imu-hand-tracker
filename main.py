"""
==================================
Faster rendering by using blitting
==================================

*Blitting* is a `standard technique
<https://en.wikipedia.org/wiki/Bit_blit>`__ in raster graphics that,
in the context of Matplotlib, can be used to (drastically) improve
performance of interactive figures. For example, the
:mod:`.animation` and :mod:`.widgets` modules use blitting
internally. Here, we demonstrate how to implement your own blitting, outside
of these classes.

Blitting speeds up repetitive drawing by rendering all non-changing
graphic elements into a background image once. Then, for every draw, only the
changing elements need to be drawn onto this background. For example,
if the limits of an Axes have not changed, we can render the empty Axes
including all ticks and labels once, and only draw the changing data later.

The strategy is

- Prepare the constant background:

  - Draw the figure, but exclude all artists that you want to animate by
    marking them as *animated* (see `.Artist.set_animated`).
  - Save a copy of the RBGA buffer.

- Render the individual images:

  - Restore the copy of the RGBA buffer.
  - Redraw the animated artists using `.Axes.draw_artist` /
    `.Figure.draw_artist`.
  - Show the resulting image on the screen.

One consequence of this procedure is that your animated artists are always
drawn on top of the static artists.

Not all backends support blitting.  You can check if a given canvas does via
the `.FigureCanvasBase.supports_blit` property.

.. warning::

   This code does not work with the OSX backend (but does work with other
   GUI backends on mac).

Minimal example
---------------

We can use the `.FigureCanvasAgg` methods
`~.FigureCanvasAgg.copy_from_bbox` and
`~.FigureCanvasAgg.restore_region` in conjunction with setting
``animated=True`` on our artist to implement a minimal example that
uses blitting to accelerate rendering

"""
import time

import matplotlib

matplotlib.use("Qt5Agg")

import matplotlib.pyplot as plt
import numpy as np


class BlitManager:
    def __init__(self, canvas, animated_artists=(), cols=1, rows=1):
        """
        Parameters
        ----------
        canvas : FigureCanvasAgg
            The canvas to work with, this only works for sub-classes of the Agg
            canvas which have the `~FigureCanvasAgg.copy_from_bbox` and
            `~FigureCanvasAgg.restore_region` methods.

        animated_artists : Iterable[Artist]
            List of the artists to manage
        """
        self.canvas = canvas
        self._bg = None
        self._artists = []

        for a in animated_artists:
            self.add_artist(a)
        # grab the background on every draw
        self.cid = canvas.mpl_connect("draw_event", self.on_draw)

    def on_draw(self, event):
        """Callback to register with 'draw_event'."""
        cv = self.canvas
        if event is not None:
            if event.canvas != cv:
                raise RuntimeError
        self._bg = cv.copy_from_bbox(cv.figure.bbox)
        self._draw_animated()

    def add_artist(self, art):
        """
        Add an artist to be managed.

        Parameters
        ----------
        art : Artist

            The artist to be added.  Will be set to 'animated' (just
            to be safe).  *art* must be in the figure associated with
            the canvas this class is managing.

        """
        if art.figure != self.canvas.figure:
            raise RuntimeError
        art.set_animated(True)
        self._artists.append(art)

    def _draw_animated(self):
        """Draw all of the animated artists."""
        fig = self.canvas.figure
        for a in self._artists:
            fig.draw_artist(a)

    def update(self):
        """Update the screen with animated artists."""
        cv = self.canvas
        fig = cv.figure
        # paranoia in case we missed the draw event,
        if self._bg is None:
            self.on_draw(None)
        else:
            # restore the background
            cv.restore_region(self._bg)
            # draw all of the animated artists
            self._draw_animated()
            # update the GUI state
            cv.blit(fig.bbox)
        # let the GUI event loop process anything it has to do
        cv.flush_events()


###############################################################################
# Here is how we would use our class.  This is a slightly more complicated
# example than the first case as we add a text frame counter as well.

# make a new figure
fig, ax = plt.subplots(3, 3)
ax = ax[0][0]
# add a line
(ln,) = ax.plot(x, np.sin(x), animated=True)
# add a frame number
fr_number = ax.annotate(
    "0",
    (0, 1),
    xycoords="axes fraction",
    xytext=(10, -10),
    textcoords="offset points",
    ha="left",
    va="top",
    animated=True,
)
bm = BlitManager(fig.canvas, [ln, fr_number])
# make sure our window is on the screen and drawn
plt.show(block=False)
plt.pause(0.1)

total = 0.0
for j in range(10000):
    start = time.time()

    # update the artists
    ln.set_ydata(np.sin(x + (j / 100) * np.pi))
    # tell the blitting manager to do its thing
    bm.update()

    end = time.time() - start
    fr_number.set_text("frame rate: {j}".format(j=(j / end)))

###############################################################################
# This class does not depend on `.
# pyplot` and is suitable to embed
# into larger GUI application.
