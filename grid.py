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

    def __init__(self, width, height, radius, model='SIR', beta=0.76, inf_thr=2.2, exp_thr=5.2):
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
        self.model = model
        # TODO: rewrite the transition from I -> R
        self.infection_phase_threshold = inf_thr
        self.exposed_phase_threshold = exp_thr

        # TODO: rewrite, is this correct?
        self.beta = beta

        # create list of Cells, with x and y coordinates
        self.cell_list = [[] for _ in range(self.width)]
        for col in range(width):
            for row in range(height):
                self.cell_list[col].append(cell.Cell(col, row, self))
                # self.id_list.append(id(self.cell_list[-1]))

                # self.cell_list.append([cell.Cell(wi, hi, self), wi, hi])

    def assign_neighbor_ids(self):
        # for every Cell assign it's neighbors
        # costly, but should count as an investment, only one call per step
        for i, targetcell in enumerate(self.cell_list):
            # set left neighbor if possible, else id = 0
            if (i%self.width) is not 0:
                leftcell = self.cell_list[i-1]
                targetcell.left_id = id(leftcell)
            else:
                targetcell.left_id = 0
            # set right neighbor if possible, else id = 0
            if ((i+1)%(self.width)) is not 0:
                rightcell = self.cell_list[i+1]
                targetcell.right_id = id(rightcell)
            else:
                targetcell.right_id = 0
            # set upper neighbor if possible, else id = 0
            if i > self.width:
                uppercell = self.cell_list[i-self.width]
                targetcell.upper_id = id(uppercell)
            else:
                targetcell.upper_id = 0
            # set lower neighbor if possible, else id = 0
            if i < (len(self.cell_list) - self.width):
                lowercell = self.cell_list[i + self.width]
                targetcell.lower_id = id(lowercell)
            else:
                targetcell.lower_id = 0

    def randomize_cell_list(self):
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
        # If state is recoverd, no further computing is needed
        if state == 'R':
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

    def cell_behaviour(self, x, y, radius=1):

        state = self.cell_list[x][y].compartment

        if state == "I":
            if random.random() < 1 / self.infection_phase_threshold:
                transition = True
            else:
                transition = False

            if 1 <= self.beta:
                infect_count = np.floor(self.beta)
            else:
                infect_count = 0

            if random.random() < self.beta % 1:
                infect_count += 1

            neighbourlist = []
            for x, y in self.get_neighbours(x, y, radius=radius):
                if self.cell_list[x][y].compartment == 'S':
                    neighbourlist.append((x, y))

            if not neighbourlist:
                return transition, []
            elif len(neighbourlist) > infect_count:
                for _ in range(len(neighbourlist) - infect_count):
                    neighbourlist.remove(random.choice(neighbourlist))
            return transition, neighbourlist

        elif state == "E":
            if random.random() < 1 / self.exposed_phase_threshold:
                transition = True
            else:
                transition = False
            return transition, []


    def step(self):
        temp = copy.deepcopy(self.cell_list)
        for row in range(self.height):
            for col in range(self.width):
                if self.cell_list[col][row].compartment == 'I':
                    transition, neighbours = self.cell_behaviour(col, row)
                    if transition:
                        temp[col][row].compartment = 'R'
                    if neighbours:
                        for (nc, nr) in neighbours:
                            if temp[nc][nr].compartment == 'S' and self.model == 'SIR':
                                temp[nc][nr].compartment = 'I'
                            elif temp[nc][nr].compartment == 'S' and self.model == 'SEIR':
                                temp[nc][nr].compartment = 'E'
                elif self.cell_list[col][row].compartment == 'E':
                    transition, _ = self.cell_behaviour(col, row)
                    if transition:
                        temp[col][row].compartment = 'I'
        self.cell_list = temp



    # def step(self):
    #     """ Evaluates the state of all cells in the grid. """
    #     # Copy grid so updating of cells doesn't affect neighbor states
    #     temp = copy.deepcopy(self.cell_list)
    #     for col in range(self.width):
    #         for row in range(self.height):
    #             temp[col][row].compartment = self.evaluate_cell(col, row, radius=self.radius)
    #             # TODO: update cells state history
    #     self.cell_list = temp

    def infect(self, x, y):
        """ Sets state of cell at x, y to infected. """
        self.cell_list[x][y].compartment = 'I'

    def recover(self, x, y):
        """ Sets state of cell at x, y to recovered. """
        self.cell_list[x][y].compartment = 'R'

    def expose(self, x, y):
        """ Sets state of cell at x, y to exposed. """
        self.cell_list[x][y].compartment = 'E'

    def get_states(self):
        """ Returns a grid of state indicators. """
        classes = ['S', 'I', 'R', 'E']
        states = [[] for _ in range(self.width)]
        for col in range(self.width):
            for row in range(self.height):
                states[col].append(classes.index(self.cell_list[col][row].compartment))
        return states

    # def state(self, x, y):
    #     """ return state of a cell, if cell NA return false"""
    #     # check candidate x and y vs grid boundaries
    #     if x >= self.width | y >= self.height:
    #         return False
    #     # test all candidate cells
    #     for ccell in self.cell_list:
    #         if ccell[1] == x & ccell[2] == y:
    #             targetcell = ccell[0]
    #             return targetcell.state
    #     # no cell found, should not happen
    #     return False

    # def step(self):
    #     """ take one time step

    #     set one time step, every cell checks its neighbors and defines the expected state. When the swing gate is open
    #     the new states are set according to the expected state.

    #     """
    #     # plus one day
    #     self.day += 1

    #     # every cell is given its direct neighbors
    #     self.assign_neighbor_ids()
    #     # let every cell check it's neighbors, and prepare the next state
    #     # (otherwise future states may already influence
    #     for cell_to_update in self.cell_list:
    #         cell_to_update.evaluate_a_day()
    #     # open the swing gate en update all states
    #     for cell_to_update in self.cell_list:
    #         new_state_row = cell_to_update.compartment_table[-1]
    #         for i in range(len(cell_to_update.model_type)):
    #             if new_state_row[i]:
    #                 cell_to_update.compartment = cell_to_update.model_type[i]
    #     # TODO: check neighbor requirements i.e. when is an 'adjacent' cell taken into account?
    #     #
    #     # for now check if there are cells around the cell of interest and retrieve their state
    #     # default case: a cell has 8 neighbours


if __name__ == "__main__":
    myGrid = Grid(9, 9)
    # state = myGrid.state(1, 1)
    # print("state van 1, 1, is: " + state)
    myGrid.step()

    air = 'lucht'
