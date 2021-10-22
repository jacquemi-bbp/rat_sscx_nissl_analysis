
"""
Module that computes density as function of brain percentage of depth
"""

import pandas as pd

def compute_cell_density(nb_cell_per_slide, split_polygons, z_length):
    """
    Computes density as function of brain percentage of depth
    :param nb_cell_per_slide: list of int
    :param split_polygons: list of shapely polygons representing S1 layers as function if brain depth
    :param z_length: float ( thickness of the cut over z axis (mm)
    :return: Pandas dataframe representing the density as function of brain percentage of depth (nb cells / mm3)
    """
    densities = []
    areas = []
    for nb_cell, polygon in zip(nb_cell_per_slide, split_polygons):
        areas.append(polygon.area)
        densities.append(nb_cell/ ((polygon.area / 1e6) * z_length))

    depth_percentage = [i/len(split_polygons) for i in range(len(split_polygons))]
    densities_df = pd.DataFrame({'depth_percentage': depth_percentage, 'densities': densities})
    return densities_df