"""
Produces astrocyte morphology in HDF5 format from 3D meshes
"""
import configparser
import click
import pandas as pd
from qpath_processing.rat_SSCX_Nissl_processing import (
    compute_cell_density)
from qpath_processing.io import (
    write_densities_csv, read_qupath_annotations, read_cells_coordinate, read_pixel_size)
from qpath_processing.geometry import (
    create_depth_polygons, create_grid, count_nb_cell_per_polygon
)
from qpath_processing.visualisation import plot_densities, plot_split_polygons_and_cell_depth
from qpath_processing.version import VERSION

@click.version_option(VERSION)
@click.command()
@click.option('--config-file-path', required=False, help='Configuration file path')
@click.option('--cell-position-file_path', help='Cells position file path.', required=False)
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

    print('INFO: Read input files')
    cells_centroid_x, cells_centroid_y = read_cells_coordinate(cell_position_file_path)
    pixel_size = read_pixel_size(pixel_file_path)
    s1_pixel_coordinates, quadrilateral_pixel_coordinates =  read_qupath_annotations(annotations_geojson_path)
    s1_coordinates = s1_pixel_coordinates * pixel_size
    quadrilateral_coordinates = quadrilateral_pixel_coordinates * pixel_size

    print('INFO: Create S1 grid as function of brain depth')
    _, horizontal_lines = create_grid(quadrilateral_coordinates, s1_coordinates, nb_row, nb_col)
    split_polygons = create_depth_polygons(s1_coordinates, horizontal_lines)

    print('INFO: Computes the cells densities as function of percentage depth')
    nb_cell_per_slide = count_nb_cell_per_polygon(cells_centroid_x, cells_centroid_y, split_polygons)
    depth_percentage, densities = compute_cell_density(nb_cell_per_slide, split_polygons, thickness_cut/1e3)
    densities_dataframe = pd.DataFrame({'depth_percentage': depth_percentage, 'densities': densities})

    print('INFO: Write results')
    write_densities_csv(densities_dataframe, output_file_path)

    if visualisation_flag:
        plot_split_polygons_and_cell_depth(split_polygons, s1_coordinates, cells_centroid_x, cells_centroid_y)
        plot_densities(depth_percentage, densities)


'''
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

'''