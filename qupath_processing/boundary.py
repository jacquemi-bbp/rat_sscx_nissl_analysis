"""
Layers boundary module

"""

import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN

from qupath_processing.io import qupath_cells_detection_to_dataframe
from qupath_processing.utilities import get_angle


def get_cell_coordinate_by_layers(cell_position_file_path, layers_name):
    """
    Read cells' coordinates from input file to fill a dictionary
    :param cell_position_file_path: (str)
    :parma layers_name (str)
    :return: dict: key -> Layer name, values np.array of shape (N, 2)
    """
    df = qupath_cells_detection_to_dataframe(cell_position_file_path)
    layer_points = {}
    for layer_name in layers_name:
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
    df = qupath_cells_detection_to_dataframe(cell_position_file_path)
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
        layers_points = layer_points[layer_name]
        if layers_points.shape[0] > 0:
            layer_clustered_points[layer_name] =\
                clustering(layer_name, layers_points,
                           eps_value, visualisation=False)
        else:
            layer_clustered_points[layer_name] = layers_points

    return layer_clustered_points


def clustering(layer_name, coordinates, _eps=100, visualisation=False):
    """
    Perform DBSCAN clustering from vector array or distance matrix.
    (https://scikit-learn.org/stable/modules/generated/sklearn.cluster.DBSCAN.html)
    :param layer_name: (str) The layer name
    :param coordinates: (numpy.array) of shape (N, 2)
    :param _eps: (float) eps value use for the DBSCAN algorithm
    :param visualisation: (bool) enable visualisation
    :return: Coordinates of main cluster (numpy.array) of shape (N, 2)
    """
    labels_true = []
    labels_true.extend([layer_name] * coordinates.shape[0])

    # #############################################################################
    # Compute DBSCAN
    db = DBSCAN(eps=_eps, min_samples=10).fit(coordinates)
    core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
    core_samples_mask[db.core_sample_indices_] = True
    labels = db.labels_

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

        xy = coordinates[class_member_mask & ~core_samples_mask]
        if visualisation:
            plt.plot(
                xy[:, 0],
                xy[:, 1],
                "o",
                markerfacecolor=tuple(col),
                markeredgecolor="k",
                markersize=3,
            )

        xy = coordinates[class_member_mask & core_samples_mask]
        if visualisation:
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

    if visualisation:
        plt.gca().invert_yaxis()
        title = f'{layer_name} keep {len(return_coordinates) / X.shape[0] * 100:.2f} % of original points in main cluster'
        plt.title(title)
        plt.show()
    return return_coordinates


def locate_layers_bounderies(layer_rotatated_points, layers_name):
    """
    Compute layers boundaries. The bottom of each layer is used
    :param layer_rotatated_points:
    :paramn S1HL_length:
    :return:
    """

    # Find S1 ylength
    min_y = 9999999
    max_y = 0
    for XY in layer_rotatated_points.values():
        if len(XY) > 0:
            if XY[:, 1].min() < min_y:
                min_y = XY[:, 1].min()
            if XY[:, 1].max() > max_y:
                max_y = XY[:, 1].max()
    S1HL_y_length = max_y - min_y

    print(f'INFO: S1HL y length = {S1HL_y_length}')

    y_origin = layer_rotatated_points['Layer 1'][:, 1].min()

    boundaries_bottom = {}
    y_lines = []
    for layer_label in layers_name:
        XY = layer_rotatated_points[layer_label]
        if XY.shape[0] > 0:
            y_coors = XY[:, 1]
            layer_ymax = y_coors[y_coors.argsort()[-10:-1]].mean()
            y_lines.append(layer_ymax)

            percentage = (layer_ymax - y_origin) / S1HL_y_length
            boundaries_bottom[layer_label] = [layer_ymax - y_origin, percentage]
    return boundaries_bottom, y_lines, y_origin


def get_valid_image(dataframe, layers_name):
    """
    filter input dataframe by keeping only image where layer boundaries are correctly ordered
    :param dataframe: pandas dataframe
    :param layers_name: list of string
    :return: pandas dataframe: The filtered dataframe
    """
    return_df = dataframe.copy()
    for image_name in set(dataframe['image']):
        image_df = dataframe[dataframe['image'] == image_name]
        last_pos = 0
        for layer_name in layers_name:
            pos = image_df[image_df['Layer'] == layer_name]['Layer bottom (um). Origin is top of layer 1'].to_numpy()
            if last_pos > pos:
                return_df = return_df[return_df.image != image_name]
            last_pos = pos
    return return_df
