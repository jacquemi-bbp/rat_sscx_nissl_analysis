"""
Convert QuPath Detections and annotation to pandas dataframe
"""
import os
import numpy as np
import pandas as pd


from qupath_processing.utilities import stereology_exclusion

from qupath_processing.io import (
    read_qupath_annotations,
)


def single_image_conversion(output_path, image_name,
                            cells_detection_path, annotations_path,
                            pixel_size, exclude=False):
    os.makedirs(output_path, exist_ok=True)

    print(f'INFO: Start annotation and cells features conversion')
    (
        points_annotation_dataframe,
        s1hl_annotation_dataframe,
        out_of_pia_annotation_dataframe,
        cells_features_dataframe,
    ) = convert(cells_detection_path, annotations_path, image_name, pixel_size)

    if cells_detection_path:
        # Remove Cluster features if exist
        # One removes the cluster feature because they are all the same for each cell
        cols = [
            c
            for c in cells_features_dataframe.columns
            if c.lower().find("cluster") == -1
        ]
        print(f'INFO: Remove cluster features if exist')
        cells_features_dataframe = cells_features_dataframe[cols]

        # START CELL EXCLUSION
        if exclude:
            print(f'INFO: Start cells exclusion')
            cells_features_dataframe = stereology_exclusion(cells_features_dataframe)
            nb_exclude = cells_features_dataframe['exclude_for_density'].value_counts()[1]
            print(f'INFO: There are {nb_exclude} / {len(cells_features_dataframe)} excluded cells)')

        # Write Cells featrues dataframe
        cells_features_path = output_path + "/" + "Features_" + image_name + ".csv"
        cells_features_path =  cells_features_path.replace(" ", "")
        print(f'INFO: Export cells features to {cells_features_path}')
        cells_features_dataframe.to_csv(cells_features_path)

    if annotations_path:
        # Write annotaion dataframe
        points_annotation_path =  output_path + "/" + image_name + "_points_annotations" + ".csv"
        points_annotation_path =  points_annotation_path.replace(" ", "")
        print(f'INFO: Export points annotation to {points_annotation_path}')
        points_annotation_dataframe.to_csv(points_annotation_path)

        s1hl_path = output_path + "/" + image_name + "_S1HL_annotations" + ".csv"
        s1hl_path = s1hl_path.replace(" ", "")
        print(f'INFO: Export S1HL annotation to {s1hl_path}')
        s1hl_annotation_dataframe.to_csv(s1hl_path )

        out_of_pia_path = output_path + "/" + image_name + "_out_of_pia" + ".csv"
        out_of_pia_path = out_of_pia_path.replace(" ", "")
        print(f'INFO: Export Out_of_pia annotation to {out_of_pia_path}')
        out_of_pia_annotation_dataframe.to_csv(out_of_pia_path)

    print(f"Done ! All export dataframe saved into {output_path}")

def convert(cells_detection_path, annotations_path,image_name,  pixel_size):
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
    out_of_pia_annotation_dataframe = None

    if annotations_path:
        (
            s1_pixel_coordinates,
            quadrilateral_pixel_coordinates,
            out_of_pia,
        ) = read_qupath_annotations(annotations_path, image_name)

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

    if cells_detection_path:
        cells_detection_file_path = cells_detection_path + '/' + image_name + ' Detections.txt'
        cells_features_dataframe = pd.read_csv(cells_detection_file_path, sep="\t", engine="python")
        # Drop the features that cannot be used by the ML model

        features_to_drop = ['Object ID', 'Class', 'Parent', 'ROI',# 'Distance to midline mm',
                            'Distance to annotation with S1HL µm',
                            'Distance to annotation with SliceContour µm',
                            'Smoothed: 25 µm: Distance to annotation with S1HL µm',
                            'Smoothed: 25 µm: Distance to annotation with SliceContour µm',
                            'Smoothed: 50 µm: Distance to annotation with S1HL µm',
                            'Smoothed: 50 µm: Distance to annotation with SliceContour µm',
                            #'Classification', # Comment for Ground Truth
                            'Name', # For Ground Truth
                            'Distance to midline mm',
                            'Object type',
                            'Smoothed: 50 µm: Distance to midline mm',
                            'Smoothed: 25 µm: Distance to annotation with Other µm']

        for feature in features_to_drop:
            try:
                cells_features_dataframe = cells_features_dataframe.drop(feature, axis=1)
            except KeyError as e:
                pass

        #cells_features_dataframe = cells_features_dataframe.rename(columns={"Name": "Expert_layer"}) # comment for Ground Truth
        cells_features_dataframe = cells_features_dataframe.rename(columns={"Classification": "Expert_layer"}) # uncomment Ground Truth

        # if layers have not been set by and expert set the feature Expert_layer to N/A
        cells_features_dataframe.loc[cells_features_dataframe['Expert_layer'].astype(str).str.contains('Cellpose Julie Full'), 'Expert_layer'] = "Not applicable"
    else:
        cells_features_dataframe = None


    return (
        points_annotation_dataframe,
        s1hl_annotation_dataframe,
        out_of_pia_annotation_dataframe,
        cells_features_dataframe,
        )
