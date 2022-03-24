"""
Layers boundary module

"""

import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN

from qupath_processing.io import qupath_cells_detection_to_dataframe
from qupath_processing.utilities import get_angle


def get_layers_extremity(layer_dataframe, fnc, step=20):
    points = []
    x_min = int(layer_dataframe['Centroid X µm'].min())
    x_max = int(layer_dataframe['Centroid X µm'].max())
    for x_max in range(x_min+step, x_max, step):
        filter_df = layer_dataframe[layer_dataframe['Centroid X µm'] >= x_min]
        filter_df = filter_df[filter_df['Centroid X µm'] < x_max]
        if filter_df.size > 0:
            index = fnc(filter_df['Centroid Y µm'])
            x = filter_df.iloc[index]['Centroid X µm']
            y = filter_df.iloc[index]['Centroid Y µm']
            print(f'DEBUG y => {y}')
            points.append([x, y])
        x_min = x_max
    points = np.array(points)
    return points


def get_cell_coordinate_dataframe(cell_position_file_path, layers_name):
    """
    Read cells' coordinates from input file to fill a dictionary
    :param cell_position_file_path: (str)
    :parma layers_name (str)
    :return: dict: key -> Layer name, values np.array of shape (N, 2)
    """
    df = qupath_cells_detection_to_dataframe(cell_position_file_path)
    return df


def rotate_points_list(x_coors, y_coors, theta):
    """
    Rotate points to thetha radian angle
    :param x_coors: (numpt.array) of shape (N, )
    :param theta: (float) angle to rotate
    :return: numpy.ndarray of shape (N, 2) The inputs point rotated
    """
    assert len(x_coors) > 0
    points = np.vstack((x_coors, y_coors)).T
    rotated_point = points.copy()
    c, s = np.cos(theta), np.sin(theta)
    R = np.array(((c, -s), (s, c)))
    rotated_point = np.dot(rotated_point, R.T)
    return rotated_point[:, 0],  rotated_point[:, 1]



def rotated_cells_from_top_line(top_left, top_right, cells_dataframe):
    """
    Compute angle theta between the line defined by top_left and to right.
    The rotate points to the theta angle
    :param top_left: (numpy.array) of shape (2, 2) cartesian coordinates
    :param top_right: (numpy.array) of shape (2, 2) cartesian coordinates
    :param cells_dataframe: Datafame containing the cells features
     -> layer name values -> numpy.ndarray od shape (N, 2)
    :return: cells_dataframe with rotated points
    """
    theta = - get_angle(top_left, top_right)
    cells_dataframe['Centroid X µm'], cells_dataframe['Centroid Y µm'] = \
        rotate_points_list(cells_dataframe['Centroid X µm'], cells_dataframe['Centroid Y µm'], theta)
    return cells_dataframe, rotate_points_list(top_left, top_right, theta)


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


def get_main_cluster_ori(layers_name, layer_dbscan_eps, layer_points):
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


def get_main_cluster(layers_name, layer_dbscan_eps, dataframe):
    """
    Apply DBSCAN algorithm on cells for a specific layer and return
    the main cluster. Used to remove cells that are far away from other cells
    of the same layer
    :param layers_name: (list of str) The layer names
    :param layer_dbscan_eps: list of float value representing DBSCAN eps values
    :param dataframe:
    :return: points from main cluster dict: key -> (str) layer name values -> numpy.ndarray of shape (N, 2)
    """

    layer_clustered_points = {}
    for layer_name, eps_value in zip(layers_name, layer_dbscan_eps):
        xs = dataframe[dataframe.Class == layer_name]['Centroid X µm']
        ys = dataframe[dataframe.Class == layer_name]['Centroid Y µm']
        layers_points = layer_points[layer_name]
        if layers_points.shape[0] > 0:
            layer_clustered_points[layer_name] =\
                clustering(layer_name, layers_points,
                           eps_value, visualisation=False)
        else:
            layer_clustered_points[layer_name] = layers_points

    return result


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


def add_border_flag(cells_dataframe, layers_name, distance=20):
    """
    Add a flag to each cell in dataframe that represents the border feature
    """
    next_layers_dict = {}
    for index, layer in enumerate(layers_name):
        next_layers = layers_name[index + 1:]
        next_layers_dict[layer] = next_layers

    borders_cells = np.zeros(len(cells_dataframe.index), dtype=bool)
    for index, row in cells_dataframe.iterrows():
        if row.Class != 'Layer 6 b':
            next_layer_dfs = cells_dataframe[cells_dataframe.Class.isin(next_layers_dict[row.Class])]
            dfy = next_layer_dfs[abs(next_layer_dfs['Centroid Y µm']-row['Centroid Y µm']) < distance]
            df = dfy[abs(dfy['Centroid X µm']-row['Centroid X µm']) < distance]
            if df.size > 0:
                borders_cells[index] = True
    cells_dataframe['border'] = borders_cells
    return cells_dataframe


def locate_layers_bounderies(cells_dataframe, layers_name):
    """
    Compute layers boundaries. The bottom of each layer is used
    :param cells_dataframe
    :return:
    """
    # Find S1 ylength
    #y_origin = cells_dataframe['Centroid Y µm'].min()
    layer1_df = cells_dataframe[cells_dataframe.Class == 'Layer 1']
    y_origin = get_layers_extremity(layer1_df, np.argmin, 50)[:, 1].mean()
    S1HL_y_length = cells_dataframe['Centroid Y µm'].max() - y_origin
    boundaries_bottom = {}
    y_lines = []
    for layer in layers_name:
        if layer != 'Layer 6 b':
            layer_cells = cells_dataframe[cells_dataframe.Class == layer]
            border_cells = layer_cells[layer_cells.border == True]
            boundary = border_cells['Centroid Y µm'].mean() - y_origin
            y_lines.append(boundary)
        else:
            layer6b_df = cells_dataframe[cells_dataframe.Class == 'Layer 6 b']
            points = get_layers_extremity(layer6b_df, np.argmax, 40)
            boundary = points[:, 1].mean() - y_origin
            y_lines.append(boundary)



        percentage = (boundary) / S1HL_y_length
        boundaries_bottom[layer] = [boundary, percentage]
        print(f'INFO: {layer} layer_ymax = {boundary }')
    return boundaries_bottom, y_lines, y_origin


def get_valid_image(dataframe, layers_name):
    """
    filter input dataframe by keeping only image where layer boundaries are correctly ordered
    :param dataframe: pandas dataframe
    :param layers_name: list of string
    :return: tuple
        - pandas dataframe: The filtered dataframe
        - list of valid images
        - list of INvalid images
    """
    return_df = dataframe.copy()
    invalid_image = set()
    for image_name in set(dataframe['image']):
        image_df = dataframe[dataframe['image'] == image_name]
        last_pos = 0
        for layer_name in layers_name:
            pos = image_df[image_df['Layer'] == layer_name]['Layer bottom (um). Origin is top of layer 1'].to_numpy()
            #print(f'DEBUG {image_name} {layer_name} pos={pos} last_pos={last_pos}')
            if len(pos) == 0:
                # This layer does not exist
                # Remove these image layer boundaries from the final, valid dataframe
                return_df = return_df[return_df.image != image_name]
                invalid_image.add(image_name)
            else:
                if last_pos > pos:
                    # The prev layer boundary is upper the current one
                    # Remove these image layer boundaries from the final, valid dataframe
                    return_df = return_df[return_df.image != image_name]
                    invalid_image.add(image_name)
                last_pos = pos
    return return_df,  invalid_image
