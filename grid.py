import copy
import random
import numpy as np


from IPython import get_ipython
from IPython.display import display, clear_output

import cell
import matplotlib.pyplot as plt


class Grid:
    """
    grid object
    """
    cell_list = []
    id_list = []

    def __init__(self,
                 width,
                 height,
                 R_0 = 0,
                 gamma = 0.053,
                 recovered = 0,
                 beta = 0.152,
                 infected = 1,
                 rho = 0.0,
                 dead = 0,
                 delta = 0.2,
                 neighbours='radius',
                 model='SIR',
                 modeltype = 'S-based',
                 **kwargs):
        """
        The __init__ method initializes the grid object

        Attributes:
            width (int):        number of cells the grid measures as width
            height (int):       number of cells the grid measures as height

        Keyword arguments:
            R_0 (float):        basic reproduction number.
                                Default is 0
            gamma (float):      recovery rate, probability of recovering from the disease.
                                Default is 0.053
            recovered (int):    number of recovered people at the start of the simulation.
                                Default is 0
            beta (float):       infection rate, contacts * probability of transferring the disease.
                                Default is 0.152
            infected (int):     number of infected people at the start of the simulation.
                                Default is 1
            rho (float):        mortality rate, probability of dying from the disease.
                                Default is 0
            dead (int):         number of dead people at the start of the simulation.
                                Default is 0
            delta (float):      resusceptibility rate, probability of losing resistance.
                                Default is 0.0
            day (int):          the number of days the model is running
                                Default is 0
            neighbours (str):   which method to use when selecting methods
                                valid options are: radius, random, gauss, all and gradient
            radius (int):       radius of cells that are considered a neighbour
                                used when neighbours are selected based on radius
            nr_of_neighbours(int): number of neighbours that are considered in step
                                used when neighbours are selected randomly
            SD (int):           standard deviation of the gaussian
                                used when neighoubrs are selected randomly using a gaussian
        """
        self.width = width
        self.height = height
        self.R_0 = R_0
        self.gamma = gamma
        self.recovered = recovered
        self.beta = beta
        self.infected = infected
        self.rho = rho
        self.dead = dead
        self.delta = delta
        self.day = 0
        self.model = model
        self.exposed_phase_threshold = 5.2
        self.modeltype = modeltype

        # # Set environment
        # self.in_notebook = self.in_notebook()

        # Set update method
        self.neighbours = neighbours
        self.radius = kwargs.get('radius', 1)

        # Determine the number of contacts for every timestep
        self.nr_of_neighbours = kwargs.get('nr_of_neighbours', 8)
        if self.neighbours == 'all':
            self.nr_of_neighbours = width * height - 1
        elif self.neighbours == 'radius':
            self.nr_of_neighbours = ((self.radius * 2 + 1) ** 2) - 1
        self.SD = kwargs.get('SD', self.width)

        # Compute relevant infection probability
        self.p_infect = self.beta / self.nr_of_neighbours

        self.model_type = kwargs.get('model_type', 'SIR')
        # # self.agg_compartments = [[0] * len(self.model_type)]
        # # TODO: rewrite the transition from I -> R
        # self.infection_phase_threshold = 7

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
        neighbor_states = {'S': 0, 'I': 0, 'R': 0, 'E': 0}
        # Count states of neighbours
        if self.neighbours == 'all':
            for c in range(self.width):
                for r in range(self.height):
                    if (c, r) != (x, y):
                        neighbor_states[self.cell_list[c][r].compartment] += 1
        # elif self.neighbours == 'gradient':
        #     for c in range(self.width):
        #         for r in range(self.height):
        #             if (c, r) != (x, y):
        #                 neighbor_states[self.cell_list[c][r].compartment] += math.log10(1-(1/self.get_dist((c, r), (x, y)))+1e-9)
        else:
            for x, y in self.get_neighbours(x, y):
                neighbor_states[self.cell_list[x][y].compartment] += 1
        # Get random number
        chance = random.random()
        # Return evaluated state
        if state == 'S' and chance < self.p_infect * neighbor_states['I']:
            # Make sure there is at least one infection
            if not self.has_infected:
                self.has_infected = True
            if self.model == 'SIR':
                return 'I'
            elif self.model == 'SEIR':
                return 'E'
        elif state == 'I' and chance < self.gamma and self.has_infected:
            return 'R'
        elif state == 'E' and chance < self.exposed_phase_threshold :
            return 'I'
        else:
            return state

    def cell_behaviour(self, x, y):

        state = self.cell_list[x][y].compartment

        if state == "I":
            if random.random() < self.gamma:
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
            for x, y in self.get_neighbours(x, y):
                if self.cell_list[x][y].compartment == 'S':
                    neighbourlist.append((x, y))

            if not neighbourlist:
                return transition, []
            elif len(neighbourlist) > infect_count:
                for _ in range(len(neighbourlist) - infect_count):
                    neighbourlist.remove(random.choice(neighbourlist))
            return transition, neighbourlist

        elif state == "E":
            if random.random() < self.delta:
                transition = True
            else:
                transition = False
            return transition, []

    def step(self):
        """ Steps one day ahead. Evaluates the state of all cells in the grid. """
        # Boolean to indicate no more infected cells
        done = True
        # Copy grid so updating of cells doesn't affect neighbor states
        temp = copy.deepcopy(self.cell_list)
        # new_agg_day = [0] * len(self.model_type)
        for col in range(self.width):
            for row in range(self.height):
                if self.modeltype == "S-based":
                    new_state = self.evaluate_cell(col, row)
                    if new_state == 'I':
                        done = False
                    temp[col][row].compartment = new_state
                    temp[col][row].add_compartment_day(temp[col][row].compartment)
                    # evaluate the new aggregated states
                    # TODO: je kan dit waarschijnlijk ook doen met een index functie, voor alle modellen zonder veel if's
                    # if self.model_type == 'SIR':
                    #     if temp[col][row].compartment == 'S':
                    #         new_agg_day[0] += 1
                    #     if temp[col][row].compartment == 'I':
                    #         new_agg_day[1] += 1
                    #     if temp[col][row].compartment == 'R':
                    #         new_agg_day[2] += 1
                else:
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
        return done

    def infect(self, x, y):
        """ Sets state of cell at x, y to I=infected. """
        self.cell_list[x][y].compartment = 'I'

    def kill(self, x, y):
        """ Sets state of cell at x, y to D=dead. """
        self.cell_list[x][y].compartment = 'D'

    def get_states(self):
        """ Returns a grid of state indicators. """
        classes = ['S', 'I', 'R', 'E']
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

    def run(self, verbose=False, model="SIR"):
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
            # Update state if verbose
            if verbose:
                message = f"[Timestep {len(history['S'])-1:3d}] " + "".join([f"{k}: {v[-1]:3d} " for k, v in history.items()])
                if self.in_notebook:
                    clear_output(wait=True)
                    display(message)
                else:
                    print(message, end="\r")
        # Final history update
        history = {k: history[k] + [v] for k, v in self.count_states(model).items()}
        # Return history
        return history

    @staticmethod
    def in_notebook():
        try:
            if 'IPKernelApp' not in get_ipython().config:
                return False
        except ImportError:
            return False
        return True

    @classmethod
    def simulate(cls, *args, verbose=False, **kwargs):
        """ Runs a full simulation. """
        grid = cls(*args, **kwargs)
        modified = []
        # Randomly infect
        infected = 0
        while infected < grid.infected:
            x, y = random.randint(0, grid.width-1), random.randint(0, grid.height-1)
            if (x, y) not in modified:
                grid.infect(x, y)
                modified.append((x, y))
                infected += 1
        # Randomly kill
        dead = 0
        while dead < grid.dead:
            x, y = random.randint(0, grid.width-1), random.randint(0, grid.height-1)
            if (x, y) not in modified:
                grid.kill(x, y)
                modified.append((x, y))
                dead += 1
        return grid.run(verbose)

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
