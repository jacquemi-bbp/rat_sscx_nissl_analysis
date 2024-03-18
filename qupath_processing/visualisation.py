"""
visualisation module
"""

import matplotlib.pyplot as plt
import numpy as np
from qupath_processing.geometry import compute_cells_depth

#plt.rcParams["font.family"] = "Arial"
layers_color = {"Layer 1": "#ff0000"
            , "Layer 2":"#ff0099"
            , "Layer 3":"#cc00ff"
            , "Layer 2/3":"#751402"
            , "Layer 4":"#3300ff"
            , "Layer 5":"#0066FF"
            , "Layer 6 a":"#00ffff"
            , "Layer 6 b":"#00ff66"
           }
def get_layer_colors(values):
    colors = list(layers_color.values())

    if len(values) == 6: # Merged 2/3
        return np.take(colors, [0,3,4,5,6,7])

    elif len(values) == 7: # distinguish 2 and 3
        return np.take(colors, [0,1,2,4,5,6,7])

def plot_segment(line, color='black'):
    pt1 = line[0]
    pt2 = line[1]
    plt.plot([pt1[0], pt2[0]], [pt1[1], pt2[1]],  linestyle="-", c=color)

def plot_densities(
    percentages,
    densities,
    output_path=None,
    image_name="",
    visualisation_flag=False,
    save_plot_flag=False,
):
    """
    Plot the density per layers that represent the brain depth
    :param percentages: list of brain depth percentage (float)
    :param layers_names: list of str
    :param densities:  list of float (nb cells / mm3)
    :param image_name:
    """

    fig, ax = plt.subplots()
    ax.plot(densities, np.array(percentages) * 100)
    ax.set_xlabel("Cell density (cells/mm3)")
    ax.set_ylabel("percentage of depth (%)")
    ax.invert_yaxis()

    title = "Cell densities as function of percentage of depth"
    if image_name:
        title = image_name + " " + title
    ax.set_title(title)

    
    if visualisation_flag:
        plt.show()
    elif save_plot_flag:
        file_path = output_path + "/" + image_name + "_density_per_animal_.svg"
        plt.savefig(file_path, dpi=150)
    plt.clf()


def plot_split_polygons_and_cell_depth(
    split_polygons,
    s1_coordinates,
    cells_centroid_x,
    cells_centroid_y,
    excluded_cells_centroid_x=None,
    excluded_cells_centroid_y=None,
    vertical_lines=None,
    horizontal_lines=None,
    output_path=None,
    image_name=None,

    visualisation_flag=False,
    save_plot_flag=False,
):
    """
    Plot splitted S1 polgygons and cell coordiantes and depth
    :param split_polygons: list of shapely polygons representing S1 layers as
    function if brain depth
    :param s1_coordinates:(np.array) of shape (nb_vertices, 2) containing S1
    polygon coordinates (mm
    :param cells_centroid_x: np.array of shape (number of cells, ) of type float
    :param cells_centroid_y: np.array of shape (number of cells, ) of type float
    :return:
    """
    cells_depth = compute_cells_depth(
        split_polygons, cells_centroid_x, cells_centroid_y
    )
    colors_depth = {}
    for depth in np.unique(cells_depth):
        colors_depth[depth] = np.random.rand(1, 3)

    colors = []
    for depth in cells_depth:
        colors.append(colors_depth[depth])

    fig = plt.figure()
    fig.set_size_inches(18.5, 10.5)
    plt.axis("equal")
    plt.gca().invert_yaxis()
    for polygon in split_polygons:
        plt.plot(*polygon.exterior.xy, c='black')
    plt.plot(s1_coordinates[:, 0], s1_coordinates[:, 1], "r")
    plt.scatter(cells_centroid_x, cells_centroid_y, c='blue', s=1, alpha=.5, label='preserved cells')
    if excluded_cells_centroid_x is not None and excluded_cells_centroid_y is not None:
        plt.scatter(excluded_cells_centroid_x, excluded_cells_centroid_y, c='red', s=1, label='exluded cells')
    if vertical_lines:
        for line in vertical_lines[1:-1]:
            line = line.coords
            plot_segment(line)
    if horizontal_lines:
        for line in horizontal_lines:
            x = line.xy[0]
            y = line.xy[1]
            for i in range(0, len(x), 1):
                plt.plot(x[i:i + 2], y[i:i + 2], '-', linewidth=1, c='black')
    title = "Somatosensory cortex. Each layer represents a percentage of depth following the top of the SSX"
    if image_name:
        title = image_name + " " + title
    plt.title(title)
    plt.xlabel("X coordinates (um)")
    plt.ylabel("Y coordinates (um)")
    plt.legend()
    if visualisation_flag:
        plt.show()
    elif save_plot_flag:
        file_path = output_path + "/" + image_name + "_split_polygons_per_animal_.svg"
        print(f'plt.savefig {file_path}')
        plt.savefig(file_path)
    plt.clf()



def plot_raw_data(top_left, top_right, layer_points, image_name=""):
    """
    Display raw data cells and top line:
        - The original cells coordinates with top_line
        - The main cluster per layers cells with top_line
        - The rotated main cluster per layers cells with rotated top_line
    :param top_left:
    :param top_right:
    :param layer_points:
    """
    x_values = [top_left[0], top_right[0]]
    y_values = [top_left[1], top_right[1]]

    plt.figure(figsize=(8, 6))
    plt.gca().invert_yaxis()
    plt.plot(x_values, y_values, c="black")
    for XY in layer_points.values():
        plt.scatter(XY[:, 0], XY[:, 1], s=6, alpha=1.0)
    plt.title(image_name + " Raw data cells (one color per layer)")
    plt.show()
    plt.clf()


def plot_cluster_cells(top_left, top_right, layer_clustered_points, image_name=""):
    """
    Display cells from the main cluster for ech layer:
        - The original cells coordinates with top_line
        - The main cluster per layers cells with top_line
        - The rotated main cluster per layers cells with rotated top_line
    :param top_left:
    :param top_right:
    :param layer_points:
    :param layer_clustered_points:
    :param rotated_top_line:
    :param layer_rotatated_points:
    """
    x_values = [top_left[0], top_right[0]]
    y_values = [top_left[1], top_right[1]]

    plt.figure(figsize=(8, 6))

    # CELLS from the main cluster (after DBSCAN)
    plt.gca().invert_yaxis()
    for XY in layer_clustered_points.values():
        plt.scatter(XY[:, 0], XY[:, 1], s=6, alpha=1.0)
        plt.title(image_name + " After removing points outside the clusters")
        plt.plot(x_values, y_values, c="black")
    plt.show()
    plt.clf()

def plot_rotated_cells(rotated_top_line, layer_rotatated_points, image_name=""):
    """
    Display rotatated cell and top line:
        - The original cells coordinates with top_line
        - The main cluster per layers cells with top_line
        - The rotated main cluster per layers cells with rotated top_line
    :param rotated_top_line:
    :param layer_rotatated_points:
    """

    plt.figure(figsize=(8, 6))
    # ROTATED CELLS fron the main cluster
    plt.gca().invert_yaxis()
    x_values = [rotated_top_line[0][0], rotated_top_line[1][0]]
    y_values = [rotated_top_line[0][1], rotated_top_line[1][1]]
    plt.plot(x_values, y_values, c="black")
    for XY in layer_rotatated_points.values():
        if XY.shape[0] > 0:
            plt.scatter(XY[:, 0], XY[:, 1], s=6, alpha=1.0)
    plt.title(image_name + " After clustering and rotation")
    plt.show()
    plt.clf()


def plot_layers_bounderies(
    cells_rotated_df,
    boundaries_bottom,
    y_lines,
    rotated_top_line,
    y_origin,
    layers_name,
    image_name,
    output_path,
    visualisation_flag=False,
):
    """
    Display layers boundaries
    :param cells_rotated_df:
    :param boundaries_bottom: list [0] -> absolute boundary [1] -> percentage boundary
    :param y_lines:
    :param rotated_top_line:
    :param y_origin:
    :param layers_name:
    :param image_name:
    :param output_path:
    :param visualisation_flag:
    """
    layers_name = set(cells_rotated_df.Class)
    plt.figure(figsize=[8, 8])
    plt.gca().invert_yaxis()
    xmin = cells_rotated_df["Centroid X µm"].to_numpy(dtype=float).min()
    xmax = cells_rotated_df["Centroid X µm"].to_numpy(dtype=float).max()
    half_letter_size = 10
    xmean = (xmax + xmin) / 2
    for index, layer in enumerate(layers_name):
        df_layer = cells_rotated_df[cells_rotated_df.Class == layer]
        sc = plt.scatter(
            df_layer["Centroid X µm"].to_numpy(dtype=float),
            df_layer["Centroid Y µm"].to_numpy(dtype=float) - y_origin,
            s=2,
        )
        border_cells = df_layer[df_layer["border"] == True]
        col = sc.get_facecolors()[0].tolist()
        plt.scatter(
            border_cells["Centroid X µm"].to_numpy(dtype=float),
            border_cells["Centroid Y µm"].to_numpy(dtype=float) - y_origin,
            s=10,
            color=col,
        )
        y = boundaries_bottom[layer][0] + half_letter_size
        plt.hlines(y, xmin, xmax, color="red")
        plt.text(xmean, y - 4 * half_letter_size, layer, size="xx-large")
    plt.hlines(0, xmin, xmax, color="black")
    plt.title(image_name + " Layers bottom boundaries (um)")
    plt.xlabel("X cells' coordinates (um)")
    plt.ylabel("Cells distance from Layer1 top coordinate (um)")
    if visualisation_flag:
        plt.show()
    else:
        file_path = output_path + "/" + image_name + ".svg"
        plt.savefig(file_path, dpi=150)
    plt.clf()


def plot_layer_per_image(
    dataframe, layers_name, image_name, output_path, visualisation_flag
):
    plt.figure(figsize=(8, 8))
    for layer_name in layers_name:
        layer_df = (
            dataframe[dataframe["Layer"] == layer_name]
            .groupby(["image", "Layer"], as_index=False)[
                "Layer bottom (um). Origin is top of layer 1"
            ]
            .mean()
        )
        positions = layer_df["Layer bottom (um). Origin is top of layer 1"]
        layer_animal = layer_df["image"]
        plt.scatter(layer_animal, positions, label=layer_name, s=100)
    plt.xlabel("image")
    plt.xticks(rotation=90)
    plt.ylabel("Layer bottom. Origin is top of " + layer_name + " (um)")
    plt.gca().legend()
    plt.gca().set_title("Layer boundaries by input image")
    if visualisation_flag:
        plt.show()
    else:
        file_path = output_path + "/" + image_name + "layer_per_image_.svg"
        plt.savefig(file_path, dpi=150)
    plt.clf()


def plot_layer_per_animal(
    dataframe, layers_name, image_name, output_path, visualisation_flag
):
    plt.figure(figsize=(8, 8))
    for layer_name in layers_name:
        layer_df = (
            dataframe[dataframe["Layer"] == layer_name]
            .groupby(["animal", "Layer"], as_index=False)[
                "Layer bottom (um). Origin is top of layer 1"
            ]
            .mean()
        )
        positions = layer_df["Layer bottom (um). Origin is top of layer 1"]
        layer_animal = layer_df["animal"]
        plt.scatter(layer_animal, positions, label=layer_name, s=100)
        plt.xlabel("Animal id")
        plt.xticks(rotation=90)
        plt.ylabel("Layer bottom. Origin is top of " + layer_name + " (um)")
        plt.gca().legend()
    plt.gca().set_title("Layer boundaries by input animal")
    if visualisation_flag:
        plt.show()
    else:
        file_path = output_path + "/" + image_name + "layer_per_animal_.svg"
        plt.savefig(file_path, dpi=150)
    plt.clf()


def plot_densities_by_layer(layers, layers_densities, image_name, output_path, visualisation_flag=False):
        y_pos = np.arange(len(layers))
        plt.barh(y_pos, layers_densities,  align='center')
        plt.gca().set_yticks(y_pos, labels=layers)
        plt.title(image_name + " Cells density by layers (nb cell / mm3)")
        plt.gca().invert_yaxis()
        if visualisation_flag:
            plt.show()
        else:
            file_path = output_path + "/" + image_name + "_densities_by_layer.svg"
            plt.savefig(file_path, dpi=150)
        plt.clf()



def plot_layers(cells_pos_list, polygons, image_name, alpha, output_path, visualisation_flag=False):
    colors = get_layer_colors(polygons)
    for cells_pos, polygon, color in zip(cells_pos_list, polygons, colors):
        plt.scatter(cells_pos[:, 0], cells_pos[:, 1], s=1, color=color)
        x, y = polygon.exterior.xy
        plt.plot(x, y, color=color)
    plt.title(f'{image_name} Layer polygon for alpha={alpha}')
    plt.gca().invert_yaxis()
    if visualisation_flag:
        plt.show()
    else:
        file_path = output_path + "/" + image_name + "_layer_from_points.svg"
        plt.savefig(file_path, dpi=150)
    plt.clf()
