"""
SIR as a Cellular Automaton
---------------------------

This code is part of a project for the course Natural Computing.
"""
import numpy as np
import pandas as pd

from tkinter import *
from interface import CellViz
from grid import Grid

import matplotlib.pyplot as plt

class SIRGui:

    FRAME_RATE = 1000           # Miliseconds per frame
    state_counts = []

    def __init__(self, rows, cols, mode='auto', start_loc=(25, 25), model="SIR"):
        """ Constructs a window in which visualisation will take place. """
        # Store rows and cols
        self.rows = rows
        self.cols = cols
        self.start_loc = start_loc
        self.model = model
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
        self.window.mainloop()

    def start(self):
        """ This method is run once before the simulation starts. """
        self.SIR = Grid(self.cols, self.rows, radius=1, model=self.model)
        self.SIR.infect(self.start_loc[0], self.start_loc[1])
        self.store_state()
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

        self.store_state()

        if not self.find_infected():
            # end simulation if no infected people are found
            self.auto_exit()

        self.window.after(self.FRAME_RATE, self.update)

    def manual_update(self, event):
        """ Updates the grid. """
        self.SIR.step()
        data = pd.DataFrame(self.SIR.get_states())
        self.cvs.update(data)

    def exit(self, event):
        """ Exits the application. """
        self.window.destroy()

    def auto_exit(self):
        """ Exits the application without the need of an event and shows a plot of the simulation. """
        self.window.destroy()
        self.plot_states()

    def find_infected(self):
        """ Determines whether any infected people are left"""
        return bool(self.state_counts[-1][1])

    def store_state(self):
        """ Records the number of people in all states"""
        a = np.zeros(3)
        for i in self.SIR.cell_list:
            for j in i:
                if j.compartment == 'S':
                    a[0] += 1
                elif j.compartment == 'I':
                    a[1] += 1
                else:
                    a[2] += 1
        self.state_counts.append(a)

    def plot_states(self):
        S = [i[0] for i in self.state_counts]
        I = [i[1] for i in self.state_counts]
        R = [i[2] for i in self.state_counts]
        X = list(range(1, len(S) + 1))
        plt.plot(X, S, label='Susceptible')
        plt.plot(X, I, label='Infected')
        plt.plot(X, R, label='Recovered')
        plt.legend()
        plt.show()

    
if __name__ == "__main__":
    SIRGui(51, 51, 'auto', model='SEIR')
