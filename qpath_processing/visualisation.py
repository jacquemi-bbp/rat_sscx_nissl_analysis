"""
visualisation module
"""

import matplotlib.pyplot as plt


def plot_densities(densities):
    """
    Plot the density per layers that represent the brain depth
    :param densities:  list of float (nb cells / mm3)
    """
    plt.plot([i for i in range(densities)], densities)
    plt.show()