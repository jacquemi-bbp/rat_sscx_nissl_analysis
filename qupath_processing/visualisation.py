"""
visualisation module
"""

import matplotlib.pyplot as plt
import numpy as np
from qupath_processing.geometry import compute_cells_depth


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


def plot_split_polygons_and_cell_depth(split_polygons, s1_coordinates,
                                       cells_centroid_x, cells_centroid_y):
    """
    Plot splitted S1 polgygons and cell coordiantes and depth
    :param split_polygons: list of shapely polygons representing S1 layers as
    function if brain depth
    :param s1_coordinates:(np.array) of shape (nb_vertices, 2) containing S1
    polygon coordinates (mm
    :param cells_centroid_x: np.array of shape (number of cells, ) of type float
    :param cells_centroid_y: np.array of shape (number of cells, ) of type float
    :return:
    """

    cells_depth = compute_cells_depth(split_polygons, cells_centroid_x,
                                      cells_centroid_y)
    fig = plt.figure()
    fig.set_size_inches(18.5, 10.5)
    plt.axis('equal')
    plt.gca().invert_yaxis()
    for polygon in split_polygons:
        x, y = polygon.exterior.xy
        plt.plot(x, y)
    plt.plot(s1_coordinates[:, 0], s1_coordinates[:, 1], 'r')
    plt.scatter(cells_centroid_x, cells_centroid_y,
                c=np.array(cells_depth) / 100, s=1)
    plt.show()
