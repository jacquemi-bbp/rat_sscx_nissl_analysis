import configparser
import click
from qupath_processing.density import (
    single_image_process)
from qupath_processing.io import (
    write_dataframe_to_file, list_images
)
from qupath_processing.utilities import (
        concat_dataframe, NotValidImage
)


@click.command()
@click.option('--config-file-path', required=False, help='Configuration file path')
def batch_density(config_file_path):
    config = configparser.ConfigParser()
    config.sections()
    config.read(config_file_path)

    input_directory = config['BATCH']['input_directory']
    cell_position_suffix = config['BATCH']['cell_position_suffix'].replace("\"","")
    annotations_geojson_suffix = config['BATCH']['annotations_geojson_suffix'].replace("\"","")
    output_directory = config['BATCH']['output_directory']
    output_file_prefix = config['BATCH']['output_file_prefix']
    pixel_size = float(config['BATCH']['pixel_size'])
    thickness_cut = float(config['BATCH']['thickness_cut'])
    grid_nb_row = int(config['BATCH']['grid_nb_row'])
    grid_nb_col = int(config['BATCH']['grid_nb_col'])
    layer_names = config['BATCH']['layer_names']

    image_dictionary = list_images(input_directory, cell_position_suffix, annotations_geojson_suffix)
    print(f'INFO: input files: {list(image_dictionary.keys())}')
    if len(image_dictionary) == 0:
        print('WARNING: No input files to proccess.')
        return
    final_dataframe = None
    for image_prefix, values in image_dictionary.items():
        print('INFO: Process single image {}'.format(image_prefix))
        try:
            densities_dataframe = single_image_process(values['CELL_POSITIONS_PATH'], values['ANNOTATIONS_PATH'],
                                                        pixel_size, thickness_cut, grid_nb_row, grid_nb_col,
                                                       image_prefix, layer_names, visualisation_flag=False,
                                                       output_path=output_directory)
            print('INFO: ', densities_dataframe)
            print('INFO: Concatenate results for image {}'.format(image_prefix))
            final_dataframe = concat_dataframe(densities_dataframe, final_dataframe)
        except NotValidImage:
            print('WARNING. No cells position data for {}'.format(image_prefix))

    if final_dataframe is not None:
        write_dataframe_to_file(final_dataframe, output_file_prefix,  output_directory)
