"""
visualisation module
"""

import matplotlib.pyplot as plt
import numpy as np


def plot_densities(percentages, densities):
    """
    Plot the density per layers that represent the brain depth
    :param percentages: list of brain depth percentage (float)
    :param densities:  list of float (nb cells / mm3)
    """
    plt.plot(np.array(percentages) * 100, densities)
    plt.xlabel("percentage of depth (%)")
    plt.ylabel("Cell density (cells/mm3)")
    plt.title("Cell densities as function of pertcentage of depth")
    plt.show()