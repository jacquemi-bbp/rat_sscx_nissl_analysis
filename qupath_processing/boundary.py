"""
Layers boundary module

"""

import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN

from qupath_processing.io import to_dataframe



def get_cell_coordinate_by_layers(cell_position_file_path):
    """

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
    if len(points) > 0:
        rotated_point = points.copy()
        c, s = np.cos(theta), np.sin(theta)
        R = np.array(((c, -s), (s, c)))
        rotated_point = np.dot(rotated_point, R.T)
        return rotated_point
    return np.zeros(((0, 0)), dtype=float)


def clustering(layer_name, X, _eps=100, log=False, figure=False):
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
