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
    "--cell-position-file-path", help="Cells position file path.", required=False
)
@click.option(
    "--annotations-geojson-path", help="Annotations geojson file path.", required=False
)
@click.option(
    "--pixel-size",
    help="Pixel size (default 0.3460130331522824)",
    required=False,
    type=float,
    default=0.3460130331522824,
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

@click.option(
    "--cell-position-with-exclude-output-path", help="Output path for the Cells dataframe with the excluded flag", required=False
)

@click.option(
    "--layer-boundary-path",
    help="Path to a pickle file that contains the dataframe of layer boundaries",
    required=False,
)
@click.option('--recompute-exclusion-flag', is_flag=True, help="Rest the exclusion flag and recompute it.")

@click.option("--visualisation-flag", is_flag=True)
def density(
    config_file_path,
    cell_position_file_path,
    annotations_geojson_path,
    pixel_size,
    thickness_cut,
    nb_row,
    nb_col,
    output_path,
    cell_position_with_exclude_output_path,
    layer_boundary_path,
    recompute_exclusion_flag,
    visualisation_flag,
):
    if config_file_path:
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

    cell_position_with_exclude_path = cell_position_with_exclude_output_path

    image_name = cell_position_file_path[
        cell_position_file_path.rfind("/") + 1 : cell_position_file_path.rfind(".")
    ]
    print("INFO: Process single image ", image_name)

    detections_dataframe, s1_coordinates, quadrilateral_coordinates = (
        convert_files_to_dataframe(cell_position_file_path,
                                   annotations_geojson_path,
                                   pixel_size, get_index_col=True))
    

    cells_centroid_x, cells_centroid_y = get_cells_coordinate(detections_dataframe)
    excluded_cells_centroid_x, excluded_cells_centroid_y = get_cells_coordinate(
        detections_dataframe, exclude_flag=True)
    densities_dataframe = single_image_process(
        cells_centroid_x, cells_centroid_y, s1_coordinates, quadrilateral_coordinates,
        thickness_cut, nb_row, nb_col, image_name, layer_names,
        excluded_cells_centroid_x, excluded_cells_centroid_y,
        layer_boundary_path=layer_boundary_path,
        visualisation_flag=visualisation_flag,
        output_path=output_path,
    )

    print("INFO: Write results")
    densities_dataframe_full_path = output_path + '/'+ image_name + '.csv'

    write_dataframe_to_file(densities_dataframe, densities_dataframe_full_path)
    print(f'INFO: Write density dataframe =to {densities_dataframe_full_path}')
