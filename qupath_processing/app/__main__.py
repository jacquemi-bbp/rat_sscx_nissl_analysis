"""
Processing for rat somatosensory cortex QuPath Nissl data
"""
import configparser
import click
from qupath_processing.rat_sscx_nissl_processing import (
    single_image_process)
from qupath_processing.io import (
    write_densities_file, read_pixel_size, list_images
)
from qupath_processing.utilities import (
        concat_dataframe, NotValidImage
)
from qupath_processing.version import VERSION

@click.version_option(VERSION)
@click.command()
@click.option('--config-file-path', required=False, help='Configuration file path')
@click.option('--cell-position-file-path', help='Cells position file path.', required=False)
@click.option('--annotations-geojson-path', help='Annotations geojson file path.', required=False)
@click.option('--pixel-size', help='Pixel size (default 0.3460130331522824)', required=False, type=float, default=0.3460130331522824)
@click.option('--thickness-cut', default=50, help='The thikness of the cut (default 50 um)')
@click.option('--nb-row', default=100, help='Number of row for the grid (default 100)')
@click.option('--nb-col', default=100, help='Number of columns for the grid (default 100)')
@click.option('--output-path', help='Output path where result files will be save', required=False)
@click.option('--visualisation-flag', is_flag=True)
def process(config_file_path, cell_position_file_path, annotations_geojson_path, pixel_size,
            thickness_cut, nb_row, nb_col, output_path, visualisation_flag):
    if config_file_path:
        config = configparser.ConfigParser()
        config.sections()
        config.read(config_file_path)
        cell_position_file_path = config['DEFAULT']['cell_position_file_path']
        annotations_geojson_path = config['DEFAULT']['annotations_geojson_path']
        pixel_size = float(config['DEFAULT']['pixel_size'])
        thickness_cut = float(config['DEFAULT']['thickness_cut'])
        nb_row = int(config['DEFAULT']['grid_nb_row'])
        nb_col = int(config['DEFAULT']['grid_nb_col'])
        output_path = config['DEFAULT']['output_path']
    else:
        if output_path == None:
            print('ERROR --output-path is required')

    image_name = cell_position_file_path[cell_position_file_path.rfind('/')+1:cell_position_file_path.rfind('.')]
    print('INFO: Process single image ', image_name)
    densities_dataframe = single_image_process(cell_position_file_path, annotations_geojson_path, pixel_size, thickness_cut,
                         nb_row, nb_col, image_name,  visualisation_flag=visualisation_flag)
    print('INFO: ', densities_dataframe)
    print('INFO: Write results')
    write_densities_file(densities_dataframe, image_name, output_path)



@click.version_option(VERSION)
@click.command()
@click.option('--config-file-path', required=False, help='Configuration file path')
def batch(config_file_path):
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
                                                    pixel_size, thickness_cut,
                                                    grid_nb_row, grid_nb_col, image_prefix)
            print('INFO: ', densities_dataframe)
            print('INFO: Concatenate results for image {}'.format(image_prefix))
            final_dataframe = concat_dataframe(densities_dataframe, final_dataframe)
        except NotValidImage:
            print('WARNING. No cells position data for {}'.format(image_prefix))

    write_densities_file(final_dataframe, output_file_prefix,  output_directory)
