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
from qupath_processing.utilities import NotValidImage


def to_dataframe(file_path):
    """
    Ream input file and return and panf=das data frame
    :param file_path: (str). Path to the fiule that containns cell cordinates
    :return: Pandas ddataframe containing data from input file_path
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
    dataframe = pd.DataFrame(data, index=idx, columns=cols)
    return dataframe



def read_cells_coordinate(dataframe):
    """
    Read file that contains cell positions and create cells centroids x,y position
    :param file_path:(str) Pandas ddataframe containing cells coordinate and metadata (layer, ...)
    :return:
        tuple:
            - cells_centroid_x np.array of shape (number of cells, ) of type float
            - cells_centroid_y np.array of shape (number of cells, ) of type float
    """

    try:
        cells_centroid_x = dataframe['Centroid X µm'].to_numpy(dtype=float)
        cells_centroid_y = dataframe['Centroid Y µm'].to_numpy(dtype=float)
        return cells_centroid_x, cells_centroid_y
    except KeyError:
        raise NotValidImage


def read_qupath_annotations(file_path):
    """
    Read file that contains quPath annotations
    :param file_path:
    :return:
        tuple:
            - s1_coordinates: np.array(float) of shape (nb_vertices, 2) containing S1HL polygon
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
            ## S1HL annotation has a classification key b4 name
            if "classification" in entry["properties"].keys():
                if "name" in entry["properties"]["classification"].keys():
                    if entry["properties"]["classification"]["name"] != "SliceContour" and\
                            entry["properties"]["classification"]["name"] != 'Other':
                        annotations[entry["properties"]["classification"]["name"]] = np.array(entry["geometry"]["coordinates"])
        except KeyError:  # annotation without name
            pass

    s1_pixel_coordinates = annotations['S1HL'][0]
    # These 4 points can not be find via an algo, so we need QuPath annotation
    quadrilateral_pixel_coordinates = np.array([annotations['top_left'], annotations['top_right'],
                                                annotations['bottom_right'],
                              annotations['bottom_left'], annotations['top_left']])

    return s1_pixel_coordinates, quadrilateral_pixel_coordinates




def write_dataframe_to_file(dataframe, image_name, output_path):
    """
    export and save result to xlsx file
    :param dataframe (pandas Dataframe):
    :param output_path(str):
    """
    dataframe.to_excel(output_path + '/' + image_name + '.xlsx', header=True, index=False)
    dataframe.to_pickle(output_path + '/' + image_name + '.pkl')



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
        prefix_pos = filename.find(cell_position_suffix)  # SLD_0000521.vsi - 20x_01 Detections.txt
        if prefix_pos != -1:
            image_name = filename[:prefix_pos]
            if image_name + annotations_geojson_suffix in onlyfiles:
                image_dictionary[image_name] = {}
                image_dictionary[image_name]['CELL_POSITIONS_PATH'] =\
                    input_directory + '/' + image_name + cell_position_suffix
                image_dictionary[image_name]['ANNOTATIONS_PATH'] = \
                    input_directory + '/' + image_name +\
                    annotations_geojson_suffix
            else:
                print(f"ERROR: {image_name + annotations_geojson_suffix} "
                      f"does not exist for image {image_name}")

    return image_dictionary



def get_top_line_coordinates(annotation_position_file_path):
    """
    Read TOP_LEFT and TOP_RIGHT point from file located at annotation_position_file_path
    :param annotation_position_file_path: (str)
    :return: np.array of shape (2,2) containing top left and right points
    """
    df_annotation = to_dataframe(annotation_position_file_path)
    position={}
    for point_str in ['TOP_LEFT', 'TOP_RIGHT', 'BOTTOM_RIGHT', 'BOTTOM_FEFT']:
        annotation = df_annotation[df_annotation["Name"] == point_str]
        position[point_str] = [annotation['Centroid X µm'].to_numpy(dtype=float),
                               annotation['Centroid Y µm'].to_numpy(dtype=float) ]
    top_left = position['TOP_LEFT']
    top_right = position['TOP_RIGHT']
    return np.array(top_left), np.array(top_right)


# Importing library


# data to be written row-wise in csv fil
data = [['Geeks'], [4], ['geeks !']]

# opening the csv file in 'w+' mode
file = open('g4g.csv', 'w+', newline='')

# writing the data into the file
with file:
    write = csv.writer(file)
    write.writerows(data)