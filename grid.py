import copy
import random
import numpy as np
import pandas as pd

from typing import List, Any

import cell


class Grid:
    """
    grid object
    """
    cell_list: List[List[cell.Cell]] = []
    id_list: List[int] = []

    def __init__(self, width, height, radius=1):
        """
        The __init__ method initializes the grid object

        Attributes:
            width (int): number of cells the grid measures as width
            height (int): number of cells the grid measures as height
            day (int): the number of days the model is running
        """
        self.day = 0
        self.width = width
        self.height = height
        self.radius = radius
        # TODO: rewrite the transition from I -> R
        self.infection_phase_threshold = 7

        # TODO: rewrite, is this correct?
        self.beta = 0.1

        # create list of Cells, with x and y coordinates
        self.cell_list = [[] for _ in range(self.width)]
        for col in range(width):
            for row in range(height):
                self.cell_list[col].append(cell.Cell(col, row, self))
                # self.id_list.append(id(self.cell_list[-1]))

                # self.cell_list.append([cell.Cell(wi, hi, self), wi, hi])

    def randomize_cell_list(self):
        # TODO: make function
        # shuffle cell_list, so the instances are shuffeled
        # reassign all the x, y locations
        pass

    def get_neighbours(self, x, y, radius=1):
        """ Returns a list of coordinates of cells neighbouring the cell at x, y. """
        neigh = []
        for col in range(x-radius, x+radius+1):
            for row in range(y-radius, y+radius+1):
                # Skip center
                if col == x and row == y:
                    continue
                # Append neighbour
                # Modulo makes the grid loop around so we don't have to worry about border cases.
                neigh.append((col % self.width, row % self.height))
        return neigh

    def evaluate_cell(self, x, y, radius=1):
        """ Evaluates the state of cell at x, y based on it's neighbours. """
        # Get current state
        state = self.cell_list[x][y].compartment
        # If state is recovered, no further computing is needed
        if state == 'R':
            self.cell_list[x][y].compartment_table.append()
            return 'R'
        # Set initial counts to 0
        neighbor_states = {'S': 0, 'I': 0, 'R': 0}
        # Count states of neighbours
        for x, y in self.get_neighbours(x, y, radius=radius):
            neighbor_states[self.cell_list[x][y].compartment] += 1
        # Get random number
        chance = random.random()
        # Return evaluated state
        if state == 'S' and chance < 1 - (1-self.beta) ** neighbor_states['I']:
            return 'I'
        elif state == 'I' and chance < 1 / self.infection_phase_threshold:
            return 'R'
        else:
            return state

    def step(self):
        """ Evaluates the state of all cells in the grid. """
        # Copy grid so updating of cells doesn't affect neighbor states
        temp = copy.deepcopy(self.cell_list)
        for col in range(self.width):
            for row in range(self.height):
                temp[col][row].compartment = self.evaluate_cell(col, row, radius=self.radius)
                temp[col][row].add_compartment_day(temp[col][row].compartment)
        self.cell_list = temp

    def infect(self, x, y):
        """ Sets state of cell at x, y to I=infected. """
        self.cell_list[x][y].compartment = 'I'

    def get_states(self):
        """ Returns a grid of state indicators. """
        classes = ['S', 'I', 'R']
        states = [[] for _ in range(self.width)]
        for col in range(self.width):
            for row in range(self.height):
                states[col].append(classes.index(self.cell_list[col][row].compartment))
        return states


if __name__ == "__main__":
    myGrid = Grid(9, 9)
    # state = myGrid.state(1, 1)
    # print("state van 1, 1, is: " + state)
    myGrid.infect(4, 4)
    myGrid.step()
    for i in range(20):
        myGrid.step()

    air = 'lucht'
    print("klaar")
