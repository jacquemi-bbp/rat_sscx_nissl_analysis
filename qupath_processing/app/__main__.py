"""
Produces astrocyte morphology in HDF5 format from 3D meshes
"""
import configparser
import click
from qupath_processing.rat_sscx_nissl_processing import (
    single_image_process)
from qupath_processing.io import (
    write_densities_csv, read_pixel_size, list_images
)
'''
from qupath_processing.io import (
    write_densities_csv, read_pixel_size, list_images)
'''
from qupath_processing.version import VERSION

@click.version_option(VERSION)
@click.command()
@click.option('--config-file-path', required=False, help='Configuration file path')
@click.option('--cell-position-file-path', help='Cells position file path.', required=False)
@click.option('--annotations-geojson-path', help='Annotations geojson file path.', required=False)
@click.option('--pixel-file-path', help='Pixel size file path.', required=False)
@click.option('--thickness-cut', default=50, help='The thikness of the cut (default 50 um)')
@click.option('--nb-row', default=100, help='Number of row for the grid (default 100)')
@click.option('--nb-col', default=100, help='Number of columns for the grid (default 100)')
@click.option('--output-file-path', help='Output file path', required=False)
@click.option('--visualisation-flag', is_flag=True)
def process(config_file_path, cell_position_file_path, annotations_geojson_path, pixel_file_path,
            thickness_cut, nb_row, nb_col, output_file_path, visualisation_flag):
    if config_file_path:
        config = configparser.ConfigParser()
        config.sections()
        config.read(config_file_path)
        cell_position_file_path = config['DEFAULT']['cell_position_file_path']
        annotations_geojson_path = config['DEFAULT']['annotations_geojson_path']
        pixel_file_path = config['DEFAULT']['pixel_file_path']
        thickness_cut = float(config['DEFAULT']['thickness_cut'])
        nb_row = int(config['DEFAULT']['grid_nb_row'])
        nb_col = int(config['DEFAULT']['grid_nb_col'])
        output_file_path = config['DEFAULT']['output_file_path']
    pixel_size = read_pixel_size(pixel_file_path)
    print('INFO: Process single image')
    densities_dataframe = single_image_process(cell_position_file_path, annotations_geojson_path, pixel_size, thickness_cut,
                         nb_row, nb_col, visualisation_flag)
    print('INFO: ', densities_dataframe)
    print('INFO: Write results')
    write_densities_csv(densities_dataframe, output_file_path)



@click.version_option(VERSION)
@click.command()
@click.option('--config-file-path', required=False, help='Configuration file path')
def batch(config_file_path):
    config = configparser.ConfigParser()
    config.sections()
    config.read(config_file_path)

    input_directory = config['BATCH']['input_directory']
    cell_position_suffix = config['BATCH']['cell_position_suffix']
    annotations_geojson_suffix = config['BATCH']['annotations_geojson_suffix']
    output_directory = config['BATCH']['output_directory']
    pixel_size = float(config['BATCH']['pixel_size'])
    thickness_cut = float(config['BATCH']['thickness_cut'])
    grid_nb_row = int(config['BATCH']['grid_nb_row'])
    grid_nb_col = int(config['BATCH']['grid_nb_col'])

    image_dictionary = list_images(input_directory, cell_position_suffix, annotations_geojson_suffix)
    for image_prefix, values in image_dictionary.items():
        print('INFO: Process single image {}'.format(image_prefix))
        densities_dataframe = single_image_process(values['CELL_POSITIONS_PATH'], values['ANNOTATIONS_PATH'],
                                                   pixel_size, thickness_cut,
                                                   grid_nb_row, grid_nb_col)
        print('INFO: ', densities_dataframe)
        print('INFO: Write results for image {}'.format(image_prefix))
        write_densities_csv(densities_dataframe, output_directory + '/' + image_prefix + '.xlsx')