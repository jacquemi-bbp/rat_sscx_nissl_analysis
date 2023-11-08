"""
Read / Write files modules
"""
from os import listdir, makedirs
from os.path import isfile, join, isdir
import numpy as np
import geojson
import pandas as pd
import openpyxl
from qupath_processing.utilities import NotValidImage



def convert_files_to_dataframe(
    cell_position_file_path,
    annotations_geojson_path,
    pixel_size

):
    print(
        f"INFO: Read input files {cell_position_file_path} and {annotations_geojson_path}"
    )
    # try:
    detection_dataframe = qupath_cells_detection_to_dataframe(cell_position_file_path)
    (
        s1_pixel_coordinates,
        quadrilateral_pixel_coordinates,
        out_of_pia,
    ) = read_qupath_annotations(annotations_geojson_path)

    print("INFO: Convert coodonates from pixel to mm")
    s1_coordinates = s1_pixel_coordinates * pixel_size
    quadrilateral_coordinates = quadrilateral_pixel_coordinates * pixel_size
    print("INFO: Create S1 grid as function of brain depth")

    return detection_dataframe, s1_coordinates, quadrilateral_coordinates


def qupath_cells_detection_to_dataframe(file_path):
    """
    Ream input file that contains QuPah cells detection and return and pandas data frame
    :param file_path: (str). Path to the file that contains cells coordinates
    :return: Pandas dataframe containing data from input file_path
    """
    if file_path.find('pkl') > 0:
        return pd.read_pickle(file_path)
    else:
        return pd.read_csv(file_path, sep="	|\t", engine="python")


def get_cells_coordinate(dataframe, exclude=False):
    """
    Read file that contains cell positions and create cells centroids x,y position
    :param dataframe:(Pandas dataframe) containing cells coordinate and metadata (layer, ...)
    :excluded :(bool) return exluded cells position if set otherwise none excluded cell.
    :return:
        tuple:
            - cells_centroid_x np.array of shape (number of cells, ) of type float
            - cells_centroid_y np.array of shape (number of cells, ) of type float
    """
    if exclude:
        dataframe=dataframe[dataframe['exclude'] == True]
    try:
        cells_centroid_x = dataframe["Centroid X µm"].to_numpy(dtype=float)
        cells_centroid_y = dataframe["Centroid Y µm"].to_numpy(dtype=float)
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
            - quadrilateral: np.array(float) o shape (4, 2): ClockWise coordinates defined by
            top_left, top_right, bottom_right, bottom_left coordinates
    Notes: The returned coordinates unit is pixel. One needs to multiply coordinate values by the
     pixel size to obtain um as unit
    """
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
                        print(f'INFO: Get {entry["properties"]["classification"]["name"]} entry ')
                        annotations[
                            entry["properties"]["classification"]["name"]
                        ] = np.array(entry["geometry"]["coordinates"])
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


def write_dataframe_to_file(dataframe, image_name, output_path, exel_write=True):
    """
    export and save result to xlsx file
    :param dataframe (pandas Dataframe):
    :param output_path(str):
    """
    if exel_write:
        dataframe.to_excel(
            output_path + "/" + image_name + ".xlsx", header=True, index=False
        )
    dataframe.to_pickle(output_path + "/" + image_name + ".pkl")


def list_images(input_directory, cell_position_suffix, annotations_geojson_suffix):
    """
    Create a list of images name prefix from the content of the input_directory
    :param input_directory:input directory that contains export image information from QuPath
    :param cell_position_suffix:(str) The one defined in config.ini
    :param annotations_geojson_suffix:(str) The one defined in config.ini
    :return: dictionary: key image prefix, values dictionary of file relative
                    to image_prefix
    """
    onlyfiles = [
        file_name
        for file_name in listdir(input_directory)
        if isfile(join(input_directory, file_name))
    ]
    image_dictionary = {}
    detection_files = [file for file in onlyfiles if file.count("Detections") == 1]
    for filename in detection_files:
        prefix_pos = (
            filename.find(cell_position_suffix) - 1
        )  # SLD_0000521.vsi - 20x_01 Detections.txt
        if prefix_pos != -1:
            image_name = filename[:prefix_pos]
            #image_dictionary[image_name]["IMAGE_NAME"] = image_name
            annotation_image_path = (
                input_directory + "/" + image_name + annotations_geojson_suffix
            )
            if image_name + annotations_geojson_suffix in onlyfiles:
                image_dictionary[image_name] = {}
                image_dictionary[image_name]["CELL_POSITIONS_PATH"] = (
                    input_directory + "/" + image_name + " " + cell_position_suffix
                )
                image_dictionary[image_name]["ANNOTATIONS_PATH"] = annotation_image_path
            else:
                print(
                    f"ERROR: {image_name + annotations_geojson_suffix} "
                    f"does not exist for image {image_name}"
                )

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
