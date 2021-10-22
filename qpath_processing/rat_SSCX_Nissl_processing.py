import pandas as pd
from qpath_processing.io import (
    read_qupath_annotations, read_cells_coordinate,
    )
from qpath_processing.geometry import (
    create_depth_polygons, create_grid, count_nb_cell_per_polygon
)

from qpath_processing.visualisation import plot_densities, plot_split_polygons_and_cell_depth
"""
Module that computes density as function of brain percentage of depth
"""
def single_image_process(cell_position_file_path, annotations_geojson_path, pixel_size, thickness_cut,
                         nb_row, nb_col, visualisation_flag = False):
    """

    :param cell_position_file_path:
    :param annotations_geojson_path:
    :param pixel_size:
    :param thickness_cut:
    :param nb_row:
    :param nb_col:
    :return: densities_dataframe(pandas dataframe)
    """

    print('INFO: Read input files')
    cells_centroid_x, cells_centroid_y = read_cells_coordinate(cell_position_file_path)

    s1_pixel_coordinates, quadrilateral_pixel_coordinates = read_qupath_annotations(annotations_geojson_path)
    s1_coordinates = s1_pixel_coordinates * pixel_size
    quadrilateral_coordinates = quadrilateral_pixel_coordinates * pixel_size

    print('INFO: Create S1 grid as function of brain depth')
    _, horizontal_lines = create_grid(quadrilateral_coordinates, s1_coordinates, nb_row, nb_col)
    split_polygons = create_depth_polygons(s1_coordinates, horizontal_lines)

    print('INFO: Computes the cells densities as function of percentage depth')
    nb_cell_per_slide = count_nb_cell_per_polygon(cells_centroid_x, cells_centroid_y, split_polygons)
    depth_percentage, densities = compute_cell_density(nb_cell_per_slide, split_polygons, thickness_cut / 1e3)
    densities_dataframe = pd.DataFrame({'depth_percentage': depth_percentage, 'densities': densities})

    if visualisation_flag:
        if visualisation_flag:
            plot_split_polygons_and_cell_depth(split_polygons, s1_coordinates, cells_centroid_x, cells_centroid_y)
            plot_densities(depth_percentage, densities)
    return densities_dataframe


def compute_cell_density(nb_cell_per_slide, split_polygons, z_length):
    """
    Computes density as function of brain percentage of depth
    :param nb_cell_per_slide: list of int
    :param split_polygons: list of shapely polygons representing S1 layers as function if brain depth
    :param z_length: float ( thickness of the cut over z axis (mm)
    :return: tuple:
        -  depth_percentage: list of float representing the percentage of brain depth
        -  densities: list of float representing the number of cell by mm3
    #Pandas dataframe representing the density as function of brain percentage of depth (nb cells / mm3)
    """
    densities = []
    areas = []
    for nb_cell, polygon in zip(nb_cell_per_slide, split_polygons):
        areas.append(polygon.area)
        densities.append(nb_cell/ ((polygon.area / 1e6) * z_length))

    depth_percentage = [i/len(split_polygons) for i in range(len(split_polygons))]
    return depth_percentage, densities
