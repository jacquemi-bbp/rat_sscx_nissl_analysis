import click
import numpy as np
import pandas as pd

from qupath_processing.io import (
    qupath_cells_detection_to_dataframe,
    get_qpproject_images_metadata
)
from qupath_processing.convert import (
    convert,
)
from qupath_processing.utilities import get_image_lateral



@click.command()
@click.option('--cells-detection-file-path', required=True, help='QuPath exported file that contains cells detection features')
@click.option('--annotations-file-path', required=True, help='QuPath exported file that contains images annotations (S1HL, top_left, ...')
@click.option('--output-prefix', required=True, help='The prefix of the output files')
@click.option('--output-path', required=True, help='Path that will contain the converted data into two Dataframes')
@click.option('--qupath-project-path', required=True, help='qupath project path that contains images metadata')
@click.option('--qupath-image-name', required=True, help='iamge name inside the qupath project')
def cmd(cells_detection_file_path, annotations_file_path, output_prefix, output_path, qupath_project_path,
        qupath_image_name):
    images_metadata = get_qpproject_images_metadata(qupath_project_path)
    images_lateral = get_image_lateral(images_metadata)
    try:
        lateral = images_lateral[qupath_image_name]
    except KeyError:
        print(f'INFO: There is no lateral metadata for image {qupath_image_name}')
        lateral = np.nan

    points_annotation_dataframe, s1hl_annotation_dataframe, out_of_pia_annotation_dataframe,\
    cells_features_dataframe = convert(cells_detection_file_path, annotations_file_path, lateral)

    # Write dataframe
    points_annotation_dataframe.to_pickle(output_path + '/' + output_prefix + '_points_annotations' +'.pkl')
    s1hl_annotation_dataframe.to_pickle(output_path + '/' + output_prefix + '_S1HL_annotations' +'.pkl')
    cells_features_dataframe.to_pickle(output_path + '/' + output_prefix + '_cells_features' + '.pkl')
    out_of_pia_annotation_dataframe.to_pickle(output_path + '/' + output_prefix + '_out_of_pia' + '.pkl')
    print('Done !')


