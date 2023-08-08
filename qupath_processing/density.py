"""
QuPath porcessing for rat somatosensory cortex Nissl data module
"""

import pandas as pd

from qupath_processing.geometry import (
    create_depth_polygons,
    create_grid,
    count_nb_cell_per_polygon,
)

from qupath_processing.visualisation import (
    plot_densities,
    plot_split_polygons_and_cell_depth,
)



# pylint: disable=too-many-arguments
# pylint: disable=too-many-locals

def single_image_process(
    cells_centroid_x, cells_centroid_y, s1_coordinates, quadrilateral_coordinates,
    thickness_cut, nb_row, nb_col, image_prefix, layers_name, layer_boundary_path=None,
    visualisation_flag=False, output_path=None,
):
    """
    :param cells_centroid_x:(np.array)
    :param cells_centroid_y:(np.array)
    :param s1_coordinates:(np.array)
    :param quadrilateral_coordinates:(np.array)
    :param thickness_cut:(float) um
    :param nb_row:(int)
    :param nb_col:(int)
    :param image_prefix(str)
    :param layers_name(list of str)
    :param layer_boundary_path:(str)
    :param visualisation_flag:(bool)
    :param output_path:(str)
    :return: densities_dataframe(pandas dataframe)

    """
    horizontal_lines, vertical_lines = create_grid(
        quadrilateral_coordinates, s1_coordinates, nb_row, nb_col
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
    if total_used_cells != len(cells_centroid_x):
        densities_dataframe = pd.DataFrame(
            {"image": [image_prefix], "depth_percentage": None, "densities": None}
        )
        print(
            f"ERROR there are  {len(cells_centroid_x) - total_used_cells } \
                cells outside the grid for a total of {len(cells_centroid_x)} cells"
        )

    else:
        densities_dataframe = pd.DataFrame(
            {
                "image": [image_prefix] * len(depth_percentage),
                "depth_percentage": depth_percentage,
                "densities": densities,
            }
        )

        if layer_boundary_path:
            boundary_df = pd.read_pickle(layer_boundary_path)
            boundaries_percentage = list(
                boundary_df["Layer bottom (percentage). Origin is top of layer 1"]
            )
        else:
            boundaries_percentage = None

        plot_split_polygons_and_cell_depth(
            split_polygons,
            s1_coordinates,
            cells_centroid_x,
            cells_centroid_y,
            vertical_lines=None,
            visualisation_flag=visualisation_flag,
            output_path=output_path,
            image_name=image_prefix,
        )

        plot_densities(
            depth_percentage,
            densities,
            layers_name,
            boundaries_percentage=boundaries_percentage,
            visualisation_flag=visualisation_flag,
            output_path=output_path,
            image_name=image_prefix,
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
