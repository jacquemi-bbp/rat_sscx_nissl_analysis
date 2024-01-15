import configparser
import click

from qupath_processing.io import (
    write_dataframe_to_file,
    list_images,
    get_qpproject_images_metadata,
    save_dataframe_without_space_in_path,
)

from qupath_processing.convert import (
    convert,
)
from qupath_processing.utilities import (
    get_image_lateral,
    get_image_animal,
    get_image_immunohistochemistry,
)

from qupath_processing.convert import single_image_conversion

@click.command()
@click.option("--config-file-path", required=False, help="Configuration file path")
def cmd(config_file_path):

    config = configparser.ConfigParser()
    config.sections()
    config.read(config_file_path)

    input_detection_directory = config["BATCH"]["input_detection_directory"]
    try:
        input_annotation_directory = config["BATCH"]["input_annotation_directory"]
        annotations_geojson_suffix = config["BATCH"]["annotations_geojson_suffix"]
    except KeyError:
        input_annotation_directory = None
        annotations_geojson_suffix = None

    exclude_flag = config.getboolean('BATCH', 'exclude')


    cell_position_suffix = config["BATCH"]["cell_position_suffix"].replace('"', "")
    pixel_size = float(config["BATCH"]["pixel_size"])
    try:
        qupath_project_path = config["BATCH"]["qpproj_path"]
    except KeyError:
        qupath_project_path = None
    output_path = config["BATCH"]["output_directory"]

    images_dictionary = list_images(
        input_detection_directory, cell_position_suffix, annotations_geojson_suffix, input_annotation_directory
    )

    for image_prefix, values in images_dictionary.items():
        print("INFO: Process single image {}".format(image_prefix))
        single_image_conversion(output_path, qupath_project_path, image_prefix,
                                input_detection_directory, input_annotation_directory,
                                pixel_size, exclude = exclude_flag)