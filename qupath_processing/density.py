"""
QuPath porcessing for rat somatosensory cortex Nissl data module
"""

import pandas as pd

from qupath_processing.geometry import (
    create_depth_polygons,
    create_grid,
    count_nb_cell_per_polygon,
)

from qupath_processing.visualisation import (
    plot_densities,
    plot_split_polygons_and_cell_depth,
)



# pylint: disable=too-many-arguments
# pylint: disable=too-many-locals

def single_image_process(
    cells_centroid_x, cells_centroid_y, s1_coordinates, quadrilateral_coordinates,
    thickness_cut, nb_row, nb_col, image_prefix, layers_name,
    excluded_cells_centroid_x=None, excluded_cells_centroid_y=None,
    layer_boundary_path=None,
    visualisation_flag=False, output_path=None,
):
    """
    :param cells_centroid_x:(np.array)
    :param cells_centroid_y:(np.array)
    :param s1_coordinates:(np.array)
    :param quadrilateral_coordinates:(np.array)
    :param thickness_cut:(float) um
    :param nb_row:(int)
    :param nb_col:(int)
    :param image_prefix(str)
    :param layers_name(list of str)
    :param layer_boundary_path:(str)
    :param visualisation_flag:(bool)
    :param output_path:(str)
    :return: densities_dataframe(pandas dataframe)

    """
    horizontal_lines, vertical_lines = create_grid(
        quadrilateral_coordinates, s1_coordinates, nb_row, nb_col
    )
    split_polygons = create_depth_polygons(s1_coordinates, horizontal_lines)
    print("INFO: Computes the cells densities as function of percentage depth")
    nb_cell_per_slide = count_nb_cell_per_polygon(
        cells_centroid_x, cells_centroid_y, split_polygons
    )

    depth_percentage, densities, nb_cells = compute_cell_density(
        nb_cell_per_slide, split_polygons, thickness_cut / 1e3
    )

    total_used_cells = sum(nb_cells)
    if total_used_cells != len(cells_centroid_x + excluded_cells_centroid_x):
        densities_dataframe = pd.DataFrame(
            {"image": [image_prefix], "depth_percentage": None, "densities": None}
        )
        print(
            f"ERROR there are  {len(cells_centroid_x + excluded_cells_centroid_x) - total_used_cells } \
                cells outside the grid for a total of {len(cells_centroid_x)} cells"
        )

    else:
        densities_dataframe = pd.DataFrame(
            {
                "image": [image_prefix] * len(depth_percentage),
                "depth_percentage": depth_percentage,
                "densities": densities,
            }
        )

        if layer_boundary_path:
            boundary_df = pd.read_pickle(layer_boundary_path)
            boundaries_percentage = list(
                boundary_df["Layer bottom (percentage). Origin is top of layer 1"]
            )
        else:
            boundaries_percentage = None

        plot_split_polygons_and_cell_depth(
            split_polygons,
            s1_coordinates,
            cells_centroid_x,
            cells_centroid_y,
            excluded_cells_centroid_x,
            excluded_cells_centroid_y,
            vertical_lines=vertical_lines,
            horizontal_lines=horizontal_lines,
            visualisation_flag=visualisation_flag,
            output_path=output_path,
            image_name=image_prefix,
        )

        plot_densities(
            depth_percentage,
            densities,
            layers_name,
            boundaries_percentage=boundaries_percentage,
            visualisation_flag=visualisation_flag,
            output_path=output_path,
            image_name=image_prefix,
        )
        '''
        def plot_densities(
    percentages,
    densities,
    layers_names,
    boundaries_percentage=None,
    visualisation_flag=None,
    output_path=None,
    image_name="",
):
    """
    Plot the density per layers that represent the brain depth
    :param percentages: list of brain depth percentage (float)
    :param layers_names: list of str
    :param densities:  list of float (nb cells / mm3)
    :param boundaries_percentage:
    :param image_name:
    """

    fig, ax = plt.subplots()
    if boundaries_percentage:
        boundaries_percentage.insert(0, 0)
        for layer_name, boundary_prev, boundary_next in zip(
            layers_names, boundaries_percentage[0:-1], boundaries_percentage[1:]
        ):
            center = int((boundary_next + boundary_prev) * 100 / 2)
            ax.axvline(boundary_prev * 100, color="red", markersize=2)
            ax.annotate(
                layer_name, xy=(center - 3, int(np.max(densities))), color="red"
            )

    ax.plot(densities, np.array(percentages) * 100)
    ax.set_xlabel("Cell density (cells/mm3)")
    ax.set_ylabel("percentage of depth (%)")
    ax.invert_yaxis()

    title = "Cell densities as function of percentage of depth"
    if image_name:
        title = image_name + " " + title
    ax.set_title(title)
    #x = np.array(percentages) * 100  # the label locations

    #ax.set_yticks(x, percentages)
    if visualisation_flag:
        plt.show()
    else:
        file_path = output_path + "/" + image_name + "layer_per_animal_.png"
        plt.savefig(file_path, dpi=150)


def plot_split_polygons_and_cell_depth(
    split_polygons,
    s1_coordinates,
    cells_centroid_x,
    cells_centroid_y,
    excluded_cells_centroid_x=None,
    excluded_cells_centroid_y=None,
    vertical_lines=None,
    horizontal_lines=None,
    visualisation_flag=False,
    output_path=None,
    image_name=None,
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
        x_coord, y_coord = polygon.exterior.xy
        #plt.plot(x_coord, y_coord, c='black')
    plt.plot(s1_coordinates[:, 0], s1_coordinates[:, 1], "r")
    plt.scatter(cells_centroid_x, cells_centroid_y, c='blue', s=1, alpha=.5, label='preserved cells')
    if excluded_cells_centroid_x is not None and excluded_cells_centroid_y is not None:
        plt.scatter(excluded_cells_centroid_x, excluded_cells_centroid_y, c='red', s=1, label='exluded cells')
    if vertical_lines:
        for line in vertical_lines:
            line = line.coords
            plt.axline((line[0][0], line[0][1]), (line[1][0], line[1][1]), linewidth=1, color="black")
    if horizontal_lines:
        for line in horizontal_lines:
            line = line.coords
            plt.axline((line[0][0], line[0][1]), (line[1][0], line[1][1]), linewidth=1, color="black")
    plt.title(
        "Somatosensory cortex. Each layer represents a percentage of depth following the top of the SSX"
    )
    plt.xlabel("X coordinates (um)")
    plt.ylabel("Y coordinates (um)")
    plt.legend()
    if visualisation_flag:
        plt.show()

    file_path = output_path + "/" + image_name + "layer_per_animal_.svg"
    print(f'plt.savefig {file_path}')
    plt.savefig(file_path)



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
        file_path = output_path + "/" + image_name + ".png"
        plt.savefig(file_path, dpi=150)


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
        file_path = output_path + "/" + image_name + "layer_per_image_.png"
        plt.savefig(file_path, dpi=150)


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
        file_path = output_path + "/" + image_name + "layer_per_animal_.png"
        plt.savefig(file_path, dpi=150)

        '''
    return densities_dataframe


def compute_cell_density(nb_cell_per_slide, split_polygons, z_length):
    """
    Computes density as function of brain percentage of depth
    :param nb_cell_per_slide: list of int
    :param split_polygons:list of shapely polygons representing S1 layers as function if brain depth
    :param z_length: float ( thickness of the cut over z axis (mm)
    :return: tuple:
        -  depth_percentage: list of float representing the percentage of brain depth
        -  densities: list of float representing the number of cell by mm3
    """
    nb_cells = []
    densities = []

    for nb_cell, polygon in zip(nb_cell_per_slide, split_polygons):
        nb_cells.append(nb_cell)
        densities.append(nb_cell / ((polygon.area / 1e6) * z_length))

    depth_percentage = [i / len(split_polygons) for i in range(len(split_polygons))]

    return depth_percentage, densities, nb_cells
