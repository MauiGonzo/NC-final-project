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

    FRAME_RATE = 1000 // 5          # Miliseconds per frame
    state_counts = []

    def __init__(self, rows, cols, mode='auto', **kwargs):
        """ Constructs a window in which visualisation will take place. """
        # Store rows and cols
        self.rows = rows
        self.cols = cols
        self.kwargs = kwargs

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
        self.SIR = Grid(self.cols, self.rows, **self.kwargs)
        self.SIR.infect(25, 25)
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
        # self.window.quit()
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
        fig = plt.figure(figsize=(12, 5))
        plt.subplot(1, 2, 1)
        plt.plot(X, S, label='Susceptible')
        plt.plot(X, I, label='Infected')
        plt.plot(X, R, label='Recovered')
        plt.legend()
        plt.subplot(1, 2, 2)
        plt.stackplot(X, R, I, S, labels=['Recovered', 'Infected', 'Susceptible'], colors=['#2ca02c', '#ff7f0e', '#1f77b4', '#d62728'])
        handles, labels = plt.gca().get_legend_handles_labels()
        order = [2, 1, 0]
        plt.legend([handles[idx] for idx in order], [labels[idx] for idx in order], loc='center right')
        fig.show()


if __name__ == "__main__":
    SIRGui(51, 51, 'auto', neighbours='all')
    # SIRGui(51, 51, 'auto', neighbours='radius', radius=1)
    # SIRGui(51, 51, 'auto', neighbours='random', nr_of_neighbours=5)
    # SIRGui(51, 51, 'auto', neighbours='gauss', nr_of_neighbours=8, SD=0.9)
    # SIRGui(51, 51, 'auto', neighbours='gradient')

