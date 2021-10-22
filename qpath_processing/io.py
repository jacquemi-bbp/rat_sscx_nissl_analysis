"""
Read / Write files modules
"""

from itertools import islice
import csv
import numpy as np
import geojson
import pandas as pd
import openpyxl


def read_cells_coordinate(file_path):
    """
    Read file that contains cell positions and create cells centroids x,y position
    :param file_path:(str) Path to the file that contains cell positions exported form QuPath
    :return:
        tuple:
            - cells_centroid_x np.array of shape (number of cells, ) of type float
            - cells_centroid_y np.array of shape (number of cells, ) of type float
    """
    wb = openpyxl.Workbook()
    ws = wb.worksheets[0]

    with open(file_path, 'r') as data:
        reader = csv.reader(data, delimiter='\t')
        for row in reader:
            ws.append(row)
    data = ws.values
    cols = next(data)[1:]
    data = list(data)
    idx = [r[0] for r in data]
    data = (islice(r, 1, None) for r in data)
    df_404 = pd.DataFrame(data, index=idx, columns=cols)
    cells_centroid_x = df_404['Centroid X µm'].to_numpy(dtype=float)
    cells_centroid_y = df_404['Centroid Y µm'].to_numpy(dtype=float)
    return cells_centroid_x, cells_centroid_y


def read_qupath_annotations(file_path):
    """
    Read file that contains quPath annotations
    :param file_path:
    :return:
        tuple:
            - s1_coordinates: np.array(float) of shape (nb_vertices, 2) containing S1 polygon coordinates
            - quadrilateral: np.array(float) o shape (5, 2): ClockWise coordinates defined by TOP_LEFT, TOP_RIGHT,
                                                            BOTTOM_RIGHT, BOTTOM_LEFT and TOP_LEFT coordinates
    Notes: The returned coordinates unit is pixel. One needs to multiply coordinate values by the pixel size to
                                                    obtain um as unit
    """
    annotations_geo = geojson.load(open(file_path, 'rb'))

    annotations = dict()
    for entry in annotations_geo:
        try:
            if "name" in entry["properties"].keys():
                annotations[entry["properties"]["name"]] = np.array(entry["geometry"]["coordinates"])
        except KeyError:  # annotation without name
            pass

    s1_pixel_coordinates = annotations['S1'][0]
    # These 4 points can not be find via an algo, so we need QuPath annotation
    quadrilateral_pixel_coordinates = np.array([annotations['TOP_LEFT'], annotations['TOP_RIGHT'],  annotations['BOTTOM_RIGHT'],
                              annotations['BOTTOM_LEFT'], annotations['TOP_LEFT']])

    return s1_pixel_coordinates, quadrilateral_pixel_coordinates


def read_pixel_size(pixel_file_path):
    """
    Read pixel size information in a file
    :param pixel_file_path:(str):
    :return:  float. Pixel size (um)
    """
    with open(pixel_file_path, 'r') as f:
        readed_pixel_size = float(f.readline())
    return readed_pixel_size


def write_densities_csv(dataframe, output_file_path):
    """
    export and save result to xlsx file
    :param dataframe (pandas Dataframe):
    :param output_file_path(str):
    """
    dataframe.to_excel(output_file_path, header=True, index=False)