"""
QuPath porcessing for rat somatosensory cortex Nissl data module
"""

import pandas as pd

from qupath_processing.geometry import (
    create_depth_polygons,
    create_grid,
    count_nb_cell_per_polygon,
)

from qupath_processing.io import (
    get_cells_coordinate
)


from qupath_processing.visualisation import (
    plot_densities,
    plot_split_polygons_and_cell_depth,
)



# pylint: disable=too-many-arguments
# pylint: disable=too-many-locals

def single_image_process(image_name,
                         cell_position_file_path,
                        points_annotations_path,
                        s1hl_path,
                        output_path,
                        thickness_cut=50,
                        nb_row=10, nb_col=10,
                        visualisation_flag = False,
                        save_plot_flag = False):
    """
    param cell_position_file_path:
    param nb_row:
    param nb_col
    returns:
    """
    cells_features_df = pd.read_csv(cell_position_file_path, index_col=0)
    assert 'exclude_for_density' in cells_features_df.columns
    (cells_centroid_x, cells_centroid_y,
     excluded_cells_centroid_x, excluded_cells_centroid_y) =\
        get_cells_coordinate(cells_features_df)

    # Create grid from annotation
    s1_coordinates_dataframe = pd.read_csv(s1hl_path, index_col=0)
    points_annotations_dataframe = pd.read_csv(points_annotations_path, index_col=0)
    s1_coordinates = s1_coordinates_dataframe.to_numpy()
    top_left = points_annotations_dataframe[points_annotations_dataframe.index == 'top_left'].to_numpy()[0]
    top_right = points_annotations_dataframe[points_annotations_dataframe.index == 'top_right'].to_numpy()[0]
    bottom_right = points_annotations_dataframe[points_annotations_dataframe.index == 'bottom_right'].to_numpy()[0]
    bottom_left = points_annotations_dataframe[points_annotations_dataframe.index == 'bottom_left'].to_numpy()[0]

    horizontal_lines, vertical_lines = create_grid(
        top_left, top_right, bottom_left, bottom_right,
        s1_coordinates, nb_row, nb_col
    )


    split_polygons = create_depth_polygons(s1_coordinates, horizontal_lines)
    print("INFO: Computes the cells densities as function of percentage depth")
    nb_cell_per_slide = count_nb_cell_per_polygon(
        cells_centroid_x, cells_centroid_y, split_polygons
    )

    depth_percentage, densities, nb_cells = compute_cell_density(
        nb_cell_per_slide, split_polygons, thickness_cut / 1e3
    )

    total_used_cells = sum(nb_cells)
    if total_used_cells != len(cells_centroid_x) :
        densities_dataframe = pd.DataFrame(
            {"image": [image_name], "depth_percentage": None, "densities": None}
        )
        print(
            f"ERROR there are  {len(cells_centroid_x) - total_used_cells } "
            f"cells outside the grid for a total of {len(cells_centroid_x)} cells"
        )
        print(f'ERROR there are  {total_used_cells}/{len(cells_centroid_x)}  used cells')
        return None

    else:
        densities_dataframe = pd.DataFrame(
            {
                "image": [image_name] * len(depth_percentage),
                "depth_percentage": depth_percentage,
                "densities": densities,
            }
        )

    if visualisation_flag or save_plot_flag:
        plot_split_polygons_and_cell_depth(
            split_polygons,
            s1_coordinates,
            cells_centroid_x,
            cells_centroid_y,
            excluded_cells_centroid_x,
            excluded_cells_centroid_y,

            vertical_lines=vertical_lines,
            horizontal_lines=None,
            output_path=output_path,
            image_name=image_name,

            visualisation_flag=visualisation_flag,
            save_plot_flag=save_plot_flag,
        )

        plot_densities(
            depth_percentage,
            densities,
            output_path=output_path,
            image_name=image_name,
            visualisation_flag=visualisation_flag,
            save_plot_flag=save_plot_flag,
        )

    return densities_dataframe


def compute_cell_density(nb_cell_per_slide, split_polygons, z_length):
    """
    Computes density as function of brain percentage of depth
    :param nb_cell_per_slide: list of int
    :param split_polygons:list of shapely polygons representing S1 layers as function if brain depth
    :param z_length: float ( thickness of the cut over z axis (mm)
    :return: tuple:
        -  depth_percentage: list of float representing the percentage of brain depth
        -  densities: list of float representing the number of cell by mm3
    """
    nb_cells = []
    densities = []

    for nb_cell, polygon in zip(nb_cell_per_slide, split_polygons):
        nb_cells.append(nb_cell)
        densities.append(nb_cell / ((polygon.area / 1e6) * z_length))

    depth_percentage = [i / len(split_polygons) for i in range(len(split_polygons))]


    return depth_percentage, densities, nb_cells
