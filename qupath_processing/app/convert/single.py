import click
import os
import numpy as np
import pandas as pd

from qupath_processing.io import (
    qupath_cells_detection_to_dataframe,
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
@click.option(
    "--cells-detection-file-path",
    required=True,
    help="QuPath exported file that contains cells detection features",
)
@click.option(
    "--annotations-file-path",
    required=True,
    help="QuPath exported file that contains images annotations (S1HL, top_left, ...",
)
@click.option(
    "--output-path",
    required=True,
    help="Path that will contain the converted data into two Dataframes",
)
@click.option(
    "--qupath-project-path",
    required=True,
    help="qupath project path that contains images metadata",
)
@click.option(
    "--qupath-image-name", required=True, help="iamge name inside the qupath project"
)
@click.option(
    "--pixel-size", required=True, type=float, help="The pixel size in the QuPath project"
)
def cmd(
    cells_detection_file_path,
    annotations_file_path,
    output_path,
    qupath_project_path,
    qupath_image_name,
    pixel_size
):
    os.makedirs(output_path, exist_ok=True)
    images_metadata = get_qpproject_images_metadata(qupath_project_path)
    images_lateral = get_image_lateral(images_metadata)
    try:
        lateral = images_lateral[qupath_image_name]
    except KeyError:
        print(f"INFO: There is no lateral metadata for image {qupath_image_name}")
        lateral = np.nan

    (
        points_annotation_dataframe,
        s1hl_annotation_dataframe,
        out_of_pia_annotation_dataframe,
        cells_features_dataframe,
    ) = convert(cells_detection_file_path, annotations_file_path, pixel_size)

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
        output_path + "/" + qupath_image_name + "_points_annotations" + ".csv"
    )
    s1hl_annotation_dataframe.to_csv(
        output_path + "/" + qupath_image_name + "_S1HL_annotations" + ".csv"
    )

    out_of_pia_annotation_dataframe.to_csv(
        output_path + "/" + qupath_image_name + "_out_of_pia" + ".csv"
    )

    cells_features_dataframe.to_csv(
        output_path + "/" + qupath_image_name + "_cells_features" + ".csv"
    )

    images_immunohistochemistry = get_image_immunohistochemistry(images_metadata)
    images_animal = get_image_animal(images_metadata)
    metadata_df = pd.DataFrame(
    {
        "image": qupath_image_name,
        "lateral": lateral,
        "animal": images_animal,
        "immunohistochemistry ID": images_immunohistochemistry,
    }
    )
    metadata_df.to_pickle(output_path + "/" + qupath_image_name + "_" "metadata.pkl")
    print(f"Done ! All export dataframe saved into {output_path}")