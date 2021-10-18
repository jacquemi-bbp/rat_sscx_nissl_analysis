"""
Produces astrocyte morphology in HDF5 format from 3D meshes
"""
import configparser
import click
from qpath_processing.rat_SSCX_Nissl_processing import (
    process_inputs,
    process_layers_inputs,
    compute_densities,
    save_results)
from qpath_processing.version import VERSION

@click.version_option(VERSION)
@click.command()
@click.option('--config-file-path', required=False, help='Configuration file path')
@click.option('--cell-position-file_path', help='Cells position file path.', required=False)
@click.option('--s1-geojson-path', help='s1 geojson file path.', required=False)
@click.option('--pixel-file-path', help='pixel size file path.', required=False)
@click.option('--thickness-cut', default=50, help='The thikness of the cut (default 50 um)')
@click.option('--nb-slices', default=100, help='Number of slices (default 100)')
@click.option('--output-file-path', help='output file path', required=False)
@click.option('--visualisation-flag', is_flag=True)
def process(config_file_path, cell_position_file_path, s1_geojson_path, pixel_file_path,
            thickness_cut, nb_slices, output_file_path, visualisation_flag):
    if config_file_path:
        config = configparser.ConfigParser()
        config.sections()
        config.read(config_file_path)
        cell_position_file_path = config['DEFAULT']['cell_position_file_path']
        s1_geojson_path = config['DEFAULT']['s1_geojson_path']
        pixel_file_path = config['DEFAULT']['pixel_file_path']
        thickness_cut = float(config['DEFAULT']['thickness_cut'])
        nb_slices = int(config['DEFAULT']['nb_slices'])
        output_file_path = config['DEFAULT']['output_file_path']

    cells_dataframe, s1_geo, pixel_size = process_inputs(cell_position_file_path, s1_geojson_path, pixel_file_path)
    dataframe = compute_densities(s1_geo, cells_dataframe, pixel_size, thickness_cut, nb_slices, visualisation_flag)
    save_results(dataframe, output_file_path)

@click.version_option(VERSION)
@click.command()
@click.option('--config-file-path', required=False, help='Configuration file path')
def batch(config_file_path):
    if config_file_path:
        config = configparser.ConfigParser()
        config.sections()
        config.read(config_file_path)
        cell_position_file_path = config['DEFAULT']['cell_position_file_path']
        s1_geojson_path = config['DEFAULT']['s1_geojson_path']
        pixel_file_path = config['DEFAULT']['pixel_file_path']
        thickness_cut = float(config['DEFAULT']['thickness_cut'])
        nb_slices = int(config['DEFAULT']['nb_slices'])
        output_file_path = config['DEFAULT']['output_file_path']

    cells_dataframe, s1_geo, pixel_size = process_inputs(cell_position_file_path, s1_geojson_path, pixel_file_path)
    dataframe = compute_densities(s1_geo, cells_dataframe, pixel_size, thickness_cut, nb_slices, False)
    save_results(dataframe, output_file_path)



@click.version_option(VERSION)
@click.command()
@click.option('--config-file-path', required=False, help='Configuration file path')
def layers(config_file_path):
    if config_file_path:
        config = configparser.ConfigParser()
        config.sections()
        config.read(config_file_path)
        cell_position_file_path = config['DEFAULT']['cell_position_file_path']
        layers_geojson_path = config['DEFAULT']['layers_geojson_path']
        pixel_file_path = config['DEFAULT']['pixel_file_path']
        thickness_cut = float(config['DEFAULT']['thickness_cut'])
        nb_slices = int(config['DEFAULT']['nb_slices'])
        output_file_path = config['DEFAULT']['output_file_path']

    cells_dataframe, s1_geo, pixel_size = process_layers_inputs(cell_position_file_path, layers_geojson_path, pixel_file_path)
    dataframe = compute_densities(s1_geo, cells_dataframe, pixel_size, thickness_cut, nb_slices, False)
    save_results(dataframe, output_file_path)

