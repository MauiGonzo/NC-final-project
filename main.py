"""
SIR as a Cellular Automaton
---------------------------

This code is part of a procject for the course Natural Computing.
"""
import numpy as np
import pandas as pd

from tkinter import *
from interface import CellViz
from grid import Grid

class SIRGui:

    FRAME_RATE = 1000           # Miliseconds per frame

    def __init__(self, rows, cols, mode='auto'):
        """ Constructs a window in which visualisation will take place. """
        # Store rows and cols
        self.rows = rows
        self.cols = cols

        # Create window
        self.window = Tk()
        self.window.title("SIR as a Cellular Automaton")
        self.window.bind('<Escape>', self.exit)
        if mode == 'manual':
            self.window.bind('<Button-1>', self.manual_update)
        self.window.configure(background='#3d3d3d')

        # Add canvas
        self.cvs = CellViz(self.window, cols, rows, 720, colors=['gray', 'red', 'green'], outline='gray')
        self.cvs.grid(column=0, row=0)

        # Show window
        self.start()
        if mode == 'auto':
            self.window.after(self.FRAME_RATE, self.update)
        elif mode == 'manual':
            self.manual_update(None)
        self.window.mainloop()

    def start(self):
        """ This method is run once before the simulation starts. """
        self.SIR = Grid(self.cols, self.rows)
        self.SIR.infect(25, 25)
        data = pd.DataFrame(self.SIR.get_states())
        self.cvs.start()
        self.cvs.update(data)

    def update(self):
        """ Updates the screen. """
        # Update cell values
        self.SIR.step()
        data = pd.DataFrame(self.SIR.get_states())
        self.cvs.update(data)
        # Keep calling for updates
        self.window.after(self.FRAME_RATE, self.update)

    def manual_update(self, event):
        """ Updates the grid. """
        self.SIR.step()
        data = pd.DataFrame(self.SIR.get_states())
        self.cvs.update(data)

    def exit(self, event):
        """ Exits the application. """
        self.window.destroy()


if __name__ == "__main__":
    SIRGui(51, 51, 'manual')
