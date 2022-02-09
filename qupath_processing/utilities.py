"""
Utilities module
"""

import pandas as pd
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