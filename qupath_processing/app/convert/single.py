import click

from qupath_processing.io import (
    qupath_cells_detection_to_dataframe,
    read_qupath_annotations
)
import pandas as pd


@click.command()
@click.option('--cells-detection-file-path', required=True, help='QuPath exported file that contains cells detection features')
@click.option('--annotations-file-path', required=True, help='QuPath exported file that contains images annotations (S1HL, top_left, ...')
@click.option('--output-prefix', required=True, help='The prefix of the output files')
@click.option('--output-path', required=True, help='Path that will contain the converted data into two Dataframes')
def cmd(cells_detection_file_path, annotations_file_path, output_prefix, output_path):

    s1_pixel_coordinates, quadrilateral_pixel_coordinates, out_of_pia = read_qupath_annotations(annotations_file_path)

    points_annotation_dataframe = pd.DataFrame(quadrilateral_pixel_coordinates,
                 index=['top_left', 'top_right', 'bottom_right', 'bottom_left'],
                 columns=['Centroid X µm', 'Centroid Y µm'], )
    s1hl_annotation_dataframe = pd.DataFrame(s1_pixel_coordinates, columns=['Centroid X µm', 'Centroid Y µm'],)
    out_of_pia_annotation_dataframe = pd.DataFrame(out_of_pia, columns=['Centroid X µm', 'Centroid Y µm'], )
    cells_features_dataframe = qupath_cells_detection_to_dataframe(cells_detection_file_path)


    # Write dataframe
    points_annotation_dataframe.to_pickle(output_path + '/' + output_prefix + '_points_annotations' +'.pkl')
    s1hl_annotation_dataframe.to_pickle(output_path + '/' + output_prefix + '_S1HL_annotations' +'.pkl')
    cells_features_dataframe.to_pickle(output_path + '/' + output_prefix + '_cells_features' + '.pkl')
    out_of_pia_annotation_dataframe.to_pickle(output_path + '/' + output_prefix + '_out_of_pia' + '.pkl')

    print('Done !')

