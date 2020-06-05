import copy
import math
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

    def __init__(self, width, height, neighbours='radius', **kwargs):
        """
        The __init__ method initializes the grid object

        Attributes:
            width (int): number of cells the grid measures as width
            height (int): number of cells the grid measures as height
            day (int): the number of days the model is running
        
        Keyword arguments:
            neighbours (str):   which method to use when selecting methods
                                valid options are: radius, random, gauss, all and gradient
            radius (int):       radius of cells that are considered a neighbour
                                used when neighbours are selected based on radius
            nr_of_neighbours(int): number of neighbours that are considered in step
                                used when neighbours are selected randomly
            SD (int):           standard deviation of the gaussian
                                used when neighoubrs are selected randomly using a gaussian
        """
        self.day = 0
        self.width = width
        self.height = height
        self.neighbours = neighbours

        self.radius = kwargs.get('radius', 1)
        self.nr_of_neighbours = kwargs.get('nr_of_neighbours', 8)
        self.SD = kwargs.get('SD', self.width)

        # TODO: rewrite the transition from I -> R
        self.infection_phase_threshold = 7

        # TODO: rewrite, is this correct?
        self.beta = 0.1

        # create list of Cells, with x and y coordinates
        self.cell_list = [[] for _ in range(self.width)]
        for col in range(width):
            for row in range(height):
                self.cell_list[col].append(cell.Cell(col, row, self))

    def get_neighbours(self, x, y):
        """ Returns a list of coordinates of cells neighbouring the cell at x, y. """
        if self.neighbours == 'radius':
            return self._get_neighbours_in_radius(x, y, self.radius)
        if self.neighbours == 'random':
            return self._get_neighbours_randomly(x, y, self.nr_of_neighbours)
        if self.neighbours == 'gauss':
            return self._get_neighbours_gaussian(x, y, self.nr_of_neighbours, self.SD)
        if self.neighbours == 'all':
            return self._get_neighbours_all(x, y)

    def _get_neighbours_in_radius(self, x, y, radius):
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
    
    def _get_neighbours_randomly(self, x, y, nr_of_neighbours):
        """ Returns a list of randomly sampled neighbours where each cell has an equal chance of being sampled. """
        neigh = []
        while len(neigh) < nr_of_neighbours:
            col = random.randint(0, self.width-1)
            row = random.randint(0, self.height-1)
            if (col, row) == (x, y) or (col, row) in neigh:
                continue
            else:
                neigh.append((col, row))
        return neigh

    def _get_neighbours_gaussian(self, x, y, nr_of_neighbours, SD=2):
        """ Returns a list of randomly sampled neighbours where cells closer to x,y have a higher chance of being sampled. """
        neigh = []
        while len(neigh) < nr_of_neighbours:
            col = (x + int(random.gauss(0, SD))) % (self.width)
            row = (y + int(random.gauss(0, SD))) % (self.height)
            if (col, row) == (x, y) or (col, row) in neigh:
                continue
            else:
                neigh.append((col, row))
        return neigh

    def get_dist(self, a, b):
        """ Computes the distance between point a and point b. """
        a = np.array(a)
        b = np.array(b)
        dist = np.linalg.norm(a-b)
        return dist

    def evaluate_cell(self, x, y):
        """ Evaluates the state of cell at x, y based on it's neighbours. """
        # Get current state
        state = self.cell_list[x][y].compartment
        # If state is recovered, no further computing is needed
        if state == 'R':
            self.cell_list[x][y].compartment_table.append(state)
            return 'R'
        # Set initial counts to 0
        neighbor_states = {'S': 0, 'I': 0, 'R': 0}
        # Count states of neighbours
        if self.neighbours == 'all':
            for c in range(self.width):
                for r in range(self.height):
                    if (c, r) != (x, y):
                        neighbor_states[self.cell_list[c][r].compartment] += 1
        if self.neighbours == 'gradient':
            for c in range(self.width):
                for r in range(self.height):
                    if (c, r) != (x, y):
                        neighbor_states[self.cell_list[c][r].compartment] += math.log10(1-(1/self.get_dist((c, r), (x, y)))+1e-9)
        else:
            for x, y in self.get_neighbours(x, y):
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
                temp[col][row].compartment = self.evaluate_cell(col, row)
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
    myGrid.infect(4, 4)
    for i in range(20):
        myGrid.step()
        
    print("klaar")
