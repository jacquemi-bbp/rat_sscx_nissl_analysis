import configparser
import click
import ast
import pandas as pd
import numpy as np

from qupath_processing.io import (
    write_dataframe_to_file, list_images,
    read_qupath_annotations, get_qpproject_images_metadata,
    create_directory_if_not_exist
)
from qupath_processing.utilities import (
        concat_dataframe, NotValidImage,
        get_image_immunohistochemistry,
        get_image_animal,
        get_image_lateral
)

from qupath_processing.boundary import (
    get_main_cluster,
    get_cell_coordinate_by_layers,
    compute_dbscan_eps,
    rotated_cells_from_top_line,
    locate_layers_bounderies
)

from qupath_processing.visualisation import plot_layers_bounderies


@click.command()
@click.option('--config-file-path', required=False, help='Configuration file path')
def batch_boundary(config_file_path):
    config = configparser.ConfigParser()
    config.sections()
    config.read(config_file_path)

    input_directory = config['BATCH']['input_directory']
    cell_position_suffix = config['BATCH']['cell_position_suffix'].replace("\"","")
    annotations_geojson_suffix = config['BATCH']['annotations_geojson_suffix'].replace("\"","")
    output_directory = config['BATCH']['output_directory']
    pixel_size = float(config['BATCH']['pixel_size'])
    layers_name = ast.literal_eval(config['BATCH']['layers_name'])
    layer_dbscan_eps = ast.literal_eval(config['BATCH']['layer_dbscan_eps'])
    output_file_prefix = config['BATCH']['output_file_prefix']
    qpproj_path = config['BATCH']['qpproj_path']

    image_dictionary = list_images(input_directory, cell_position_suffix, annotations_geojson_suffix)
    print(f'INFO: input files: {list(image_dictionary.keys())}')
    if len(image_dictionary) == 0:
        print('WARNING: No input files to proccess.')
        return

    image_metadata = get_qpproject_images_metadata(qpproj_path)
    images_lateral = get_image_lateral(image_metadata)
    images_immunohistochemistry = get_image_immunohistochemistry(image_metadata)
    images_animal = get_image_animal(image_metadata)

    final_dataframe = None
    for image_prefix, values in image_dictionary.items():
        print('INFO: Process single image {}'.format(image_prefix))
        print(values['CELL_POSITIONS_PATH'], values['ANNOTATIONS_PATH'])
        image_name = values['IMAGE_NAME']


        bregma = images_lateral[image_name]
        animal = images_animal[image_name]
        immunohistochemistry = images_immunohistochemistry[image_name]
        print(f'INFO: {image_name} is {bregma}, {animal} {immunohistochemistry}')

        # Get data and metadata from input files
        layer_points = get_cell_coordinate_by_layers(values['CELL_POSITIONS_PATH'], layers_name)

        # top_left, top_right = get_top_line_coordinates(annotations_path)
        s1_pixel_coordinates, quadrilateral_pixel_coordinates, out_of_pia = read_qupath_annotations( values['ANNOTATIONS_PATH'])
        top_left = quadrilateral_pixel_coordinates[0] * pixel_size
        top_right = quadrilateral_pixel_coordinates[1] * pixel_size

        # Apply cluster DBSCAN layer by layer
        layer_clustered_points = get_main_cluster(layers_name, layer_dbscan_eps,
                                                  layer_points)

        # Rotate the image as function of to top line to ease the length computation
        layer_rotatated_points, rotated_top_line = rotated_cells_from_top_line(top_left, top_right,
                                                                               layer_clustered_points)

        # Locate the layers boundaries
        boundaries_bottom, y_lines, y_origin = locate_layers_bounderies(layer_rotatated_points, layers_name)

        # Write result to pandas and excel file
        layers = []
        absolute = []
        percentage = []
        for name, bottom in boundaries_bottom.items():
            layers.append(name)
            absolute.append(bottom[0])
            percentage.append(bottom[1])

        dataframe = pd.DataFrame({'image': image_name,
                                  'bregma': bregma,
                                  'animal': animal,
                                  'immunohistochemistry ID': immunohistochemistry,
                                  'Layer': layers,
                                  'Layer bottom (um). Origin is top of layer 1': absolute,
                                  'Layer bottom (percentage). Origin is top of layer 1': percentage})
        #write_dataframe_to_file(dataframe, image_name, output_directory)

        create_directory_if_not_exist(output_directory)

        plot_layers_bounderies(layer_rotatated_points, boundaries_bottom, y_lines,
                               rotated_top_line, y_origin, layers_name, image_name, output_directory, False)

        final_dataframe = concat_dataframe(dataframe, final_dataframe)

    write_dataframe_to_file(final_dataframe, output_file_prefix, output_directory)
