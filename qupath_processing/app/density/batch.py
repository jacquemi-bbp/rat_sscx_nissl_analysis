import configparser
import click
from qupath_processing.density import single_image_process
from qupath_processing.io import (write_dataframe_to_file,
                                  list_images,
                                  convert_files_to_dataframe,
                                  get_cells_coordinate)
from qupath_processing.utilities import concat_dataframe, NotValidImage, stereology_exclusion


@click.command()
@click.option("--config-file-path", required=False, help="Configuration file path")
def batch_density(config_file_path):
    config = configparser.ConfigParser()
    config.sections()
    config.read(config_file_path)
    input_directory = config["BATCH"]["input_directory"]
    cell_position_suffix = config["BATCH"]["cell_position_suffix"].replace('"', "")
    annotations_geojson_suffix = config["BATCH"]["annotations_geojson_suffix"].replace(
        '"', ""
    )
    output_directory = config["BATCH"]["output_directory"]
    output_file_prefix = config["BATCH"]["output_file_prefix"]
    pixel_size = float(config["BATCH"]["pixel_size"])
    thickness_cut = float(config["BATCH"]["thickness_cut"])
    grid_nb_row = int(config["BATCH"]["grid_nb_row"])
    grid_nb_col = int(config["BATCH"]["grid_nb_col"])
    layer_names = config["BATCH"]["layer_names"]

    final_dataframe = None

    image_dictionary = list_images(
        input_directory, cell_position_suffix, annotations_geojson_suffix
    )
    print(f"INFO: input files: {list(image_dictionary.keys())}")
    if len(image_dictionary) == 0:
        print("WARNING: No input files to proccess.")
        return

    for image_prefix, values in image_dictionary.items():
        print("INFO: Process single image {}".format(image_prefix))
        try:
            detections_dataframe, s1_coordinates, quadrilateral_coordinates = (
                convert_files_to_dataframe(values["CELL_POSITIONS_PATH"],
                                           values["ANNOTATIONS_PATH"],
                                           pixel_size, ))

            # Apply stereology exclusion.
            print("INFO: Apply stereology exclusion")
            detections_dataframe = stereology_exclusion(detections_dataframe)
            try:
                nb_exclude = detections_dataframe['exclude'].value_counts()[1]
            except IndexError:
                nb_exclude = 0
            exclude_dataframe_filename= image_prefix + '_with_exclude_flags'
            write_dataframe_to_file(detections_dataframe, exclude_dataframe_filename, input_directory,
                                    exel_write=False)
            detections_dataframe = detections_dataframe[detections_dataframe.exclude == False]
            print(f'INFO: There are {nb_exclude} / {len(detections_dataframe)} excluded cells)')
            print(f'INFO: Write dataframe with exclude flag to {input_directory + "/" + exclude_dataframe_filename}')
            cells_centroid_x, cells_centroid_y = get_cells_coordinate(detections_dataframe)
            densities_dataframe = single_image_process(
                cells_centroid_x, cells_centroid_y, s1_coordinates, quadrilateral_coordinates,
                thickness_cut, grid_nb_row, grid_nb_col, image_prefix, layer_names,
                output_path=output_directory,
            )
            print("INFO: ", densities_dataframe)
            print("INFO: Concatenate results for image {}".format(image_prefix))
            final_dataframe = concat_dataframe(densities_dataframe, final_dataframe)
        except NotValidImage:
            print("WARNING. No cells position data for {}".format(image_prefix))

    if final_dataframe is not None:
        write_dataframe_to_file(final_dataframe, output_file_prefix, output_directory)
