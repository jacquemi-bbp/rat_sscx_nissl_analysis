import os

import configparser
import click
import pandas as pd

from qupath_processing.density import single_image_process
from qupath_processing.io import (
    write_dataframe_to_file,
    get_cells_coordinate
)






@click.command()
@click.option("--config-file-path", required=False, help="Configuration file path")
@click.option(
    "--cell-position-file-path", help="Cells position dataframe file path.", required=False
)
@click.option(
    "--s1hl_path", help="S1HL annotations dataframe file path.", required=False
)
@click.option(
    "--points-annotations-path", help="Annotations dataframe file path.", required=False
)
@click.option(
    "--image-to-exlude-path", help="exel files taht contan the list of image to exclude (xlsx).", required=False
)

@click.option(
    "--thickness-cut", default=50, help="The thikness of the cut (default 50 um)"
)
@click.option(
    "--alpha", default= 0.01, type=float,
    required=False, help="Alpha value used to create alpha shape polygon from layer points"
)
@click.option("--nb-row", default=10, help="Number of row for the grid (default 100)")
@click.option(
    "--nb-col", default=10, help="Number of columns for the grid (default 100)"
)
@click.option(
    "--output-path", help="Output path where result files will be save", default='/tmp', required=False
)
@click.option("--visualisation-flag", is_flag=True)
@click.option("--save-plot-flag", is_flag=True)
def density(
    config_file_path,
    cell_position_file_path,
    points_annotations_path,
    s1hl_path,
    thickness_cut,
    nb_row,
    nb_col,
    output_path,
    image_to_exlude_path,
    visualisation_flag,
    save_plot_flag,
    alpha
):

    if config_file_path:

        config = configparser.ConfigParser()
        config.read(config_file_path)
        cell_position_file_path = config["DEFAULT"]["cell_position_file_path"]
        points_annotations_path = config["DEFAULT"]["points_annotations_file_path"]
        s1hl_path = config["DEFAULT"]["s1hl_file_path"]

        thickness_cut = float(config["DEFAULT"]["thickness_cut"])
        nb_row = int(config["DEFAULT"]["grid_nb_row"])
        nb_col = int(config["DEFAULT"]["grid_nb_col"])
        output_path = config["DEFAULT"]["output_path"]

        save_plot_flag = config.getboolean('DEFAULT', 'save_plot_flag')

        image_to_exlude_path = config["DEFAULT"]["image_to_exlude_path"]

    if points_annotations_path is None:
        print('ERROR: points-annotations-path is mandatory')
        return

    if s1hl_path is None:
        print('ERROR: s1hl-path is mandatory')
        return    

    image_name = cell_position_file_path[
        cell_position_file_path.rfind("/") + 1 : cell_position_file_path.rfind(".")
    ]

    # Verify that the image is not in the exlude images list
    if image_to_exlude_path:
        df_image_to_exclude = pd.read_excel(image_to_exlude_path, index_col=0, skiprows=[0,1,2,3,4,5,6])

    if not os.path.exists(output_path):
        # if the directory is not present then create it.
        os.makedirs(output_path)
        print(f'INFO: Create output_path {output_path}')

    print("INFO: Process single image ", image_name)
    percentage_dataframe, per_layer_dataframe = single_image_process(image_name,
                         cell_position_file_path,
                         points_annotations_path,
                         s1hl_path,
                         output_path,
                         df_image_to_exclude = df_image_to_exclude,
                         thickness_cut = thickness_cut,
                         nb_col = nb_col,
                         nb_row = nb_row,
                         visualisation_flag = visualisation_flag,
                         save_plot_flag = save_plot_flag,
                         alpha=alpha
                         )
    if percentage_dataframe is None:
        print("ERROR: The computed density percentage is not valid")
    else:
        print("INFO: Write density percentage dataframe")
        densities_dataframe_full_path = output_path + '/'+ image_name + '.csv'
        write_dataframe_to_file(percentage_dataframe, densities_dataframe_full_path)
        print(f'INFO: Write density percentage dataframe =to {densities_dataframe_full_path}')

    if per_layer_dataframe is None:
        print("ERROR: The computed density per layer is not valid")
    else:
        print("INFO: Write density per layer dataframe")
        densities_per_layer_dataframe_full_path = output_path + '/'+ image_name + '_per_layer.csv'
        write_dataframe_to_file(per_layer_dataframe, densities_per_layer_dataframe_full_path)
        print(f'INFO: Write density per layer dataframe =to {densities_per_layer_dataframe_full_path}')


