import click
import pandas as pd
from qupath_processing.utilities import stereology_exclusion


@click.command()
@click.option(
    "--dataframe-file-path", required=True, help="Full path to the input dataframe"
)
@click.option(
    "--dataframe-output-path",
    required=True,
    help="Output directory path to export the dataframe with the exclude_flag",
)

def cmd(
    dataframe_file_path, dataframe_output_path):

    print(f'INFO: Start cells exclusion')
    cells_features_dataframe = pd.read_csv(dataframe_file_path, index_col=0)
    cells_features_dataframe = stereology_exclusion(cells_features_dataframe)
    nb_exclude = cells_features_dataframe['exclude_for_density'].value_counts()[1]
    print(f'INFO: There are {nb_exclude} / {len(cells_features_dataframe)} excluded cells)')
    #Write Cells featrues dataframe
    slash_pos = dataframe_file_path.rfind('/')
    if slash_pos > -1:
        file_name = dataframe_file_path[slash_pos + 1:]
    else:
        file_name = dataframe_file_path

    full_path = dataframe_output_path + '/' + file_name

    print(f'INFO: Export cells features to {full_path}')
    cells_features_dataframe.to_csv(full_path)