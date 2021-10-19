#!/usr/bin/env python

import sys

import numpy as np
import pandas as pd
import csv
import openpyxl
from itertools import islice

import matplotlib.pyplot as plt

import geojson

from shapely.ops import split
from shapely.geometry import Point, LineString, Polygon


# # Compute density (cell / mm3 )

# ## Convert QuPath Cell detection data to pandas
# #### 404_cell_position.txt are created thanks to QuPath script: export-annotation_geojson.groovy

def process_cell_pos(cell_position_file_path):
    """

    :param cell_position_file_path:(str): path to cells position file
    :return:  Pandas dataframe with cells information
    """

    wb = openpyxl.Workbook()
    ws = wb.worksheets[0]

    with open(cell_position_file_path, 'r') as data:
        reader = csv.reader(data, delimiter='\t')
        for row in reader:
            ws.append(row)

    data = ws.values
    cols = next(data)[1:]
    data = list(data)
    idx = [r[0] for r in data]
    data = (islice(r, 1, None) for r in data)
    cells_dataframe = pd.DataFrame(data, index=idx, columns=cols)
    return cells_dataframe


def process_pixel_size(pixel_file_path):
    """
    :param pixel_file_path:(str):
    :return:  float. Pixel size (um)
    """
    with open(pixel_file_path, 'r') as f:
        read_pixel_size = float(f.readline())
    print("pixel size:", read_pixel_size)
    return read_pixel_size


def process_layers_inputs(cell_position_file_path, layers_geojson_path, pixel_file_path):
    """
    Process inputs file to produce cells position, s1 Polygon and get pixel size
    :param cell_position_file_path:(str): path to cells position file
    :param layers_geojson_path:(str): path to layer annotations geojson file
    :param pixel_file_path:(str): path to pixel size information file
    :return:
    tuple of:

        pixel_size (float): File containing one float value (um)
        list of layers annotation geometry (geojson)


    """
    cells_dataframe = process_cell_pos(cell_position_file_path)
    read_pixel_size = process_pixel_size(pixel_file_path)

    layers_geojson = geojson.load(open(layers_geojson_path,'rb'))

    layers_geometries = {}
    for entry in layers_geojson:
        name = (entry["properties"]["classification"]["name"])
        layers_geometries[name] = np.array(entry["geometry"]["coordinates"][0])

    return cells_dataframe, layers_geometries, read_pixel_size



def process_inputs(cell_position_file_path, s1_geojson_path, pixel_file_path):
    """
    Process inputs file to produce cells position, s1 Polygon and get pixel size
    :param cell_position_file_path(str): path to cells position file
    :param s1_geojson_path(str): path to s1_geojson file
    :param pixel_file_path(str): path to pixel size information file
    :return:
    tuple of:
        Pandas dataframe with cells information
        pixel_size (float): File containing one float value (um)
        S1 annotation geometry (geojson)


    """
    cells_dataframe = process_cell_pos(cell_position_file_path)
    read_pixel_size = process_pixel_size(pixel_file_path)
    s1_geometry = geojson.load(open(s1_geojson_path,'rb'))

    return cells_dataframe, s1_geometry, read_pixel_size


def plot_densities(densities, slides_y_centroid, cells_centroid_x, cells_centroid_y, splitted_polygons):
    """
    Plot denstities VS slide y centroid, cells and splitted polygon
    :param densities(np.array): shape (nb_cells, )
    :param slides_y_centroid(np.array): shape (nb_cells, )
    :param cells_centroid_x(np.array): shape (nb_cells, )
    :param cells_centroid_y(np.array): shape (nb_cells, )
    :param splitted_polygons(lilst): list of Polygons
    """
    fig = plt.figure()
    ax = fig.add_subplot(111, label="1", frame_on=False)
    ax.axis('equal')
    _ = plt.scatter(cells_centroid_x, cells_centroid_y, s=.5, label='cells position')
    ax.tick_params(axis='x', colors="blue")
    ax.invert_yaxis()
    ax.set_ylabel("y (um)")
    ax.set_xlabel("x (um)")
    ax.title.set_text("Cells coordinates in S1 and Densities per slice")
    for polygon in splitted_polygons:
        ax.plot(polygon.exterior.coords.xy[0], polygon.exterior.coords.xy[1], color='red', linewidth=.3)
    ax.legend()
    # plt.subplot(122)
    # Generate a new Axes instance, on the twin-X axes (same position)
    ax2 = ax.twiny()
    ax2.tick_params(axis='y', labelcolor='black')
    # ax2.invert_yaxis()
    ax2.plot(densities, slides_y_centroid, '--bx', color='black', label='cells desitites per slices', markersize=5.,
             linewidth=1.)
    ax2.grid(axis='x')
    ax2.set_ylabel("Slices y centroid (mm)")
    ax2.set_xlabel("Cell density (cells/mm3)")
    ax2.legend()
    plt.show()


def split_polygons(s1_polygon, slice_y_length, s1_coordinates):
    """
    pqram: s1_polygon
    parma: slice_y_length
    param: s1_coordinates
    :return:
    """
    # Create lines that will be used to split S1 polygon
    s1_button=s1_coordinates[:,1].min()
    s1_top=s1_coordinates[:,1].max()
    split_lines_y_coord = np.arange(s1_button + slice_y_length, s1_top, slice_y_length)
    s1_x_min = s1_coordinates[:,0].min() - 1
    s1_x_max = s1_coordinates[:,0].max() + 1
    split_lines = []
    for split_line_y_coord in split_lines_y_coord:
        split_lines.append(LineString([[s1_x_min-1, split_line_y_coord], [s1_x_max+1, split_line_y_coord]]))
    # Split s1 polygon
    split_polygons = []
    polygon_to_split = s1_polygon
    for line in split_lines:
        split_result = split(polygon_to_split, line)
        split_polygons.append(split_result[0])
        polygon_to_split = split_result[1]
    split_polygons.append(polygon_to_split)
    split_polygon_areas = [(polygon.area / 1e6) for polygon in split_polygons]
    total_area = sum(split_polygon_areas)
    print('Recomputed area {:.2f} %'.format((total_area / (s1_polygon.area / 1e6)) * 100))
    return split_polygons, split_polygon_areas


def compute_layers_densities(layers_geometries, cells_dataframe, pixel_size, thickness_cut, visualistation_flag):
    """
    Compute cell density (cells / mm3) by layers
    :param layers_geometries: (dict) key: layer name, values numpy array of shape (nb_points, 2) of layers geometry
    :param cells_dataframe:
    :param pixel_size(float): (um)
    :param thickness_cut(float): thickness cut (um)
    :param nb_slices (int):
    :param visualistation_flag(bool)
    :return:
    """
    # Compute geometries
    layers_name = []
    densities = []
    nb_cells_per_layer = []
    volumes = []
    for name, coordinates in layers_geometries.items():
        if name == 'SliceContour' or name == 'S1' or name == 'OutsidePia' or name == 'WM (white matter)':
            continue
        layers_name.append(name)
        cells_centroid_y = cells_dataframe['Centroid Y µm'].to_numpy(dtype=float)
        #slice_y_length = s1_length / nb_slices
        print('--------> Name:', name)
        print('coordinate shape:', coordinates.shape)
        polygon = Polygon(coordinates)

        # Compute the number of cells for the current layers
        '''
        nb_cells_per_bin = np.zeros(len(splitted_polygons), dtype=int)
        for index, polygon in enumerate(splitted_polygons):
            nb_cells_per_bin[index] = \
                np.where((cells_centroid_y >= polygon.bounds[1]) & (cells_centroid_y < polygon.bounds[3]))[0].shape[0]
        '''
        nb_cells = np.where((cells_centroid_y >= polygon.bounds[1]) & (cells_centroid_y < polygon.bounds[3]))[0].shape[0]
        nb_cells_per_layer.append(nb_cells)
        print('nb_cells:', nb_cells)
        print('volume: ', np.array(polygon.area) * (thickness_cut / 1e3))
        # Compute densities per slice # nb_cells / mm3
        volume = (np.array(polygon.area) * (thickness_cut / 1e3))
        volumes.append(volume)
        density = nb_cells / volume
        print('Density for layer {} = {} cell/mm3='.format(name,  density))
        densities.append(density)


    final_df = pd.DataFrame({'layers': layers_name, 'nb_cells_per_layer' : nb_cells_per_layer,
                             'volumes': volume, 'densities': densities})
    return final_df


def compute_densities(s1_geo, cells_dataframe, pixel_size, thickness_cut, nb_slices, visualistation_flag):
    """
    Compute cell density (cells / mm3) by slice
    :param s1_geo:
    :param cells_dataframe:
    :param pixel_size(float): (um)
    :param thickness_cut(float): thickness cut (um)
    :param nb_slices (int):
    :param visualistation_flag(bool)
    :return:
    """
    # Compute s1 geometry
    s1_coordinates = np.array(s1_geo["features"][0]["geometry"]["coordinates"][0]) * pixel_size
    s1_button=s1_coordinates[:,1].min()
    s1_top=s1_coordinates[:,1].max()
    s1_length = s1_top - s1_button
    cells_centroid_x = cells_dataframe['Centroid X µm'].to_numpy(dtype=float)
    cells_centroid_y = cells_dataframe['Centroid Y µm'].to_numpy(dtype=float)
    slice_y_length = s1_length / nb_slices
    s1_polygon = Polygon(s1_coordinates)
    splitted_polygons, split_polygon_areas = split_polygons(s1_polygon, slice_y_length, s1_coordinates)
    
    # Compute the number of cells per slice
    nb_cells_per_bin = np.zeros(len(splitted_polygons), dtype=int)
    for index, polygon in enumerate(splitted_polygons):
        nb_cells_per_bin[index] = \
        np.where((cells_centroid_y >= polygon.bounds[1]) & (cells_centroid_y < polygon.bounds[3]))[0].shape[0]

    # Compute densities per slice # nb_cells / mm3
    densities = nb_cells_per_bin / (np.array(split_polygon_areas) * (thickness_cut/1e3))

    # Compute average density
    nb_cell = len(cells_dataframe)
    total_volume = s1_polygon.area / 1e6 * (thickness_cut/1e3)
    print('Average density cell/mm3=', nb_cell / total_volume)

    # Get y coordinate at slice center
    start = s1_button + slice_y_length / 2
    step = slice_y_length
    slides_y_centroid = np.arange(start, s1_top, step)

    if visualistation_flag:
        plot_densities(densities, slides_y_centroid, cells_centroid_x, cells_centroid_y, splitted_polygons)

    final_df = pd.DataFrame({'layers_y_centroid': slides_y_centroid, 'densities': densities})
    return final_df


def save_results(dataframe, output_file_path):
    """
    export and save result to xlsx file
    :param dataframe (pandas Dataframe):
    :param output_file_path(str):
    """
    #dataframe.to_excel(output_file_path, sheet_name=sheet_name, header=True, index=False)
    dataframe.to_excel(output_file_path, header=True, index=False)

