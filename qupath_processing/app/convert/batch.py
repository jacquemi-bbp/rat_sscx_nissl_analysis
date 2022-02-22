import numpy as np
import configparser
import click

from qupath_processing.io import (
            write_dataframe_to_file,
            list_images,
            get_qpproject_images_metadata
            )
@click.command()
@click.option('--config-file-path', required=False, help='Configuration file path')
def cmd(config_file_path):
    config = configparser.ConfigParser()
    config.sections()
    config.read(config_file_path)

    input_directory = config['BATCH']['input_directory']
    cell_position_suffix = config['BATCH']['cell_position_suffix'].replace("\"","")
    annotations_geojson_suffix = config['BATCH']['annotations_geojson_suffix'].replace("\"","")
    qpproj_path = config['BATCH']['qpproj_path']
    output_directory = config['BATCH']['output_directory']
    output_file_prefix = config['BATCH']['output_file_prefix']

    image_dictionary = list_images(input_directory, cell_position_suffix, annotations_geojson_suffix)
    images_metadata = get_qpproject_images_metadata(qpproj_path)
    print(images_metadata)

    images_lateral= {}
    for image in images_metadata:
        if 'Exclude' in image['metadata']:
            images_lateral[image['imageName']] = image['metadata']['Exclude']
        else:
            images_lateral[image['imageName']] = np.nan

    print(images_lateral)



    for image_name in image_dictionary.keys():
        print(f'image {image_name}')
        try:
            lateral = images_lateral[image_name] 
            print(f'image {image_name}  lateral: {lateral}')
        except KeyError:
            print(f'No {image_name} medatada in QuPath project')

