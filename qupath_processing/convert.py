"""
Convert QuPath Detections and annotation to pandas dataframe
"""
import pandas as pd

from qupath_processing.io import (
    qupath_cells_detection_to_dataframe,
    read_qupath_annotations,
)


def convert(cells_detection_file_path, annotations_file_path, pixel_size, convert_annotation=True):
    """
    :param cells_detection_file_path: path to the cells detection file produced by QuPath
    :param annotations_file_path: path to the annotations file produced by QuPath
    :param pixel_size(float)
    :return: tuple of pands datafrmae:
                    - points_annotation_dataframe
                    - s1hl_annotation_dataframe
                    - out_of_pia_annotation_dataframe
                    - cells_features_dataframe

    """
    points_annotation_dataframe = None
    s1hl_annotation_dataframe = None
    s1hl_annotation_dataframe = None
    out_of_pia_annotation_dataframe = None

    if convert_annotation:
        (
            s1_pixel_coordinates,
            quadrilateral_pixel_coordinates,
            out_of_pia,
        ) = read_qupath_annotations(annotations_file_path)

        points_annotation_dataframe = pd.DataFrame(
            quadrilateral_pixel_coordinates *  pixel_size,
            index=["top_left", "top_right", "bottom_right", "bottom_left"],
            columns=["Centroid X µm", "Centroid Y µm"],
        )

        s1hl_annotation_dataframe = pd.DataFrame(
            s1_pixel_coordinates * pixel_size,
            columns=["Centroid X µm", "Centroid Y µm"],
        )

        out_of_pia_annotation_dataframe = pd.DataFrame(
            out_of_pia *  pixel_size,
            columns=["Centroid X µm", "Centroid Y µm"],
        )
    cells_features_dataframe = pd.read_csv(cells_detection_file_path, sep="	|\t", engine="python", index_col=0)
    # Drop the features that cannot be used by the ML model

    features_to_drop = ['Object ID', 'Class', 'Parent', 'ROI',# 'Distance to midline mm',
                        'Distance to annotation with S1HL µm',
                        'Distance to annotation with SliceContour µm',
                        'Smoothed: 25 µm: Distance to annotation with S1HL µm',
                        'Smoothed: 25 µm: Distance to annotation with SliceContour µm',
                        'Smoothed: 50 µm: Distance to annotation with S1HL µm',
                        'Smoothed: 50 µm: Distance to annotation with SliceContour µm',
                        'Classification',
                        'Distance to midline mm',
                        'Object type',
                        'Smoothed: 50 µm: Distance to midline mm']

    for feature in features_to_drop:
        try:
            cells_features_dataframe = cells_features_dataframe.drop(feature, axis=1)
        except KeyError as e:
            print(e)

    cells_features_dataframe = cells_features_dataframe.rename(columns={"Name": "Expert_layer"})

    # if layers have not been set by and expert set the feature Expert_layer to N/A
    cells_features_dataframe.loc[cells_features_dataframe['Expert_layer'].astype(str).str.contains('Cellpose Julie Full'), 'Expert_layer'] = "Not applicable"


    return (
        points_annotation_dataframe,
        s1hl_annotation_dataframe,
        out_of_pia_annotation_dataframe,
        cells_features_dataframe,
        )
