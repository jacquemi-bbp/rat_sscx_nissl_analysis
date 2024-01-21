"""
Utilities module
"""

import pandas as pd
import numpy as np
import math
import random
from sklearn.neighbors import NearestNeighbors

class NotValidImage(Exception):
    pass


def stereology_exclusion(dataframe):
    """
    :param dataframe (pandas.dataframe)
    In order to obtain reasonable correction factor,
    we randomly assign a -z coordinate to each cell as well as an appropriate diameter
    (estimated from the nearest neighbouring cells)
    """

    data = dataframe[["Centroid X µm","Centroid Y µm"]].values
    nbrs = NearestNeighbors(n_neighbors=5,algorithm="kd_tree").fit(data)
    dataframe['mean_diameter'] = 0.5*(dataframe["Max diameter µm"] + dataframe["Min diameter µm"])

    def exclude(sample, slice_thickness = 50):
        sample['neighbors'] = nbrs.kneighbors(data,6,return_distance=False)[sample.name,:] #sample.name = row index
        neighbor_mean = dataframe.iloc[sample['neighbors']]['mean_diameter'].mean()
        sample['neighbor_mean'] = neighbor_mean
        sample['exclude_for_density'] = random.uniform(0,slice_thickness) + neighbor_mean/2 >= slice_thickness
        return sample
    dataframe_with_exclude_flag = dataframe.apply(exclude,axis=1)
    return dataframe_with_exclude_flag


def concat_dataframe(dest, source=None):
    """
    Concatenate source dataframe to dest
    :param source: (pandas.DataFrame)
    :param dest: (pandas.DataFrame)
    :return: pandas.DataFrame: The contatenation of source into dest
    Notes: If source == None, return dest Dataframe
    """
    if source is None:
        return dest
    return pd.concat([dest, source])


def get_angle(p1, p2) -> float:
    """Get the angle of this line with the horizontal axis."""
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    theta = math.atan2(dy, dx)
    if theta < 0:
        theta = math.pi * 2 + theta
    return theta


def get_image_animal(images_metadata):
    """
    Get image animal metadata value
    :param images_metadata: (dictionary) Key -> Image name. Values -> image metadata
    :return:
        str: The image lateral value or np.nan if not existing
    """
    results = {}
    for image in images_metadata:
        if "Animal" in image["metadata"]:
            results[image["imageName"]] = image["metadata"]["Animal"]
        else:
            results[image["imageName"]] = "ND"

    return results


def get_image_immunohistochemistry(images_metadata):
    """
    Get image Immunohistochemistry ID metadata value
    :param images_metadata: (dictionary) Key -> Image name. Values -> image metadata
    :return:
        str: The image lateral value or np.nan if not existing
    """
    results = {}
    for image in images_metadata:
        if "Immunohistochemistry ID" in image["metadata"]:
            results[image["imageName"]] = image["metadata"]["Immunohistochemistry ID"]
        else:
            results[image["imageName"]] = "ND"

    return results


def get_image_lateral(images_metadata):
    """
    Get image lateral metadata value
    :param images_metadata: (dictionary) Key -> Image name. Values -> image metadata
    :return:
        float: The image lateral value or np.nan if not existing
    """
    images_lateral = {}
    for image in images_metadata:
        if "Distance to midline" in image["metadata"]:
            images_lateral[image["imageName"]] = image["metadata"][
                "Distance to midline"
            ]
        else:
            images_lateral[image["imageName"]] = np.nan
    return images_lateral


def get_specific_metadata(images_metadata, meta_name, default=np.nan):
    """
    Get a metadata value
    :param images_metadata: (dictionary) Key -> Image name. Values -> image metadata
    :param meta_name: (str)> The name of the metadata
    :default: the default value to return if metadata name does not exist
    :return:
        float|str: The metadata value oif exist or default if not existing
    """
    result = {}
    for image in images_metadata:
        if meta_name in image["metadata"]:
            result[image["imageName"]] = image["metadata"][meta_name]
        else:
            result[image["imageName"]] = default
    return result

 


def  get_image_to_exlude_list(df_image_to_exclude):
    df_image_to_exclude=df_image_to_exclude.dropna().reset_index(drop=True)
    # Step 2: Apply a function to each value
    def remove_space(image_name):
        return image_name.replace(" ", "")
    new_image_name_column = df_image_to_exclude['Image ID to exclude'].apply(remove_space)

    # Step 3: Assign the new values back to the column
    df_image_to_exclude['Image ID to exclude'] = new_image_name_column
    return list(df_image_to_exclude['Image ID to exclude'])

