
"""
Module that computes density as function of brain percentage of depth
"""

def compute_cell_density(nb_cell_per_slide, split_polygons, z_length):
    """
    Computes density as function of brain percentage of depth
    :param nb_cell_per_slide: list of int
    :param split_polygons: list of shapely polygons representing S1 layers as function if brain depth
    :param z_length: float ( thickness of the cut over z axis (mm)
    :return: tuple:
        -  depth_percentage: list of float representing the percentage of brain depth
        -  densities: list of float representing the number of cell by mm3
    #Pandas dataframe representing the density as function of brain percentage of depth (nb cells / mm3)
    """
    densities = []
    areas = []
    for nb_cell, polygon in zip(nb_cell_per_slide, split_polygons):
        areas.append(polygon.area)
        densities.append(nb_cell/ ((polygon.area / 1e6) * z_length))

    depth_percentage = [i/len(split_polygons) for i in range(len(split_polygons))]
    return depth_percentage, densities
