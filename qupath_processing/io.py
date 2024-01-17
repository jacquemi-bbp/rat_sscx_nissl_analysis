"""
Read / Write files modules
"""
from os import listdir, makedirs
from os.path import isfile, join
import glob
import numpy as np
import geojson
import pandas as pd
import openpyxl
from qupath_processing.utilities import NotValidImage
from collections import defaultdict



def get_cells_coordinate(dataframe):
    """
    Read file that contains cell positions and create cells centroids x,y position
    :param dataframe:(Pandas dataframe) containing cells coordinate and metadata (layer, ...)
    :excluded :(bool) return exluded cells position if set otherwise none excluded cell.
    :return:
        tuple:
            - cells_centroid_x np.array of shape (number of cells, ) of type float
            - cells_centroid_y np.array of shape (number of cells, ) of type float
    """

    valid_cells_dataframe = dataframe[dataframe['exclude_for_density']==False]
    cells_centroid_x = valid_cells_dataframe["Centroid X µm"].to_numpy(dtype=float)
    cells_centroid_y = valid_cells_dataframe["Centroid Y µm"].to_numpy(dtype=float)

    exluded_cells_dataframe = dataframe[dataframe['exclude_for_density'] == True]
    excluded_cells_centroid_x = exluded_cells_dataframe["Centroid X µm"].to_numpy(dtype=float)
    excluded_cells_centroid_y = exluded_cells_dataframe["Centroid Y µm"].to_numpy(dtype=float)
    return cells_centroid_x, cells_centroid_y, excluded_cells_centroid_x, excluded_cells_centroid_y



def read_qupath_annotations(directory_path, image_name):
    """
    Read file that contains quPath annotations
    :param directory_path:
    :param image_name:
    :return:
        tuple:
            - s1_coordinates: np.array(float) of shape (nb_vertices, 2) containing S1HL polygon
            coordinates
            - quadrilateral: np.array(float) o shape (4, 2): ClockWise coordinates defined by
            top_left, top_right, bottom_right, bottom_left coordinates
    Notes: The returned coordinates unit is pixel. One needs to multiply coordinate values by the
     pixel size to obtain um as unit
    """
    file_path = directory_path + '/' + image_name + '_annotations.json'
    with open(file_path, "rb") as annotation_file:
        annotations_geo = geojson.load(annotation_file)
    annotations = {}
    for entry in annotations_geo:
        try:
            if "name" in entry["properties"].keys():
                annotations[entry["properties"]["name"]] = np.array(
                    entry["geometry"]["coordinates"]
                )
            # S1HL annotation has a classification key b4 name
            if "classification" in entry["properties"].keys():
                if "name" in entry["properties"]["classification"].keys():
                    if (
                        entry["properties"]["classification"]["name"] != "SliceContour"
                        and entry["properties"]["classification"]["name"] != "Other"
                        and entry["properties"]["classification"]["name"].find("Layer")
                        == -1
                    ):
                        try:
                            key = entry["properties"]["classification"]["name"]
                            value = entry["geometry"]["coordinates"]
                            annotations[key] = np.array(value)
                        except ValueError:
                            '''
                            Because of miss created annotation by user, some QuPath annotation type 
                            are not simple polygon, but ROI (composition of several polygons.
                            In this case, we get the bigger polygon and do noy used the other

                                ---
                                | | 
                            -------
                            |   |
                            |   |
                            -----

                            '''
                            value = np.array(value, dtype="object")
                            value = np.vstack(value.flatten())
                            value = value.astype(np.float64)
                            shape = value.shape
                            if shape[0] != 1:
                                value = value.reshape([1, shape[0], shape[1]])
                            annotations[key] = value
        except KeyError:  # annotation without name
            pass

    try:
        s1_pixel_coordinates = annotations["S1HL"][0]
    except KeyError:
        s1_pixel_coordinates = annotations["S1"][0]
    if (
        isinstance(s1_pixel_coordinates, np.ndarray)
        and s1_pixel_coordinates.shape[0] == 1
    ):
        s1_pixel_coordinates = np.array(s1_pixel_coordinates[0])
    out_of_pia = annotations["Outside Pia"][0]
    if isinstance(out_of_pia, np.ndarray) and out_of_pia.shape[0] == 1:
        out_of_pia = np.array(out_of_pia[0])

    # These 4 points can not be find via an algo, so we need QuPath annotation
    # These 4 points can not be find via an algo, so we need QuPath annotation
    try:
        quadrilateral_pixel_coordinates = np.array(
            [
                annotations["top_left"],
                annotations["top_right"],
                annotations["bottom_right"],
                annotations["bottom_left"],
            ]
        )
    except KeyError as e:
        """
        print(f'! ERROR: {e}')
        value = input("Could we consider that bottom_left and bottom_right are superposed ? Y/n:\n").lower()
        while value != 'y' and value != 'n' and len(value) > 0:
            value = input("Could we consider that bottom_left and bottom_right are superposed ? Y/n:\n")
        """
        value = "y"

        if value == "y" or len(value) == 0:
            try:
                quadrilateral_pixel_coordinates = np.array(
                    [
                        annotations["top_left"],
                        annotations["top_right"],
                        annotations["bottom_right"],
                        annotations["bottom_right"],
                    ]
                )
            except KeyError:
                quadrilateral_pixel_coordinates = np.array(
                    [
                        annotations["top_left"],
                        annotations["top_right"],
                        annotations["bottom_left"],
                        annotations["bottom_left"],
                    ]
                )
        else:
            raise e
    return s1_pixel_coordinates, quadrilateral_pixel_coordinates, out_of_pia


def get_qpproject_images_metadata(file_path):
    """
    Read file that contains quPath annotations
        :param file_path: Path to QuPath project qpproj file
        :return: dictionnary. Keys -> images name. Valuesdict of image Metadata
    """
    with open(file_path, "rb") as annotation_file:
        annotations_geo = geojson.load(annotation_file)
    return annotations_geo["images"]


def write_dataframe_to_file(dataframe, image_path):
    """
    export and save result to xlsx file
    :param dataframe (pandas Dataframe):
    :param output_path(str):
    """
    if image_path.find('.txt'):
        image_path = image_path.replace('.txt', '.csv')
    dataframe.to_csv(image_path)


def list_images(cell_features_path=None, cell_features_suffix=None, 
                annotation_path=None, annotations_geojson_suffix=None):
    """
    Generate of dictionary of directory that contains the cell_feature and annotation pathes for each images

    :param cell_features_path: input directory that contains export cells features from QuPath
    :param cell_features_suffix:(str) cell features files suffix
    :param annotation_path:(str) input directory that contains export annotations information from QuPath
    :param annotations_geojson_suffix:(str) annotation files suffix
    :return: dictionary of dictionary: key image prefix -> dictionary of files CELL_POSITIONS_PATH and ANNOTATIONS_PATH
    """
    
    cells_file_list= []
    if cell_features_path:
        cells_file_list = glob.glob(cell_features_path + '/*' + cell_features_suffix)

    annotation_file_list=[]
    if annotation_path:
        annotation_file_list = glob.glob(annotation_path + '/*' + annotations_geojson_suffix)
 




    image_dictionary = defaultdict(dict)

    for cell_feature_filename in cells_file_list:
        prefix_pos = (
            cell_feature_filename.find(cell_features_suffix) - 1
        )
        if prefix_pos != -1:
            slash_pos = cell_feature_filename.rfind('/')
            image_name = cell_feature_filename[slash_pos+1:prefix_pos]
            image_dictionary[image_name]["CELL_POSITIONS_PATH"] = cell_feature_filename


    for annotation_filename in annotation_file_list:
        print(f'annotation_filename {annotation_filename}')
        prefix_pos = (
                annotation_filename.find(annotations_geojson_suffix) - 1
            )
        print(f'prefix_pos {prefix_pos}')
        if prefix_pos != -1:
            slash_pos = annotation_filename.rfind('/')
            image_name = annotation_filename[slash_pos+1:prefix_pos+1]
            print(f'image_name {image_name}')
            image_dictionary[image_name]["ANNOTATIONS_PATH"] = annotation_filename

    return image_dictionary


def get_top_line_coordinates(annotation_position_file_path):
    """
    Read TOP_LEFT and TOP_RIGHT point from file located at annotation_position_file_path
    :param annotation_position_file_path: (str)
    :return: np.array of shape (2,2) containing top left and right points
    """
    df_annotation = qupath_cells_detection_to_dataframe(annotation_position_file_path)
    position = {}
    for point_str in ["TOP_LEFT", "TOP_RIGHT", "BOTTOM_RIGHT", "BOTTOM_FEFT"]:
        annotation = df_annotation[df_annotation["Name"] == point_str]
        position[point_str] = [
            annotation["Centroid X µm"].to_numpy(dtype=float),
            annotation["Centroid Y µm"].to_numpy(dtype=float),
        ]
    top_left = position["TOP_LEFT"]
    top_right = position["TOP_RIGHT"]
    return np.array(top_left), np.array(top_right)


def create_directory_if_not_exist(directory_path):
    """
    Check if directory exists, if not, create it
    :param directory_path
    """
    check_folder = isdir(directory_path)
    # If folder doesn't exist, then create it.
    if not check_folder:
        makedirs(directory_path)
        print("created folder : ", directory_path)


def save_dataframe_without_space_in_path(dataframe, path):
    path = path.replace(" ", "")
    dataframe.to_csv(path)


