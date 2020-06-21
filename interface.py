
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
