import configparser
import click
from qupath_processing.density import single_image_process
from qupath_processing.io import (
    write_dataframe_to_file,
    convert_files_to_dataframe,
    get_cells_coordinate
)

from qupath_processing.utilities import stereology_exclusion



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
    "--output-path", help="Output path where result files will be save", required=False
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
    
    # Apply stereology exclusion if needed.
    apply_exclusion=False
    print("INFO: Looks for stereology exclusion column")
    if recompute_exclusion_flag:
        print("INFO: Apply stereology exclusion")
        detections_dataframe = stereology_exclusion(detections_dataframe) 
        apply_exclusion = True 
    try:
        nb_exclude = detections_dataframe['exclude_for_density'].value_counts()[1] 
        print("INFO: Find stereology exclusion column")
                                           
    except IndexError:
        nb_exclude = 0
    except KeyError as e:
        # The exclude_for_density row does not exist, need to compute it"
        print("INFO: The stereology exclude_for_density row does not exist in the dataframe, one needs to compute it now.")
        print("INFO: Apply stereology exclusion")
        detections_dataframe = stereology_exclusion(detections_dataframe)
        apply_exclusion = True 
        try:
            nb_exclude = detections_dataframe['exclude_for_density'].value_counts()[1]
        except IndexError:
            nb_exclude = 0
        
        nb_exclude = detections_dataframe['exclude_for_density'].value_counts()[1]
        print(f'INFO: There are {nb_exclude} / {len(detections_dataframe)} excluded cells)')
        #detections_dataframe = detections_dataframe[detections_dataframe['exclude_for_density'] == False]



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


    if apply_exclusion:
        write_dataframe_to_file(detections_dataframe, cell_position_with_exclude_output_path)
        print(f'INFO: Write Cells dataframe with exclude flag to {cell_position_with_exclude_output_path}')

