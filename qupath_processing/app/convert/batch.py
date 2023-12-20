import numpy as np
import pandas as pd
import configparser
import click

from qupath_processing.io import (
    write_dataframe_to_file,
    list_images,
    get_qpproject_images_metadata,
)

from qupath_processing.convert import (
    convert,
)
from qupath_processing.utilities import (
    get_image_lateral,
    get_image_animal,
    get_image_immunohistochemistry,
)


@click.command()
@click.option("--config-file-path", required=False, help="Configuration file path")
def cmd(config_file_path):
    config = configparser.ConfigParser()
    config.sections()
    config.read(config_file_path)

    input_directory = config["BATCH"]["input_directory"]
    cell_position_suffix = config["BATCH"]["cell_position_suffix"].replace('"', "")
    pixel_size = float(config["BATCH"]["pixel_size"])
    qpproj_path = config["BATCH"]["qpproj_path"]
    output_directory = config["BATCH"]["output_directory"]
    annotations_geojson_suffix = config["BATCH"]["annotations_geojson_suffix"]

    images_metadata = get_qpproject_images_metadata(qpproj_path)
    images_lateral = get_image_lateral(images_metadata)
    print(f'DEBUG images_lateral{images_lateral}')
    images_immunohistochemistry = get_image_immunohistochemistry(images_metadata)
    images_animal = get_image_animal(images_metadata)

    images_dictionary = list_images(
        input_directory, cell_position_suffix, annotations_geojson_suffix
    )
    print(f"INFO: input files: {list(images_dictionary.keys())}")
    if len(images_dictionary) == 0:
        print("WARNING: No input files to proccess.")
        return

    image_name_list = []
    image_lateral_list = []
    image_animal_list = []
    image_immunohistochemistry_list = []

    for image_prefix, values in images_dictionary.items():
        print("INFO: Process single image {}".format(image_prefix))
        cells_detection_path = values["CELL_POSITIONS_PATH"]
        annotation_path = values["ANNOTATIONS_PATH"]
        image_name = image_prefix # values["IMAGE_NAME"]
        image_name_list.append(image_name)
        image_lateral_list.append(images_lateral[image_name])
        image_animal_list.append(images_animal[image_name])
        image_immunohistochemistry_list.append(images_immunohistochemistry[image_name])

        (
            points_annotation_dataframe,
            s1hl_annotation_dataframe,
            out_of_pia_annotation_dataframe,
            cells_features_dataframe,
        ) = convert(cells_detection_path, annotation_path, pixel_size)


        # Remove Cluster features if exist
        # One removes the cluster feature because they are all the same for each cell
        cols = [
            c
            for c in cells_features_dataframe.columns
            if c.lower().find("cluster") == -1
        ]
        cells_features_dataframe = cells_features_dataframe[cols]


        # Write dataframe
        points_annotation_dataframe.to_csv(
            output_directory + "/" + image_name + "_points_annotations" + ".csv"
        )
        s1hl_annotation_dataframe.to_csv(
            output_directory + "/" + image_name + "_S1HL_annotations" + ".csv"
        )

        out_of_pia_annotation_dataframe.to_csv(
            output_directory + "/" + image_name + "_out_of_pia" + ".csv"
        )

        '''
        # Add image metadata
        bregma = images_lateral[image_name]
        bregma = bregma[bregma.find('around ') + 7:bregma.find('mm')]
        cells_features_dataframe['bregma'] = bregma
        '''

        cells_features_dataframe.to_csv(
            output_directory + "/" + image_name + "_cells_features" + ".csv"
        )


    metadata_df = pd.DataFrame(
        {
            "image": image_name_list,
            "lateral": image_lateral_list,
            "animal": image_animal_list,
            "immunohistochemistry ID": image_immunohistochemistry_list,
        }
    )
    metadata_df.to_pickle(output_directory + "/" "metadata.pkl")
    print("Done !")
