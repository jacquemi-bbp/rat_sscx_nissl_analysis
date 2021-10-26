"""
build integration tests
"""
from pathlib import Path
import pandas as pd
from pandas.testing import assert_frame_equal
import qupath_processing.rat_sscx_nissl_processing as tested


DATA_DIR = Path(__file__).resolve().parent / 'data'



def test_single_image_process():
    """
    single image processing integration test
    """
    cell_position_file_path = DATA_DIR / '539_02_cell_position.txt'
    annotations_geojson_path = DATA_DIR / '539_02_annotations.geojson'
    pixel_size = 0.346
    thickness_cut = 50
    grid_nb_row = 100
    grid_nb_col = 100

    densities_dataframe = tested.single_image_process(cell_position_file_path,
                                                      annotations_geojson_path, pixel_size,
                                                      thickness_cut, grid_nb_row, grid_nb_col,
                                                      'test')
    reference_dataframe = pd.read_pickle(DATA_DIR / '539_02_dataframe.pkl')
    assert_frame_equal(reference_dataframe, densities_dataframe)
