"""
visualisation module
"""

import matplotlib.pyplot as plt
import numpy as np
from qupath_processing.geometry import compute_cells_depth


def plot_densities(percentages, densities, boundaries_percentage=None, image_name=""):
    """
    Plot the density per layers that represent the brain depth
    :param percentages: list of brain depth percentage (float)
    :param densities:  list of float (nb cells / mm3)
    :param boundaries_percentage:
    :param image_name:
    """

    fig, ax = plt.subplots()
    if boundaries_percentage:
        layers_names = ["Layer 1", "Layer 2", "Layer 3", "Layer 4", "Layer 5", "Layer 6 a", "Layer 6b"]
        boundaries_percentage.insert(0, 0)
        for layer_name, boundary_prev, boundary_next in zip(layers_names, boundaries_percentage[0:-1],
                                                            boundaries_percentage[1:]):
            center = int((boundary_next + boundary_prev) * 100 / 2)
            ax.axvline(boundary_prev*100, color='red', markersize=2)
            ax.annotate(layer_name, xy=(center-3, int(np.max(densities))), color='red')

    ax.plot(np.array(percentages) * 100, densities)
    ax.set_xlabel("percentage of depth (%)")
    ax.set_ylabel("Cell density (cells/mm3)")
    title = "Cell densities as function of percentage of depth"
    if image_name :
        title = image_name + " " + title
    ax.set_title(title)


    #percentages = [0.0, .1, .2, .3, .4, .5, .6, .7, .8, .9]
    #densities = [53643., 106323., 103229., 95383., 85405., 93651., 93482., 93826., 90305., 88825.]

    x = np.array(percentages) * 100  # the label locations

    width = 100 / len(percentages)  # the width of the bars


    rects2 = ax.bar(x + width / 2, densities, width, label='Cells density', color='plum', edgecolor='plum')

    # Add some text for labels, title and custom x-axis tick labels, etc.
    # ax.set_ylabel('cell densities')
    # ax.set_title('cell densities as function of brain depth')
    ax.set_xticks(x, percentages)
    #ax.legend()

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


def plot_raw_data(top_left, top_right, layer_points, image_name=''):
    """
    Display raw data cells and top line:
        - The original cells coordinates with top_line
        - The main cluster per layers cells with top_line
        - The rotated main cluster per layers cells with rotated top_line
    :param top_left:
    :param top_right:
    :param layer_points:
    """
    x_values = [top_left[0], top_right[0]]
    y_values = [top_left[1], top_right[1]]

    plt.figure(figsize=(8, 6))
    plt.gca().invert_yaxis()
    plt.plot(x_values, y_values, c='black')
    for XY in layer_points.values():
        plt.scatter(XY[:, 0], XY[:, 1], s=6, alpha=1.)
    plt.title(image_name + ' Raw data cells (one color per layer)')
    plt.show()


def plot_cluster_cells(top_left, top_right, layer_clustered_points, image_name=''):
    """
    Display cells from the main cluster for ech layer:
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

    plt.figure(figsize=(8, 6))

    # CELLS from the main cluster (after DBSCAN)
    plt.gca().invert_yaxis()
    for XY in layer_clustered_points.values():
        plt.scatter(XY[:, 0], XY[:, 1], s=6, alpha=1.)
        plt.title(image_name + ' After removing points outside the clusters')
        plt.plot(x_values, y_values, c='black')
    plt.show()


def plot_rotated_cells(rotated_top_line, layer_rotatated_points, image_name=''):
    """
    Display rotatated cell and top line:
        - The original cells coordinates with top_line
        - The main cluster per layers cells with top_line
        - The rotated main cluster per layers cells with rotated top_line
    :param rotated_top_line:
    :param layer_rotatated_points:
    """

    plt.figure(figsize=(8, 6))
    # ROTATED CELLS fron the main cluster
    plt.gca().invert_yaxis()
    x_values = [rotated_top_line[0][0], rotated_top_line[1][0]]
    y_values = [rotated_top_line[0][1], rotated_top_line[1][1]]
    plt.plot(x_values, y_values, c='black')
    for XY in layer_rotatated_points.values():
        if XY.shape[0] > 0:
            plt.scatter(XY[:, 0], XY[:, 1], s=6, alpha=1.)
    plt.title(image_name + ' After clustering and rotation')
    plt.show()


def plot_layers_bounderies(layer_rotatated_points, boundaries_bottom, y_lines,
                           rotated_top_line, y_origin, layers_name, image_name, output_path, visualisation_flag=False):
    """
    Display layers boundaries
    :param layer_rotatated_points:
    :param boundaries_bottom: list [0] -> absolute boundary [1] -> percentage boundary
    :param y_lines:
    :param rotated_top_line:
    :param y_origin:
    :param layers_name:
    :param image_name:
    :param output_path:
    :param visualisation_flag:
    """
    plt.figure(figsize=(8, 8))
    plt.gca().invert_yaxis()
    x_means = []
    for layer_label, XY in layer_rotatated_points.items():
        if XY.size > 0:
            plt.scatter(XY[:, 0], XY[:, 1] - y_origin, s=10, alpha=.5)
            y = boundaries_bottom[layer_label][0]
            plt.hlines(y, XY[:, 0].min(), XY[:, 0].max(),
                       color='red')
            x_means.append( XY[:, 0].mean())
    if 'Layer 6 b' in layer_rotatated_points:
        y_lines.append(layer_rotatated_points['Layer 6 b'][:, 1].max())
    half_letter_size = 10

    x_values = [rotated_top_line[0][0], rotated_top_line[1][0]]
    y_values = [rotated_top_line[0][1], rotated_top_line[1][1]] - y_origin
    plt.plot(x_values, y_values, c='black')
    y_0 = y_origin

    for y_1, layer_name, xmean in zip(y_lines, layers_name, x_means):
        y = (y_0 + y_1) / 2
        plt.text(xmean, y - y_origin + half_letter_size, layer_name,
                 size='xx-large')
        y_0 = y_1
    plt.title(image_name + ' Layers bottom boundaries (um) . The bottom of each layer since it\'s assumed that Layers 1 starts at 0.')
    plt.xlabel("X cells' coordinates (um)")
    plt.ylabel("Cells distance from Layer1 top coordinate (um)")
    if visualisation_flag:
        plt.show()
    else:
        file_path = output_path + '/' + image_name + '.png'
        plt.savefig(file_path, dpi=150)

