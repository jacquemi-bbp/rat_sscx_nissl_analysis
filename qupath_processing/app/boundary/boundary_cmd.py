import configparser
import click
import numpy as np
import ast

import matplotlib.pyplot as plt
from qupath_processing.boundary import (
    clustering,
    get_cell_coordinate_by_layers,
    rotate_points_list
)
from qupath_processing.io import get_top_line_coordinates
from qupath_processing.utilities import get_angle


@click.command()
@click.option('--config-file-path', required=True, help='Configuration file path')
@click.option('--output-path',  required=True, help='Output path where result files will be save')
@click.option('--visualisation-flag', is_flag=True)
def cmd(config_file_path, output_path, visualisation_flag):

    config = configparser.ConfigParser()
    config.sections()
    config.read(config_file_path)
    cell_position_file_path = config['DEFAULT']['cell_position_file_path']
    annotations_path = config['DEFAULT']['annotations_path']
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
    for layer_label, XY in layer_rotatated_points.items():
        y_coors = XY[:, 1]
        layer_ymin = y_coors[y_coors.argsort()[0:10]].mean()
        y_lines.append(layer_ymin)
        final_result[layer_label] = layer_ymin - y_origin

    if visualisation_flag:

        x_values = [top_left[0], top_right[0]]
        y_values = [top_left[1], top_right[1]]

        fig, axs = plt.subplots(2, 2, figsize=(8, 8))
        axs[0][0].invert_yaxis()
        axs[0][0].plot(x_values, y_values, c='black')
        for XY in layer_points.values():
            axs[0][0].scatter(XY[:, 0], XY[:, 1], s=2, alpha=0.8)
        axs[0][0].set_title('Origin points per layer')


        axs[0][1].invert_yaxis()
        for XY in layer_clustered_points.values():
            axs[0][1].scatter(XY[:, 0], XY[:, 1], s=2, alpha=0.8)
            axs[0][1].set_title('After removing points outside the clusters')
            axs[0][1].plot(x_values, y_values, c='black')

        axs[1][0].invert_yaxis()
        x_values = [rotated_points[0][0], rotated_points[1][0]]
        y_values = [rotated_points[0][1], rotated_points[1][1]]
        axs[1][0].plot(x_values, y_values, c='black')
        for XY in layer_rotatated_points.values():
            axs[1][0].scatter(XY[:, 0], XY[:, 1], s=2, alpha=0.8)
        axs[1][0].set_title('After clustering and rotation')
        plt.show()

        # Display layer boundaries
        for layer_label, XY in layer_rotatated_points.items():
            plt.scatter(XY[:, 0], XY[:, 1] - y_origin, s=10, alpha=.5)
            y_coors = XY[:, 1]
            x_coors = XY[:, 0]

            layer_ymin = y_coors[y_coors.argsort()[0:10]].mean()
            layer_ymax = y_coors[y_coors.argsort()[-10:-1]].mean()
            xmean = x_coors.mean()
            y_lines.append(layer_ymin)
            plt.hlines(layer_ymin - y_origin, XY[:, 0].min(), XY[:, 0].max(),
                       color='black')
            final_result[layer_label] = layer_ymin - y_origin

        y_lines.append(layer_rotatated_points['Layer 6b'][:, 1].max())

        half_letter_size = 10
        y_0 = y_lines[0]
        for y_1, layer_name in zip(y_lines[1:],
                                   ['Layer 1', 'Layer 2', 'Layer 3', 'Layer 4',
                                    'Layer 5',
                                    'Layer 6 a', 'Layer 6b']):
            y = (y_0 + y_1) / 2
            plt.text(xmean, y - y_origin + half_letter_size, layer_name,
                     size='xx-large')
            y_0 = y_1

        plt.show()


    print(f'INFO final result {final_result}')






