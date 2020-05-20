import numpy as np

class Cell:
    """
    represents a cell

    attributes:
        x               : [Int] x location in the grid
        y               : [Int] y location in the grid
        grid            : [Grid object]
        state           : [String] indicate the current state of the cell, default 'S'
        state_table     : [ndarray] stores the cells history in one hot fashion
        model_type      : [String] indicate the model used, by default 'SIR'
    """
    state_lookup = []

    #     TODO: make a state list, days vs SIR-states
    def __init__(self, x, y, grid, state='S', type='SIR'):
        self.x = x
        self.y = y
        self.grid = grid
        self.state = state
        self.model_type = type
        self.state_table = np.zeros(len(type))
        # do the inital step
        # find out which position has state in type, that is the location that needs an update in state_table
        self.state_table[type.index(state)] = 1

    def step(self):
        """ do one time step"""
        # TODO: add more actions
        # step one day forward
        # what state are the neighbors in?
        # who are my neighbors?



        pass

    def state(self):
        """ returns the recent state of the cell"""
        if self.state_table.ndim == 1:
            return self.state
        else:
            return self.model_type((max(self.state_table[-1, :])))


if __name__ == "__main__":
    myCell = Cell(0, 0)


    print(myCell)
