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



    if pixel_file_path:
        with open(pixel_file_path, 'r') as f:
            read_pixel_size = float(f.readline())
        print("pixel size:", read_pixel_size)

    s1_geometry = geojson.load(open(s1_geojson_path,'rb'))
    return cells_dataframe, s1_geometry, read_pixel_size


def compute_densities(s1_geo, cells_dataframe, pixel_size, z_thicknes, nb_slices):
    """
    Compute cell density (cells / mm3)
    :param s1_geo:
    :param cells_dataframe:
    :param pixel_size(float): (um)
    :param z_thickness (float): thickness cut (mm)
    :param nb_slices (int):
    :return:
    """

    s1_coordinates = np.array(s1_geo["features"][0]["geometry"]["coordinates"][0]) * pixel_size
    s1_button=s1_coordinates[:,1].min()
    s1_top=s1_coordinates[:,1].max()
    print('S1 anotation button {}, top {}'.format(s1_button, s1_top))
    z_length = 50 / 10e3 # mm

    cells_centroid_x = cells_dataframe['Centroid X µm'].to_numpy(dtype=float)
    cells_centroid_y = cells_dataframe['Centroid Y µm'].to_numpy(dtype=float)


    s1_length = s1_top - s1_button
    '''
    fractions=np.zeros(cells_centroid_y.shape[0], dtype=float)
    for index, point in enumerate(cells_centroid_y):
        fractions[index]=(point-s1_button) / s1_length

    fig=plt.figure()
    ax3=fig.add_subplot(121, label="1")
    ax3.invert_yaxis()
    fract_hist = ax3.hist(fractions, nb_slices, orientation='horizontal')
    ax3.title.set_text("Number of cells by slices Histogram")

    nb_points_per_bin = fract_hist[0]
    '''
    slice_y_length = s1_length / nb_slices
    split_lines_y_coord = np.arange(s1_button + slice_y_length, s1_top, slice_y_length)

    s1_x_min = 0.#s1_coordinates[:,0].min()
    s1_x_max = 15000# s1_coordinates[:,0].max()
    split_lines = []
    for split_line_y_coord in split_lines_y_coord:
        split_lines.append(LineString([[s1_x_min-1, split_line_y_coord], [s1_x_max+1, split_line_y_coord]]))


    s1_polygon = Polygon(s1_coordinates)

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
    
    # Compute the number of points per slice
    nb_points_per_bin = np.zeros(len(split_polygons), dtype=int)
    for index, polygon in enumerate(split_polygons):
        nb_points_per_bin[index] = \
        np.where((cells_centroid_y >= polygon.bounds[1]) & (cells_centroid_y < polygon.bounds[3]))[0].shape[0]

    densities = nb_points_per_bin / (np.array(split_polygon_areas) * z_length)


    nb_cell = len(cells_dataframe)
    total_volume = s1_polygon.area / 1e6 * z_length
    print('Total density cell/mm3=', nb_cell / total_volume)

    start = s1_button + slice_y_length / 2
    step = slice_y_length
    slides_y_centroid = np.arange(start, s1_top, step)


    fig=plt.figure()
    ax=fig.add_subplot(111, label="1", frame_on=False)

    ax.axis('equal')
    _ = plt.scatter(cells_centroid_x, cells_centroid_y, s=.1, label='cells position')
    ax.tick_params(axis='x', colors="blue")
    ax.invert_yaxis()
    ax.set_ylabel("y (um)")
    ax.set_xlabel("x (um)")
    ax.grid(axis='x')
    ax.title.set_text("Cells coordinates in S1 and Densities per slice")

    #fig.grid(axis='y')
    x_min = s1_coordinates[:, 0].min()
    x_max = s1_coordinates[:, 0].max()
    '''
    for line in split_lines:
        ax.plot([x_min, x_max], [line.coords.xy[1][0], line.coords.xy[1][1]],  '--', color='yellow')
    ax.plot([x_min, x_max], [s1_coordinates[:,1].min(), s1_coordinates[:,1].min()], '--', color='yellow')
    ax.plot([x_min, x_max], [s1_coordinates[:,1].max(), s1_coordinates[:,1].max()], '--', color='yellow', label='slices border')

    '''
    for polygon in split_polygons:
        ax.plot(polygon.exterior.coords.xy[0], polygon.exterior.coords.xy[1], color='red')

    ax.legend()
    #plt.subplot(122)
    # Generate a new Axes instance, on the twin-X axes (same position)
    ax2 = ax.twiny()
    ax2.tick_params(axis='y', labelcolor='black')
    #ax2.invert_yaxis()
    ax2.plot(densities, slides_y_centroid, '--bo', color='black', label='cells desitites per slcies')

    ax2.set_ylabel("Slices y centroid (mm)")
    ax2.set_xlabel("Cell density (cells/mm3)")
    ax2.legend()
    plt.show()



if __name__ == '__main__':
    if len(sys.argv) != 6:
        print('Usage: rat_SSCX_Nissl_processing.py cell_position_file_path, s1_geojson_path, pixel_file_path, thickness_cut, nb_slices')
        sys.exit(1)
    cell_position_file_path = sys.argv[1]
    s1_geojson_path = sys.argv[2]
    pixel_file_path = sys.argv[3]
    thickness_cut = float(sys.argv[4])
    nb_slices = int(sys.argv[5])
    cells_dataframe, s1_geo, pixel_size = process_inputs(cell_position_file_path, s1_geojson_path, pixel_file_path)
    compute_densities(s1_geo, cells_dataframe, pixel_size, thickness_cut, nb_slices)


