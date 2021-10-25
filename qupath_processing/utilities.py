"""
Utilities module
"""

import pandas as pd

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
    return  pd.concat([dest, source])
