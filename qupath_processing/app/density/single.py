import configparser
import click
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
    "--annotations-file-path", help="Annotations dataframe file path.", required=False
)

@click.option(
    "--thickness-cut", default=50, help="The thikness of the cut (default 50 um)"
)
@click.option("--nb-row", default=100, help="Number of row for the grid (default 100)")
@click.option(
    "--nb-col", default=100, help="Number of columns for the grid (default 100)"
)
@click.option(
    "--output-path", help="Output path where result files will be save", default='/tmp', required=False
)

@click.option("--visualisation-flag", is_flag=True)
def density(
    config_file_path,
    cell_position_file_path,
    annotations_file_path,
    thickness_cut,
    nb_row,
    nb_col,
    output_path,
    visualisation_flag,
):

    if config_file_path:
        '''
        config = configparser.ConfigParser()
        config.read(config_file_path)
        cell_position_file_path = config["DEFAULT"]["cell_position_file_path"]
        cell_position_with_exclude_output_path = config["DEFAULT"]["cell_position_with_exclude_output_path"]
        annotations_geojson_path = config["DEFAULT"]["annotations_path"]
        pixel_size = float(config["DEFAULT"]["pixel_size"])
        thickness_cut = float(config["DEFAULT"]["thickness_cut"])
        nb_row = int(config["DEFAULT"]["grid_nb_row"])
        nb_col = int(config["DEFAULT"]["grid_nb_col"])
        output_path = config["DEFAULT"]["output_path"]
        layer_names = config["DEFAULT"]["layer_names"]
        '''
    else:
        layer_names = [
            "Layer 1",
            "Layer 2",
            "Layer 3",
            "Layer 4",
            "Layer 5",
            "Layer 6 a",
            "Layer 6 b",
        ]
    image_name = cell_position_file_path[
        cell_position_file_path.rfind("/") + 1 : cell_position_file_path.rfind(".")
    ]
    print("INFO: Process single image ", image_name)

    single_image_process(cell_position_file_path)

    '''
      cells_centroid_x, cells_centroid_y = get_cells_coordinate(detections_dataframe)
    excluded_cells_centroid_x, excluded_cells_centroid_y = get_cells_coordinate(
        detections_dataframe, exclude_flag=True)
    
    densities_dataframe = single_image_process(
        cells_centroid_x, cells_centroid_y, s1_coordinates, quadrilateral_coordinates,
        thickness_cut, nb_row, nb_col, image_name, layer_names,
        excluded_cells_centroid_x, excluded_cells_centroid_y,
        visualisation_flag=visualisation_flag,
        output_path=output_path,
    )

    print("INFO: Write results")
    densities_dataframe_full_path = output_path + '/'+ image_name + '.csv'

    write_dataframe_to_file(densities_dataframe, densities_dataframe_full_path)
    print(f'INFO: Write density dataframe =to {densities_dataframe_full_path}')

    '''

