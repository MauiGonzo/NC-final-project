from typing import List, Any

import cell


class Grid:
    """
    grid object
    """
    cell_list: List[cell.Cell] = []
    id_list: List[int] = []

    def __init__(self, width, height):
        """
        The __init__ method initializes the grid object

        Attributes:
            width (int): number of cells the grid measures as width
            height (int): number of cells the grid measures as height
            day (int): the number of days the model is running
        """
        self.day = 0;
        self.width = width
        self.height = height
        # TODO: rewrite the transition from I -> R
        self.infection_phase_threshold = 7

        # TODO: rewrite, is this correct?
        self.beta = 0.1
        # create list of Cells, with x and y coordinates
        for wi in range(width):
            for hi in range(height):
                self.cell_list.append(cell.Cell(wi, hi, self))
                self.id_list.append(id(self.cell_list[-1]))

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

    def step(self):
        """ take one time step

        set one time step, every cell checks its neighbors and defines the expected state. When the swing gate is open
        the new states are set according to the expected state.

        """
        # plus one day
        self.day += 1

        # every cell is given its direct neighbors
        self.assign_neighbor_ids()
        # let every cell check it's neighbors, and prepare the next state
        # (otherwise future states may already influence
        for cell_to_update in self.cell_list:
            cell_to_update.evaluate_a_day()
        # open the swing gate en update all states
        for cell_to_update in self.cell_list:
            new_state_row = cell_to_update.compartment_table[-1]
            for i in range(len(cell_to_update.model_type)):
                if new_state_row[i]:
                    cell_to_update.compartment = cell_to_update.model_type[i]
        # TODO: check neighbor requirements i.e. when is an 'adjacent' cell taken into account?
        #
        # for now check if there are cells around the cell of interest and retrieve their state
        # default case: a cell has 8 neighbours


if __name__ == "__main__":
    myGrid = Grid(9, 9)
    # state = myGrid.state(1, 1)
    # print("state van 1, 1, is: " + state)
    myGrid.step()

    air = 'lucht'
    print("klaar")
