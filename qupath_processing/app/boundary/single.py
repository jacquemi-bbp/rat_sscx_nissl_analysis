import configparser
import click
import pandas as pd
import ast

from qupath_processing.boundary import (
    get_main_cluster,
    get_cell_coordinate_by_layers,
    compute_dbscan_eps,
    rotated_cells_from_top_line,
    locate_layers_bounderies
)
from qupath_processing.io import (
    read_qupath_annotations,
    write_dataframe_to_file)

from qupath_processing.visualisation import (
    plot_rotated_cells,
    plot_cluster_cells,
    plot_layers_bounderies,
    plot_raw_data
)



@click.command()
@click.option('--config-file-path', required=True, help='Configuration file path')
@click.option('--visualisation-flag', is_flag=True)
def cmd(config_file_path, visualisation_flag):

    # READ configuration
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
                                              layers_name)
    print(f'INFO: layer dbscan eps values {layer_dbscan_eps}')

    # Get data and metadata from input files
    layer_points = get_cell_coordinate_by_layers(cell_position_file_path, layers_name)

    #top_left, top_right = get_top_line_coordinates(annotations_path)
    s1_pixel_coordinates, quadrilateral_pixel_coordinates = read_qupath_annotations(annotations_path)
    pixel_size = 0.3460130331522824
    top_left = quadrilateral_pixel_coordinates[0] * pixel_size
    top_right = quadrilateral_pixel_coordinates[1] * pixel_size

    if visualisation_flag:
        plot_raw_data(top_left, top_right, layer_points, file_prefix)


    # Apply cluster DBSCAN layer by layer
    layer_clustered_points = get_main_cluster(layers_name, layer_dbscan_eps,
                                              layer_points)

    plot_cluster_cells(top_left, top_right, layer_clustered_points, file_prefix)



    # Rotate the image as function of to top line to ease the length computation
    layer_rotatated_points, rotated_top_line = rotated_cells_from_top_line(top_left, top_right, layer_clustered_points)

    if visualisation_flag:
        plot_rotated_cells(rotated_top_line, layer_rotatated_points, file_prefix)

    # Locate the layers boundaries
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
                               rotated_top_line, y_origin, layers_name, file_prefix)


