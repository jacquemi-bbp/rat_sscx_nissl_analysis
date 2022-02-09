"""
Layers boundary module

"""

import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN

from qupath_processing.io import to_dataframe
from qupath_processing.utilities import get_angle


def get_cell_coordinate_by_layers(cell_position_file_path):
    """
    Read cells' coordinates from input file to fill a dictionary
    :param cell_position_file_path: (str)
    :return: dict: key -> Layer name, values np.array of shape (N, 2)
    """
    df = to_dataframe(cell_position_file_path)
    layer_points = {}
    for layer_name in ['Layer 1',
                       'Layer 2',
                       'Layer 3',
                       'Layer 4',
                       'Layer 5',
                       'Layer 6 a',
                       'Layer 6b']:
        layer = df[df["Class"] == layer_name]
        Xs = layer['Centroid X µm'].to_numpy(dtype=float)
        Ys = layer['Centroid Y µm'].to_numpy(dtype=float)
        layer_points[layer_name] = np.column_stack((Xs, Ys))
    return layer_points


def rotate_points_list(points, theta):
    """
    Rotate points to thetha radian angle
    :param points: (numpt.array) of shape (N, 2)
    :param theta: (float) angle to rotate
    :return: numpy.ndarray of shape (N, 2) The inputs point rotated
    """

    if len(points) > 0:
        rotated_point = points.copy()
        c, s = np.cos(theta), np.sin(theta)
        R = np.array(((c, -s), (s, c)))
        rotated_point = np.dot(rotated_point, R.T)
        return rotated_point
    return np.zeros((0, 0), dtype=float)


def rotated_cells_from_top_line(top_left, top_right, layer_clustered_points):
    """
    Compute angle theta between the line defined by top_left and to right.
    The rotate points to the theta angle
    :param top_left: (numpy.array) of shape (2, 2) cartesian coordinates
    :param top_right: (numpy.array) of shape (2, 2) cartesian coordinates
    :param layer_clustered_points: dict key
     -> layer name values -> numpy.ndarray od shape (N, 2)
    :return:
    """
    theta = - get_angle(top_left, top_right)
    layer_rotatated_points = {}
    for layer_label, XY in layer_clustered_points.items():
        layer_rotatated_points[layer_label] = rotate_points_list(XY, theta)

    top_points = np.array([top_left, top_right]).reshape(-1, 2)
    return layer_rotatated_points, rotate_points_list(top_points, theta)




def compute_dbscan_eps(cell_position_file_path, layers_name, factor=4):
    """
    Compute DBSCAN eps value per layer in function of Delaunay mean value of
    each cell from of a layer
    :param cell_position_file_path: (str) the input path containing data
    :param layers_name: (str) The current layer name
    :param factor: (float): factor to multiply the Delaunay mean value
    :return: list of float of DBSCAN eps values per layer
    (https://scikit-learn.org/stable/modules/generated/sklearn.cluster.DBSCAN.html)
    """
    layer_dbscan_eps = []
    df = to_dataframe(cell_position_file_path)
    for layer_name in layers_name:
        cells_mean_delaunay = df[df['Class'] == layer_name][
                                  'Delaunay: Mean distance'].to_numpy(
            dtype=float).mean() * factor
        layer_dbscan_eps.append(cells_mean_delaunay)
    return layer_dbscan_eps


def get_main_cluster(layers_name, layer_dbscan_eps, layer_points):
    """
    Apply DBSCAN algorithm on cells for a specific layer and return
    the main cluster. Used to remove cells that are far away from other cells
    of the same layer
    :param layers_name: (list of str) The layer names
    :param layer_dbscan_eps: list of float value representing DBSCAN eps values
    :param layer_points: dict: key -> (str) layer name values -> numpy.ndarray of shape (N, 2)
    :return: points from main cluster dict: key -> (str) layer name values -> numpy.ndarray of shape (N, 2)
    """

    layer_clustered_points = {}
    for layer_name, eps_value in zip(layers_name, layer_dbscan_eps):
        layer_clustered_points[layer_name] = clustering(layer_name,
                                                        layer_points[layer_name],
                                                        eps_value, figure=False)

        if len(layer_clustered_points[layer_name]) == 0:
            print(f'Clustering for layer {layer_name} returns zeros cells. Please change layer_dbscan_eps.')
            return None
    return layer_clustered_points


def clustering(layer_name, X, _eps=100, figure=False):
    """
    (https://scikit-learn.org/stable/modules/generated/sklearn.cluster.DBSCAN.html)
    :param layer_name:
    :param X:
    :param _eps:
    :param figure:
    :return:
    """
    labels_true = []
    labels_true.extend([layer_name] * X.shape[0])

    # #############################################################################
    # Compute DBSCAN
    db = DBSCAN(eps=_eps, min_samples=10).fit(X)
    core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
    core_samples_mask[db.core_sample_indices_] = True
    labels = db.labels_
    # Number of clusters in labels, ignoring noise if present.
    n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
    # #############################################################################
    # Plot result


    # Black removed and is used for noise instead.
    unique_labels = set(labels)
    colors = [plt.cm.Spectral(each) for each in
              np.linspace(0, 1, len(unique_labels))]
    return_coordinates = []
    for k, col in zip(unique_labels, colors):
        if k == -1:
            # Black used for noise.
            col = [0, 0, 0, 1]
        class_member_mask = labels == k

        xy = X[class_member_mask & ~core_samples_mask]
        if figure:
            plt.plot(
                xy[:, 0],
                xy[:, 1],
                "o",
                markerfacecolor=tuple(col),
                markeredgecolor="k",
                markersize=3,
            )

        xy = X[class_member_mask & core_samples_mask]
        if figure:
            plt.plot(
                xy[:, 0],
                xy[:, 1],
                "o",
                markerfacecolor=tuple(col),
                markeredgecolor="k",
                markersize=12,
            )

        # KEEP points from the bigger cluster  only
        if len(xy) > len(return_coordinates):
            return_coordinates = xy

    if figure:
        plt.gca().invert_yaxis()
        title = f'{layer_name} keep {len(return_coordinates) / X.shape[0] * 100:.2f} % of original points in main cluster'
        plt.title(title)
        plt.show()
    return return_coordinates
