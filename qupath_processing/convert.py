"""
Convert QuPath Detections and annotation to pandas dataframe
"""
import numpy as np
import pandas as pd

from qupath_processing.io import (
    qupath_cells_detection_to_dataframe,
    read_qupath_annotations
)

def convert(cells_detection_file_path, annotations_file_path):
    """
    :param cells_detection_file_path: path to the cells detection file produced by QuPath
    :param annotations_file_path: path to the annotations file produced by QuPath
    :return: tuple of pands datafrmae:
                    - points_annotation_dataframe
                    - s1hl_annotation_dataframe
                    - out_of_pia_annotation_dataframe
                    - cells_features_dataframe

    """
    s1_pixel_coordinates, quadrilateral_pixel_coordinates, out_of_pia = read_qupath_annotations(annotations_file_path)

    points_annotation_dataframe = pd.DataFrame(quadrilateral_pixel_coordinates,
                                               index=['top_left', 'top_right', 'bottom_right', 'bottom_left'],
                                               columns=['Centroid X µm', 'Centroid Y µm'], )

    s1hl_annotation_dataframe = pd.DataFrame(s1_pixel_coordinates, columns=['Centroid X µm', 'Centroid Y µm'], )


    out_of_pia_annotation_dataframe = pd.DataFrame(out_of_pia, columns=['Centroid X µm', 'Centroid Y µm'], )
    cells_features_dataframe = qupath_cells_detection_to_dataframe(cells_detection_file_path)

    return points_annotation_dataframe, s1hl_annotation_dataframe, out_of_pia_annotation_dataframe,\
           cells_features_dataframe



