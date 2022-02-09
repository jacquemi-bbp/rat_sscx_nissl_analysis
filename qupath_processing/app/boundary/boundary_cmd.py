import configparser
import click
import numpy as np
import pandas as pd
import ast

import matplotlib.pyplot as plt
from qupath_processing.boundary import (
    clustering,
    get_cell_coordinate_by_layers,
    rotate_points_list
)
from qupath_processing.io import get_top_line_coordinates, write_dataframe_to_file
from qupath_processing.utilities import get_angle


@click.command()
@click.option('--config-file-path', required=True, help='Configuration file path')
@click.option('--visualisation-flag', is_flag=True)
def cmd(config_file_path, visualisation_flag):

    config = configparser.ConfigParser()
    config.sections()
    config.read(config_file_path)
    cell_position_file_path = config['DEFAULT']['cell_position_file_path']
    annotations_path = config['DEFAULT']['annotations_path']
    output_path = config['DEFAULT']['output_path']
    file_prefix = config['DEFAULT']['file_prefix']
    layers_name = ast.literal_eval(config['DEFAULT']['layers_name'])


    # Get data and metadata from input files
    layer_points = get_cell_coordinate_by_layers(cell_position_file_path)
    top_left, top_right = get_top_line_coordinates(annotations_path)

    # Apply cluster DBSCAN layer by layer
    layer_clustered_points = {}
    layer_list = ['Layer 1', 'Layer 2', 'Layer 3', 'Layer 4', 'Layer 5',
                  'Layer 6 a', 'Layer 6b']
    layer_dbscan_eps = [150, 70, 50, 40, 50, 50, 50]
    for layer_name, eps_value in zip(layer_list, layer_dbscan_eps):
        layer_clustered_points[layer_name] = clustering(layer_name,
                                                        layer_points[
                                                            layer_name],
                                                        eps_value, log=False,
                                                        figure=False)

    # Rotate the image as function of to top line to ease the length computation
    theta = - get_angle(top_left, top_right)
    layer_rotatated_points = {}
    for layer_label, XY in layer_clustered_points.items():
        layer_rotatated_points[layer_label] = rotate_points_list(XY, theta)

    top_points = np.array([top_left, top_right]).reshape(-1, 2)
    rotated_points = rotate_points_list(top_points, theta)



    # Locate the layers boundarie

    y_origin = layer_rotatated_points['Layer 1'][:, 1].min()

    final_result = {}
    y_lines = []
    for layer_label in layer_list:
        XY = layer_rotatated_points[layer_label]
        y_coors = XY[:, 1]
        layer_ymax = y_coors[y_coors.argsort()[-10:-1]].mean()
        y_lines.append(layer_ymax)
        final_result[layer_label] = layer_ymax - y_origin

    # Write result to pandas and excel file
    dataframe = pd.DataFrame({''
                              'Layers': final_result.keys(),
                              'bottom layer boundary': final_result.values()})
    write_dataframe_to_file(dataframe, file_prefix, output_path)

    if visualisation_flag:

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
        x_values = [rotated_points[0][0], rotated_points[1][0]]
        y_values = [rotated_points[0][1], rotated_points[1][1]]
        axs[2].plot(x_values, y_values, c='black')
        for XY in layer_rotatated_points.values():
            axs[2].scatter(XY[:, 0], XY[:, 1], s=6, alpha=1.)
        axs[2].set_title('After clustering and rotation')
        plt.show()

        #  Layer boundaries
        plt.figure(figsize=(8, 8))
        plt.gca().invert_yaxis()
        for layer_label, XY in layer_rotatated_points.items():
            plt.scatter(XY[:, 0], XY[:, 1] - y_origin, s=10, alpha=.5)
            y = final_result[layer_label]
            plt.hlines(y, XY[:, 0].min(), XY[:, 0].max(),
                       color='red')
        y_lines.append(layer_rotatated_points['Layer 6b'][:, 1].max())
        half_letter_size = 10

        x_values = [rotated_points[0][0], rotated_points[1][0]]
        y_values = [rotated_points[0][1], rotated_points[1][1]] - y_origin
        plt.plot(x_values, y_values, c='black')
        y_0 = y_origin

        for y_1, layer_name in zip(y_lines,
                                   ['Layer 1', 'Layer 2', 'Layer 3', 'Layer 4',
                                    'Layer 5',
                                    'Layer 6 a', 'Layer 6b']):

            x_coors = XY[:, 0]
            xmean = x_coors.mean()
            y = (y_0 + y_1) / 2
            print(
                f'DEBUG lyer_name {layer_name} {y - y_origin + half_letter_size}')
            plt.text(xmean, y - y_origin + half_letter_size, layer_name,
                     size='xx-large')
            y_0 = y_1

        plt.show()




    print(f'INFO final result {final_result}')






