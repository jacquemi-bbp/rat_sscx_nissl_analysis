import configparser
import click
import pandas as pd
import ast

import matplotlib.pyplot as plt
from qupath_processing.boundary import (
    get_main_cluster,
    get_cell_coordinate_by_layers,
    compute_dbscan_eps,
    rotated_cells_from_top_line
)
from qupath_processing.io import (
    get_top_line_coordinates,
    write_dataframe_to_file)

from qupath_processing.visualisation import (
    plot_layers_cells,
    plot_layers_bounderies,
    locate_layers_bounderies
)



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

    try:
        layer_dbscan_eps = ast.literal_eval(config['DEFAULT']['layer_dbscan_eps'])
    except KeyError:
        layer_dbscan_eps = compute_dbscan_eps(cell_position_file_path,
                                              layers_name,)

    # Get data and metadata from input files
    layer_points = get_cell_coordinate_by_layers(cell_position_file_path)
    top_left, top_right = get_top_line_coordinates(annotations_path)

    # Apply cluster DBSCAN layer by layer
    layer_clustered_points = get_main_cluster(layers_name, layer_dbscan_eps,
                                              layer_points)
    if len(layer_clustered_points) == 0:
        return

    # Rotate the image as function of to top line to ease the length computation
    layer_rotatated_points, rotated_top_line = rotated_cells_from_top_line(top_left, top_right, layer_clustered_points)

    if visualisation_flag:
        plot_layers_cells(top_left, top_right, layer_points,
                          layer_clustered_points, rotated_top_line,
                          layer_rotatated_points)



    # Locate the layers boundarie
    final_result, y_lines, y_origin = locate_layers_bounderies(layer_rotatated_points, layers_name)

    # Write result to pandas and excel file
    dataframe = pd.DataFrame({''
                              'Layer': final_result.keys(),
                              'Layer bottom (um). Origin is top of layer 1': final_result.values()})
    write_dataframe_to_file(dataframe, file_prefix, output_path)

    print(dataframe)

    if visualisation_flag:
        #  Layer boundaries
        plot_layers_bounderies(layer_rotatated_points, final_result, y_lines,
                               rotated_top_line, y_origin, layers_name)







