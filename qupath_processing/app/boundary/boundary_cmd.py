import configparser
import click
import matplotlib.pyplot as plt
from qupath_processing.boundary import (
    clustering,
    get_cell_coordinate_by_layers
)



@click.command()
@click.option('--config-file-path', required=True, help='Configuration file path')
@click.option('--output-path',  required=True, help='Output path where result files will be save')
@click.option('--visualisation-flag', is_flag=True)
def cmd(config_file_path, output_path, visualisation_flag):

    config = configparser.ConfigParser()
    config.sections()
    config.read(config_file_path)
    cell_position_file_path = config['DEFAULT']['cell_position_file_path']
    annotations_geojson_path = config['DEFAULT']['annotations_geojson_path']
    layer_points = get_cell_coordinate_by_layers(cell_position_file_path)

    print(f'DEBUG {layer_points}')
    if visualisation_flag:
        plt.figure(figsize=(10, 10))
        plt.gca().invert_yaxis()
        #x_values = [top_left[0], top_right[0]]
        #y_values = [top_left[1], top_right[1]]
        #plt.plot(x_values, y_values, c='black')

        for XY in layer_points.values():
            plt.scatter(XY[:, 0], XY[:, 1], s=20, alpha=0.8)
        plt.title('Origin points per layer')
        plt.show()




