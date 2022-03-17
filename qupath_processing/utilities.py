"""
Utilities module
"""

import pandas as pd
import numpy as np
import math

class NotValidImage(Exception):
    pass


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
        if 'Animal' in image['metadata']:
            results[image['imageName']] = image['metadata']['Animal']
        else:
            results[image['imageName']] = 'ND'

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
        if 'Immunohistochemistry ID' in image['metadata']:
            results[image['imageName']] = image['metadata']['Immunohistochemistry ID']
        else:
            results[image['imageName']] = 'ND'

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
        if 'Distance to midline' in image['metadata']:
            images_lateral[image['imageName']] = image['metadata']['Distance to midline']
        else:
            images_lateral[image['imageName']] = np.nan
    return images_lateral
