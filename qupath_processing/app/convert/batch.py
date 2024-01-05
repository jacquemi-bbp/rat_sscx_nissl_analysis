import os
import numpy as np
import pandas as pd
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


@click.command()
@click.option("--config-file-path", required=False, help="Configuration file path")
@click.option("--not-convert-annotation", required=False, help="If set do not convert the annotation files", is_flag=True)
def cmd(config_file_path, not_convert_annotation):

    convert_annotation_flag = True
    if not_convert_annotation:
        convert_annotation_flag = False
    config = configparser.ConfigParser()
    config.sections()
    config.read(config_file_path)

    input_directory = config["BATCH"]["input_directory"]

    cell_position_suffix = config["BATCH"]["cell_position_suffix"].replace('"', "")
    pixel_size = float(config["BATCH"]["pixel_size"])
    try:
        qpproj_path = config["BATCH"]["qpproj_path"]
    except KeyError:
        qpproj_path = None
    output_directory = config["BATCH"]["output_directory"]
    annotations_geojson_suffix = config["BATCH"]["annotations_geojson_suffix"]

    os.makedirs(output_directory, exist_ok=True)

    if qpproj_path:
        images_metadata = get_qpproject_images_metadata(qpproj_path)
        images_lateral = get_image_lateral(images_metadata)
        images_immunohistochemistry = get_image_immunohistochemistry(images_metadata)
        images_animal = get_image_animal(images_metadata)

    images_dictionary = list_images(
        input_directory, cell_position_suffix, annotations_geojson_suffix, convert_annotation_flag
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
        annotation_path = None
        if convert_annotation_flag:
            annotation_path = values["ANNOTATIONS_PATH"]
        image_name = image_prefix # values["IMAGE_NAME"]
        image_name_list.append(image_name)
        if qpproj_path:
            image_lateral_list.append(images_lateral[image_name])
            image_animal_list.append(images_animal[image_name])
            image_immunohistochemistry_list.append(images_immunohistochemistry[image_name])

        (
            points_annotation_dataframe,
            s1hl_annotation_dataframe,
            out_of_pia_annotation_dataframe,
            cells_features_dataframe,
        ) = convert(cells_detection_path, annotation_path, pixel_size, convert_annotation=convert_annotation_flag)


        # Remove Cluster features if exist
        # One removes the cluster feature because they are all the same for each cell
        cols = [
            c
            for c in cells_features_dataframe.columns
            if c.lower().find("cluster") == -1
        ]
        cells_features_dataframe = cells_features_dataframe[cols]


        # Write dataframe
        if points_annotation_dataframe:
            save_dataframe_without_space_in_path(points_annotation_dataframe,
                                              output_directory + "/" + image_name + "_points_annotations" + ".csv")


        if s1hl_annotation_dataframe:
            save_dataframe_without_space_in_path(s1hl_annotation_dataframe,
                                             output_directory + "/" + image_name + "_S1HL_annotations" + ".csv")

        if out_of_pia_annotation_dataframe:
            save_dataframe_without_space_in_path(out_of_pia_annotation_dataframe,
                                             output_directory + "/" + image_name + "_out_of_pia" + ".csv")

        '''
        # Add image metadata
        bregma = images_lateral[image_name]
        cells_features_dataframe['bregma'] = bregma
        '''
        save_dataframe_without_space_in_path(cells_features_dataframe,
                                             output_directory + "/" + "Features_" + image_name + ".csv")

    if qpproj_path:
        metadata_df = pd.DataFrame(
            {
                "image": image_name_list,
                "lateral": image_lateral_list,
                "animal": image_animal_list,
                "immunohistochemistry ID": image_immunohistochemistry_list,
            }
        )
        metadata_df.to_pickle(output_directory + "/" "metadata.pkl")
    print(f"Done ! All export dataframe saved into {output_directory}")
