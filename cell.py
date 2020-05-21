import numpy as np

class Cell:
    """
    represents a cell

    attributes:
        x               : [Int] x location in the grid
        y               : [Int] y location in the grid
        grid            : [Grid object]
        compartment     : [String] indicate the current state of the cell, default 'S'
        compartment_table     : [ndarray] stores the cells history in one hot fashion
        model_type      : [String] indicate the model used, by default 'SIR'
        left_id         : [int] indicating neighbors instance id
        right_id         : [int] indicating neighbors instance id
        upper_id         : [int] indicating neighbors instance id
        lower_id         : [int] indicating neighbors instance id
    """
    left_id = 0
    right_id = 0
    upper_id = 0
    lower_id = 0

    #     TODO: make a state list, days vs SIR-states
    def __init__(self, x, y, grid, state='S', type='SIR'):
        self.x = x
        self.y = y
        self.grid = grid
        self.compartment = state
        self.model_type = type
        self.compartment_table = [[0]*len(type)]
        # self.compartment_table = np.zeros([len(type), 1])
        # self.compartment_table = self.compartment_table.astype(int)
        # do the inital step
        # find out which position has state in type, that is the location that needs an update in state_table
        self.compartment_table[0][type.index(state)] = 1

    def step(self):
        """ do one time step"""
        # TODO: add more actions
        self.evaluate_a_day()
        # step one day forward

    def evaluate_a_day(self):
        """let the cell live a day and see what it becomes

        append the new state in the state_table
        """
        # TODO: pass state_table of cell to specific model function
        # for now solved below

        # if self is 'R' it is in the end-phase, state cannot change therefore
        if self.compartment == 'R':
            # do R -> R
            self.compartment_table.append([0, 0, 1])
        # if self is 'I' transition to R expected after certain number of days
        elif self.compartment == 'I':
            # apply infection rule
            # count days infected, if above threshold move to 'R' state
            days_infected = sum(self.compartment_table[1:0])
            # TODO: make this smarter :)
            if sum(self.compartment_table[1, :]) > self.grid.infection_phase_threshold:
                # do I -> R
                self.compartment_table.append([0, 0, 1])
            else:
                # do I -> I
                self.compartment_table.append([0, 1, 0])
        # if self is 'S' transition to I is possible, depending on neighbors
        elif self.compartment == 'S':
            # evaluate neighbors, for every neighbor there is a chance beta of getting infected
            # evaluate the left neighbor
            if self.left_id is not 0:
                # find this left neighbor - using the quick lookup list
                i = self.grid.id_list.index(self.left_id)
                left_neighbor = self.grid.cell_list[i]
                if left_neighbor.compartment == 'S':
                    # do S -> S
                    new_compartment_slice = [1, 0, 0]
                elif left_neighbor.compartment == 'R':
                    # do R -> R
                    new_compartment_slice = [0, 0, 1]
                elif left_neighbor.compartment == 'I':
                    # spin the unfair coin, maybe S -> I, else S -> S
                    if bias_coin(self.grid.beta):
                        new_compartment_slice = [1, 0, 0]
                    else:
                        new_compartment_slice = [0, 1, 0]
                self.compartment_table.append(new_compartment_slice)



    def state(self):
        """ returns the recent state of the cell"""
        if self.compartment_table.ndim == 1:
            return self.compartment
        else:
            return self.model_type((max(self.compartment_table[-1, :])))

# helper function
def bias_coin(p):
    if np.random.random() > p:
        return False
    else:
        return True

if __name__ == "__main__":
    myCell = Cell(0, 0)


    print(myCell)
