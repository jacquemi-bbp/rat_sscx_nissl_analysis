import configparser
import click
from qupath_processing.density import (
    single_image_process)
from qupath_processing.io import (
    write_dataframe_to_file,
)
from qupath_processing.utilities import (
        concat_dataframe, NotValidImage
)
from qupath_processing.version import VERSION




@click.command()
@click.option('--config-file-path', required=False, help='Configuration file path')
@click.option('--cell-position-file-path', help='Cells position file path.', required=False)
@click.option('--annotations-geojson-path', help='Annotations geojson file path.', required=False)
@click.option('--pixel-size', help='Pixel size (default 0.3460130331522824)', required=False, type=float, default=0.3460130331522824)
@click.option('--thickness-cut', default=50, help='The thikness of the cut (default 50 um)')
@click.option('--nb-row', default=100, help='Number of row for the grid (default 100)')
@click.option('--nb-col', default=100, help='Number of columns for the grid (default 100)')
@click.option('--output-path', help='Output path where result files will be save', required=False)
@click.option('--visualisation-flag', is_flag=True)
def density(config_file_path, cell_position_file_path, annotations_geojson_path, pixel_size,
            thickness_cut, nb_row, nb_col, output_path, visualisation_flag):
    if config_file_path:
        config = configparser.ConfigParser()
        config.sections()
        config.read(config_file_path)
        cell_position_file_path = config['DEFAULT']['cell_position_file_path']
        annotations_geojson_path = config['DEFAULT']['annotations_geojson_path']
        pixel_size = float(config['DEFAULT']['pixel_size'])
        thickness_cut = float(config['DEFAULT']['thickness_cut'])
        nb_row = int(config['DEFAULT']['grid_nb_row'])
        nb_col = int(config['DEFAULT']['grid_nb_col'])
        output_path = config['DEFAULT']['output_path']
    else:
        if output_path == None:
            print('ERROR --output-path is required')

    image_name = cell_position_file_path[cell_position_file_path.rfind('/')+1:cell_position_file_path.rfind('.')]
    print('INFO: Process single image ', image_name)
    densities_dataframe = single_image_process(cell_position_file_path, annotations_geojson_path, pixel_size, thickness_cut,
                         nb_row, nb_col, image_name,  visualisation_flag=visualisation_flag)
    print('INFO: ', densities_dataframe)
    print('INFO: Write results')
    write_dataframe_to_file(densities_dataframe, image_name, output_path)

