import numpy as np
import matplotlib.pyplot as plt

from tqdm import tqdm

from grid import Grid
from main import SIRGui
from SIR import SIR as Mat_SIR



class Experiment:

    def __init__(self, size, **kwargs):
        """ 
        Experiment

        Compares mathematical SIR with cellular SIR. 

        Args:
            size ((int, int)):  Tuple containing simulation dimensions.

        Kwargs:
            N (int):            Number of simulations to run.
                                Default is 10. 
            neighbours (str):   Which cells to consider neighbours;
                                radius, random, gauss or all
                                Default is radius.

        """
        self.size = size
        self.N = kwargs.get('N', 10)
        self.neighbours = kwargs.get('neighbours', 'all')

    def run(self):
        """ Runs the experiment. """
        MA_stats = []
        CA_stats = []
        for _ in tqdm(range(1, self.N+1)):
            # Run mathematical model and store results
            results = Mat_SIR(self.size[0]*self.size[1], 2.2, 2.9, 1, 150, 'SIR')
            MA_stats.append(results)
            # Run cellular model and store results
            results = Grid.simulate(self.size[0], self.size[1], self.neighbours)
            CA_stats.append(results)
        # Average and rapport results
        self.compute_stats(MA_stats, CA_stats)

    def compute_stats(self, MA_stats, CA_stats):
        """ Computes evaluation metrics based of history. """
        MA_eval = {}
        CA_eval = {}
        # Durations of the pandemic
        MA_eval['duration'] = np.array([len(sim['I']) for sim in MA_stats])
        CA_eval['duration'] = np.array([len(sim['I']) for sim in CA_stats])
        # Total infected
        MA_eval['total_infected'] = np.array([max(sim['R']) for sim in MA_stats])
        CA_eval['total_infected'] = np.array([max(sim['R']) for sim in CA_stats])
        # Max infected at one time
        MA_eval['max_infected'] = np.array([max(sim['I']) for sim in MA_stats])
        CA_eval['max_infected'] = np.array([max(sim['I']) for sim in CA_stats])
        # Print stats
        for k, v in MA_eval.items():
            print(f"MA {k} avg: {v.mean():.2f} std: {v.std():.2f}")
        for k, v in CA_eval.items():
            print(f"CA {k} avg: {v.mean():.2f} std: {v.std():.2f}")

    def plot_history(self, history):
        S = history['S']
        I = history['I']
        R = history['R']
        X = list(range(1, len(S) + 1))
        fig = plt.figure(figsize=(12, 5))
        plt.subplot(1, 2, 1)
        plt.plot(X, S, label='Susceptible')
        plt.plot(X, I, label='Infected')
        plt.plot(X, R, label='Recovered')
        plt.legend()
        plt.subplot(1, 2, 2)
        plt.stackplot(X, I, S, R, labels=['Infected', 'Susceptible', 'Recovered'], colors=['#ff7f0e', '#1f77b4', '#2ca02c', '#d62728'])
        handles, labels = plt.gca().get_legend_handles_labels()
        order = [1, 0, 2]
        plt.legend([handles[idx] for idx in order], [labels[idx] for idx in order], loc='center right')
        fig.show()
        input('Press enter to exit...')





if __name__ == "__main__":

    exp = Experiment((21, 21), N=3)
    exp.run()