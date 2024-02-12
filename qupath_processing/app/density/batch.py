import os
import glob

import pandas as pd

import configparser
import click

from qupath_processing.density import single_image_process
from qupath_processing.io import (write_dataframe_to_file,
                                  list_images,
                                  get_cells_coordinate)
from qupath_processing.utilities import concat_dataframe, NotValidImage, stereology_exclusion


@click.command()
@click.option("--config-file-path", required=False, help="Configuration file path")
@click.option("--visualisation-flag", is_flag=True)
@click.option("--save-plot-flag", is_flag=True)
@click.option("--do-not-compute-per-layer", is_flag=True)
@click.option("--do-not-compute-per-depth", is_flag=True)
@click.option(
    "--image-to-exlude-path", help="exel files that contains the list of image to exclude (xlsx).", required=False
)

def batch_density(config_file_path, visualisation_flag, save_plot_flag,
                 image_to_exlude_path,
                  do_not_compute_per_layer, do_not_compute_per_depth):
    config = configparser.ConfigParser()
    config.sections()
    config.read(config_file_path)
    cell_position_path = config["BATCH"]["cell_position_path"]
    cell_position_file_prefix = config["BATCH"]["cell_position_file_prefix"]

    if not do_not_compute_per_depth:
        points_annotations_path = config["BATCH"]["points_annotations_path"]
        points_annotations_file_prefix = config["BATCH"]["points_annotations_file_prefix"]

        s1hl_path = config["BATCH"]["s1hl_path"]
        s1hl_file_prefix = config["BATCH"]["s1hl_file_prefix"]

    output_path = config["BATCH"]["output_path"]
    thickness_cut = float(config["BATCH"]["thickness_cut"])
    nb_row = int(config["BATCH"]["nb_row"])
    nb_col = int(config["BATCH"]["nb_col"])

    try:
        alpha = int(config["BATCH"]["alpha"])
    except KeyError:
        alpha = 0.05

    # List images to compute
    image_path_list = glob.glob(cell_position_path + '/*.csv')

    image_list = []
    feature_str_length = len('Features_')
    for path in image_path_list:
        feature_pos = path.rfind('Features_') + feature_str_length
        image_list.append(path[feature_pos:path.find('.csv')])


    if len(image_list) == 0:
        print("WARNING: No input files to process.")
        return

    print(f'INFO" {len(image_list)} to process')

    if not os.path.exists(output_path):
        # if the directory is not present then create it.
        os.makedirs(output_path)
        print(f'INFO: Create output_path {output_path}')

    # Verify that the image is not in the exlude images list
    if image_to_exlude_path:
        df_image_to_exclude = pd.read_excel(image_to_exlude_path, index_col=0, skiprows=[0,1,2,3,4,5,6,7])


    for image_name in image_list:
        print("INFO: Process single image ", image_name)

        cell_position_file_path = cell_position_path + '/' + cell_position_file_prefix + image_name + '.csv'

        if not do_not_compute_per_depth:
            points_annotations_file_path = (points_annotations_path + '/' + points_annotations_file_prefix +
                                            image_name + '_points_annotations.csv')
            s1hl_file_path = s1hl_path + '/' + s1hl_file_prefix + image_name + '_S1HL_annotations.csv'
        else:
            points_annotations_file_path = None
            s1hl_file_path = None


        densities_dataframe, per_layer_dataframe = single_image_process(image_name,
                             cell_position_file_path,
                             points_annotations_file_path,
                             s1hl_file_path,
                             output_path,
                             df_image_to_exclude = df_image_to_exclude,
                             thickness_cut = thickness_cut,
                             nb_col = nb_col,
                             nb_row = nb_row,
                             visualisation_flag = visualisation_flag,
                             save_plot_flag = save_plot_flag,
                             alpha = alpha,
                             do_not_compute_per_layer = do_not_compute_per_layer,
                             do_not_compute_per_depth = do_not_compute_per_depth
                             )
        if not do_not_compute_per_depth:
            if densities_dataframe is None:
                print(f"ERROR: {image_name} The computed density is not valid to compute the per depth density")
            else:
                densities_dataframe_full_path = output_path + '/'+ image_name + '.csv'

                write_dataframe_to_file(densities_dataframe, densities_dataframe_full_path)
                print(f'INFO: Write density dataframe =to {densities_dataframe_full_path}')

        if not do_not_compute_per_layer :
            if  per_layer_dataframe is None:
                print("ERROR: The computed density per layer is not valid to compute the per depth density")
            else:
                densities_per_layer_dataframe_full_path = output_path + '/' + image_name + '_per_layer.csv'
                write_dataframe_to_file(per_layer_dataframe, densities_per_layer_dataframe_full_path)
                print(f'INFO: Write density per layer dataframe =to {densities_per_layer_dataframe_full_path}')





