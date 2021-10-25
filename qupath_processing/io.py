"""
Read / Write files modules
"""
from os import listdir
from os.path import isfile, join
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
    workbook = openpyxl.Workbook()
    worksheets = workbook.worksheets[0]

    with open(file_path, 'r', encoding="utf-8") as data:
        reader = csv.reader(data, delimiter='\t')
        for row in reader:
            worksheets.append(row)
    data = worksheets.values
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
            - s1_coordinates: np.array(float) of shape (nb_vertices, 2) containing S1 polygon
            coordinates
            - quadrilateral: np.array(float) o shape (5, 2): ClockWise coordinates defined by
            TOP_LEFT, TOP_RIGHT, BOTTOM_RIGHT, BOTTOM_LEFT and TOP_LEFT coordinates
    Notes: The returned coordinates unit is pixel. One needs to multiply coordinate values by the
     pixel size to obtain um as unit
    """
    with open(file_path, 'rb') as annotation_file:
        annotations_geo = geojson.load(annotation_file)
    annotations = {}
    for entry in annotations_geo:
        try:
            ## 'bottom_left', 'bottom_right', 'top_left', 'top_right' annotations
            if "name" in entry["properties"].keys():
                annotations[entry["properties"]["name"]] = \
                    np.array(entry["geometry"]["coordinates"])
            ## S1 annotation has a classification key b4 name
            if "classification" in entry["properties"].keys():
                if "name" in entry["properties"]["classification"].keys():
                    if entry["properties"]["classification"]["name"] != "SliceContour":
                        annotations[entry["properties"]["classification"]["name"]] = np.array(entry["geometry"]["coordinates"])
        except KeyError:  # annotation without name
            pass

    s1_pixel_coordinates = annotations['S1'][0]
    # These 4 points can not be find via an algo, so we need QuPath annotation
    quadrilateral_pixel_coordinates = np.array([annotations['top_left'], annotations['top_right'],
                                                annotations['bottom_right'],
                              annotations['bottom_left'], annotations['top_left']])

    return s1_pixel_coordinates, quadrilateral_pixel_coordinates


def read_pixel_size(pixel_file_path):
    """
    Read pixel size information in a file
    :param pixel_file_path:(str):
    :return:  float. Pixel size (um)
    """
    with open(pixel_file_path, 'r', encoding="utf-8") as pixel_file:
        readed_pixel_size = float(pixel_file.readline())
    return readed_pixel_size


def write_densities_csv(dataframe, output_file_path):
    """
    export and save result to xlsx file
    :param dataframe (pandas Dataframe):
    :param output_file_path(str):
    """
    dataframe.to_excel(output_file_path, header=True, index=False)


def list_images(input_directory, cell_position_suffix,
                annotations_geojson_suffix):
    """
    Create a list of images nme prefix from the content of the input_directory
    :param input_directory:input directory that contains export image information fromn QuPath
    :param cell_position_suffix:(str) The one defined in config.ini
    :param annotations_geojson_suffix:(str) The one defined in config.ini
    :return: dictionary: key image prefix, values dictionary of file relative
                    to image_prefix
    """
    onlyfiles = [file_name for file_name in listdir(input_directory) if
                 isfile(join(input_directory, file_name))]
    image_dictionary = {}
    for filename in onlyfiles:
        prefix_pos = filename.find('_cell_position.txt')
        if prefix_pos != -1:
            image_name = filename[:prefix_pos]
            if image_name + '_annotations.geojson' in onlyfiles:
                image_dictionary[image_name] = {}
                image_dictionary[image_name]['CELL_POSITIONS_PATH'] =\
                    input_directory + '/' + image_name + cell_position_suffix
                image_dictionary[image_name]['ANNOTATIONS_PATH'] = \
                    input_directory + '/' + image_name +\
                    annotations_geojson_suffix
            else:
                print(f"ERROR: {image_name + '_annotations.geojson'} "
                      f"does not exist for image {image_name}")

    return image_dictionary