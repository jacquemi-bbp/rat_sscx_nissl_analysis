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
                                       cells_centroid_x, cells_centroid_y,
                                       vertical_lines=None):
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
        x_coord, y_coord = polygon.exterior.xy
        plt.plot(x_coord, y_coord)
    plt.plot(s1_coordinates[:, 0], s1_coordinates[:, 1], 'r')
    plt.scatter(cells_centroid_x, cells_centroid_y,
               c=np.array(cells_depth) / 100, s=1)
    if vertical_lines:
        for line in vertical_lines:
            line = np.array(line)
            plt.axline((line[0][0], line[0][1]), (line[1][0], line[1][1]), color='red')
    plt.title('Somatosensory cortex. Each layer represents a percentage of depth following the top of the SSX')
    plt.xlabel("X coordinates (um)")
    plt.ylabel("Y coordinates (um)")
    plt.show()


def plot_layers_cells(top_left, top_right, layer_points, layer_clustered_points,
                      rotated_top_line, layer_rotatated_points):
    """
    Display 3 plots:
        - The original cells coordinates with top_line
        - The main cluster per layers cells with top_line
        - The rotated main cluster per layers cells with rotated top_line
    :param top_left:
    :param top_right:
    :param layer_points:
    :param layer_clustered_points:
    :param rotated_top_line:
    :param layer_rotatated_points:
    """
    x_values = [top_left[0], top_right[0]]
    y_values = [top_left[1], top_right[1]]

    # ORIGINAL CELLS
    fig, axs = plt.subplots(1, 3, figsize=(12, 4))
    axs[0].invert_yaxis()
    axs[0].plot(x_values, y_values, c='black')
    for XY in layer_points.values():
        axs[0].scatter(XY[:, 0], XY[:, 1], s=6, alpha=1.)
    axs[0].set_title('Origin points per layer')

    # CELLS from the main cluster (after DBSCAN)
    axs[1].invert_yaxis()
    for XY in layer_clustered_points.values():
        axs[1].scatter(XY[:, 0], XY[:, 1], s=6, alpha=1.)
        axs[1].set_title('After removing points outside the clusters')
        axs[1].plot(x_values, y_values, c='black')

    # ROTATED CELLS fron the main cluster
    axs[2].invert_yaxis()
    x_values = [rotated_top_line[0][0], rotated_top_line[1][0]]
    y_values = [rotated_top_line[0][1], rotated_top_line[1][1]]
    axs[2].plot(x_values, y_values, c='black')
    for XY in layer_rotatated_points.values():
        axs[2].scatter(XY[:, 0], XY[:, 1], s=6, alpha=1.)
    axs[2].set_title('After clustering and rotation')
    plt.show()


def plot_layers_bounderies(layer_rotatated_points, final_result, y_lines,
                           rotated_top_line, y_origin, layers_name):
    """
    Display layers boundaries
    :param layer_rotatated_points:
    :param final_result:
    :param y_lines:
    :param rotated_top_line:
    :param y_origin:
    :param layers_name:
    """
    plt.figure(figsize=(8, 8))
    plt.gca().invert_yaxis()
    for layer_label, XY in layer_rotatated_points.items():
        plt.scatter(XY[:, 0], XY[:, 1] - y_origin, s=10, alpha=.5)
        y = final_result[layer_label]
        plt.hlines(y, XY[:, 0].min(), XY[:, 0].max(),
                   color='red')
    y_lines.append(layer_rotatated_points['Layer 6b'][:, 1].max())
    half_letter_size = 10

    x_values = [rotated_top_line[0][0], rotated_top_line[1][0]]
    y_values = [rotated_top_line[0][1], rotated_top_line[1][1]] - y_origin
    plt.plot(x_values, y_values, c='black')
    y_0 = y_origin

    for y_1, layer_name in zip(y_lines, layers_name):
        x_coors = XY[:, 0]
        xmean = x_coors.mean()
        y = (y_0 + y_1) / 2
        plt.text(xmean, y - y_origin + half_letter_size, layer_name,
                 size='xx-large')
        y_0 = y_1
    plt.title('Layers bottom boundaries (um) . The bottom of each layer since it\'s assumed that Layers 1 starts at 0.')
    plt.xlabel("X cells' coordinates (um)")
    plt.ylabel("Cells distance from Layer1 top coordinate (um)")
    plt.show()

