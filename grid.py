import copy
import math
import random
import numpy as np
import pandas as pd

from typing import List, Any

import cell
import matplotlib.pyplot as plt


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

        self.model_type = kwargs.get('model_type', 1)
        # self.agg_compartments = [[0] * len(self.model_type)]
        # TODO: rewrite the transition from I -> R
        self.infection_phase_threshold = 7

        # TODO: rewrite, is this correct?
        self.beta = 0.1

        # create list of Cells, with x and y coordinates
        self.cell_list = [[] for _ in range(self.width)]
        for col in range(width):
            for row in range(height):
                self.cell_list[col].append(cell.Cell(col, row, self))

        # self.agg_compartments[0][0] = width * height

        self.has_infected = False

    def get_neighbours(self, x, y):
        """ Returns a list of coordinates of cells neighbouring the cell at x, y. """
        if self.neighbours == 'radius':
            return self._get_neighbours_in_radius(x, y, self.radius)
        if self.neighbours == 'random':
            return self._get_neighbours_randomly(x, y, self.nr_of_neighbours)
        if self.neighbours == 'gauss':
            return self._get_neighbours_gaussian(x, y, self.nr_of_neighbours, self.SD)

    def _get_neighbours_in_radius(self, x, y, radius):
        """ Returns a list of coordinates of cells neighbouring the cell at x, y. """
        neigh = []
        for col in range(x - radius, x + radius + 1):
            for row in range(y - radius, y + radius + 1):
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
            # TODO: check if this append is required
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
        elif self.neighbours == 'gradient':
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
        if state == 'S' and chance < 1 - (1 - self.beta) ** neighbor_states['I']:
            # Make sure there is at least one infection
            if not self.has_infected:
                self.has_infected = True
            return 'I'
        elif state == 'I' and chance < 1 / self.infection_phase_threshold and self.has_infected:
            return 'R'
        else:
            return state

    def step(self):
        """ Steps one day ahead. Evaluates the state of all cells in the grid. """
        # Boolean to indicate no more infected cells
        done = True
        # Copy grid so updating of cells doesn't affect neighbor states
        temp = copy.deepcopy(self.cell_list)
        # new_agg_day = [0] * len(self.model_type)
        for col in range(self.width):
            for row in range(self.height):
                new_state = self.evaluate_cell(col, row)
                if new_state == 'I':
                    done = False
                temp[col][row].compartment = new_state
                temp[col][row].add_compartment_day(temp[col][row].compartment)
                # evaluate the new aggregated states
                # TODO: je kan dit waarschijnlijk ook doen met een index functie, voor alle modellen zonder veel if's
                if self.model_type == 'SIR':
                    if temp[col][row].compartment == 'S':
                        new_agg_day[0] += 1
                    if temp[col][row].compartment == 'I':
                        new_agg_day[1] += 1
                    if temp[col][row].compartment == 'R':
                        new_agg_day[2] += 1
        self.cell_list = temp
        return done

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

    def count_states(self, model="SIR"):
        """ Returns a dict with a count of each state. """
        states = {k: 0 for k in model}
        for col in range(self.width):
            for row in range(self.height):
                states[self.cell_list[col][row].compartment] += 1
        return states

    def run(self, model="SIR"):
        """ Runs simulation until no more cells are infected. """
        # Construct dict to store state history in.
        history = {k: [] for k in model}
        # Step through until pandemic is over.
        done = False
        while not done:
            # Record state
            history = {k: history[k] + [v] for k, v in self.count_states(model).items()}
            # Go to next step
            done = self.step()
        # Return history
        return history
    
    @classmethod
    def simulate(cls, *args, **kwargs):
        """ Runs a full simulation. """
        grid = cls(*args, **kwargs)
        grid.infect(random.randint(0, grid.width-1), random.randint(0, grid.height-1))
        return grid.run()

if __name__ == "__main__":
    myGrid = Grid(9, 9)
    # state = myGrid.state(1, 1)
    # print("state van 1, 1, is: " + state)
    myGrid.infect(4, 4)
    myGrid.step()
    for i in range(50):
        myGrid.step()

    # plot testje
    lbl = ['S', 'I', 'R']
    x = range(len(myGrid.agg_compartments))
    y = myGrid.agg_compartments
    plt.xlabel("Days")
    plt.ylabel("nr of persons")
    plt.title("SIR Compartments vs days")
    for i in range(len(y[0])):
        plt.plot(x, [pt[i] for pt in y], label='compartment {}'.format(lbl[i]))
    plt.legend()
    plt.show()

    print("klaar")
