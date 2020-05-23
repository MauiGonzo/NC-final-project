
import math
import numpy as np
import pandas as pd
import seaborn as sn

import matplotlib
matplotlib.use("Tkagg")
import matplotlib.pyplot as plt

from tkinter import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class CellViz(Canvas):
    """
    Custom class used to visualize cell states for cellular automata.
    """

    def __init__(self,
                 master,                 # Master for this widget
                 cols=50,                # Number of cols of cells to visualize
                 rows=30,                # Number of rows of cells to visualize
                 pref_width=345,         # Preferred width of the widget in pixels
                 colors=None,            # Colors to use for cells
                 outline='',             # Color of the cell outline
                 **kwargs                # Default kwargs for widgets
                ):
        """
        A widget to visualize Cellular Automata.
        """
        self.cols = cols
        self.rows = rows
        self.cw = max(1, pref_width // cols)
        self.colors = colors
        self.outline = outline
        width = self.cw*cols if outline == '' else self.cw*cols + 1
        height = self.cw*rows if outline == '' else self.cw*rows + 1
        super().__init__(master, width=width, height=height, highlightthickness=0, **kwargs)
        self.cells = None

    def start(self):
        """ Draws grid based on cell values. """
        data = pd.DataFrame(np.zeros((self.cols, self.rows), dtype=int))

        self.cells = [[] for _ in range(self.rows)]
        for y in range(self.rows):
            for x in range(self.cols):
                c = self.int2color(data.iloc[x, y]) if self.colors is None else self.colors[data.iloc[x, y]]
                cell = self.create_rectangle([x*self.cw, y*self.cw, (x+1)*self.cw, (y+1)*self.cw], fill=c, outline=self.outline)
                self.cells[y].append(cell)

    def update(self, data):
        """ Updates the grid. """
        for y, row in enumerate(self.cells):
            for x, cell in enumerate(row):
                # Compute color if colors is not specified
                c = self.int2color(data.iloc[x, y]) if self.colors is None else self.colors[data.iloc[x, y]]
                self.itemconfig(cell, fill=c, outline=self.outline)
    
    @staticmethod
    def int2color(value):
        """ Retuns a color corresponding to the integer value. """
        r = int((math.sin(value+4) * 0.5 + 0.5) * 255)
        g = int((math.sin(value+8) * 0.5 + 0.5) * 255)
        b = int((math.sin(value+12) * 0.5 + 0.5) * 255)
        return "#%02x%02x%02x" % (r, g, b)


class Plot(Frame):
    """
    Custom class used to visualize plots.
    """

    def __init__(self,
                 master,                 # Master for this widget
                 width=500,              # Preferred width of the widget in pixels
                 **kwargs                # Default kwargs for widgets
                ):
        """
        A widget to visualize plots.
        """
        super().__init__(master, width=width, highlightthickness=0, **kwargs)
        self.configure(background='#4b4b4b', borderwidth=1, relief='sunken')
        self.data = np.array([[0, 2], [100, 98], [0, 0]])
        self.figure = None
        self.subplot = None
        self.canvas = None

    def update(self):
        """ Updates the plot frame element. """
        self.subplot.clear()
        self.subplot.stackplot(range(self.data.shape[1]), self.data)
        self.canvas.draw()

        
    # def make_graph(self):
    #     """ Draws the axis """
    #     self.delete(ALL)
    #     self.draw_x_axis([0, 1, 2])
    #     self.draw_y_axis([0.0, 0.25, 0.50, 0.75, 1.0])
    #     self.plot([(0,0), (0.5, 0.8), (0.8, 0.9)])

    # def draw_x_axis(self, values):
    #     """ Draws the x axis. """
    #     # Create horizontal axis
    #     self.h_bar = self.create_line([30, self.winfo_height()-20, self.winfo_width(), self.winfo_height()-20], width=1, fill='white')
    #     # Compute value distances
    #     dist = (self.winfo_width() - 50) / (len(values) - 1)
    #     # Write axis values
    #     self.labels = []
    #     for i, v in enumerate(values):
    #         label = self.create_text([dist * i + 30, self.winfo_height()-10], text=v, fill="white")
    #         self.labels.append(label)

    # def draw_y_axis(self, values):
    #     """ Draws the y axis. """
    #     # Create horizontal axis
    #     self.v_bar = self.create_line([30, 20, 30, self.winfo_height()-20], width=1, fill='white')
    #     # Compute value distances
    #     dist = (self.winfo_height() - 40) / (len(values) - 1)
    #     # Write axis values
    #     self.labels = []
    #     for i, v in enumerate(values):
    #         h = self.winfo_height() - (dist * i) - 20
    #         lbl_txt = self.create_text([13, h], text=v, fill="white")
    #         lbl_mark = self.create_line([26, h, 30, h], fill="white")
    #         self.labels.append((lbl_txt, lbl_mark))

    # def plot(self, values):
    #     """ Draws a polygon. """
    #     X, Y = zip(*values)
    #     # Create np arrays
    #     X = np.array(X)
    #     Y = np.array(Y)
    #     # Normalize arrays
    #     X /= X.max()
    #     Y /= Y.max()
    #     # Multiply by drawfield height
    #     X *= self.winfo_width()-50
    #     Y *= self.winfo_height()-40
    #     # Add offset
    #     X += 30
    #     Y += 20
    #     values = [val for pair in zip(X, Y) for val in pair]
    #     self.poly = self.create_polygon(values, width=1, fill="red")

    def draw_figure(self, canvas, figure, loc=(0, 0)):
        """ Draw a matplotlib figure onto a Tk canvas

        loc: location of top-left corner of figure on canvas in pixels.
        Inspired by matplotlib source: lib/matplotlib/backends/backend_tkagg.py
        """
        f = matplotlib.figure.Figure(figsize=(self.winfo_width(), self.winfo_height()), dpi=100)
        a = f.add_subplot(111)
        a.stackplot([0,0.1,0.2,0.3], [1,0.9,0.8,0.7])


        can = FigureCanvasTkAgg(f, self)
        can.draw()
        can.get_tk_widget().pack(side=BOTTOM, fill=BOTH, expand=True)
        # figure_x, figure_y, figure_w, figure_h = figure.bbox.bounds
        # figure_w, figure_h = int(figure_w), int(figure_h)
        # photo = PhotoImage(master=canvas, width=figure_w, height=figure_h)

        # # Position: convert from top-left anchor to center anchor
        # canvas.create_image(loc[0] + figure_w/2, loc[1] + figure_h/2, image=photo)

        # # Unfortunately, there's no accessor for the pointer to the native renderer
        # blit(photo, figure_canvas_agg.get_renderer()._renderer, colormode=2)

        # # Return a handle which contains a reference to the photo object
        # # which must be kept live or else the picture disappears
        # return photo

    def draw(self):
        """ Draws a plot to plot class values in. """
        print(sn.axes_style())
        self.figure = matplotlib.figure.Figure()
        self.subplot = self.figure.add_subplot(111)
        self.subplot.stackplot(range(self.data.shape[1]), self.data)

        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=BOTTOM, fill=BOTH, expand=True)


if __name__ == "__main__":
    gui = SIRGui()
