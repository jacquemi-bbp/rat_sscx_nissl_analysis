"""
Geometry module that contains geometric functions
"""

from math import sqrt
import numpy as np
from shapely.geometry import Point, LineString, Polygon
from shapely.ops import split

def distance(p1, p2):
    """
    Return the euclidian distance from two 2D points
    :param p1:  np.array of shape (2,): X,Y coordinates
    :param p2:  np.array of shape (2,): X,Y coordinates
    :return: 
        float : The euclidian distance  form p1 to p2
    """
    return sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)


def get_extrapoled_segement(segment_endpoints_coordinates, extrapol_ratio=1.5):
    """
    Extrapolates a segment in both directions of extrapol_ratio ratio
    :param segment_endpoints_coordinates:(np.array) of shape(2, 2): coordinates of the segment's endpoints
    :param extrapol_ratio: Ratio used to extrapolate the segment endpoints coordianates
    :return: (np.array) of shape(2, 2) the extrapolated segment's endpoints
    """
    p1=segment_endpoints_coordinates[0]
    p2=segment_endpoints_coordinates[1]
    a = (p2[0]+extrapol_ratio*(p1[0]-p2[0]), p2[1]+extrapol_ratio*(p1[1]-p2[1]))
    b = (p1[0]+extrapol_ratio*(p2[0]-p1[0]), p1[1]+extrapol_ratio*(p2[1]-p1[1]))
    return np.array([a, b])


def create_grid(quadrilateral, s1_coordinates, nb_row, nb_col):
    """
    Create of grid on a polygon defined by s1_coordinates.
    - The vertical lines are straight. There endpoints coordinates are computed from the quadrilateral top and bottom
     lines in order to split them in a regular way.
    - The horizontal "lines" are composed of several segments that "follow" the quadrilateral top and bottom
     lines shape to represent the brain's depth

    :param quadrilateral:(np.array) of shape(5, 2) containing the following points coordinates(mm)
                        in clockwise direction: top_left, top_right, bottom_right, bottom_left, top_left
    :param s1_coordinates:(np.array) of shape (nb_vertices, 2) containing S1 polygon coordinates (mm)
    :param nb_row:(int) grid number of rows
    :param nb_col:(int) grid number of columns
    :return: tuple:
        - list of vertical LineString that defined the grid
        - list of horizontal LineString that defined the grid

    """
    top_left = quadrilateral[0]
    top_right = quadrilateral[1]
    bottom_right = quadrilateral[2]
    bottom_left = quadrilateral[3]
    # Vertical lines
    vertical_lines = [LineString([[top_left[0] - 10, top_left[1]], [bottom_left[0] - 10, bottom_left[1]]])]
    for i in range(nb_col - 1):
        top_point = top_left + (top_right - top_left) / nb_col * (i + 1)
        bottom_point = bottom_left + (bottom_right - bottom_left) / nb_col * (i + 1)
        #line = LineString([(top_point[0], top_point[1]), (bottom_point[0], bottom_point[1])])
        line_coordinates = get_extrapoled_segement([(top_point[0], top_point[1]), (bottom_point[0], bottom_point[1])], 1.3)
        intersection_line = Polygon(s1_coordinates).intersection(LineString(line_coordinates)).coords
        vertical_lines.append(intersection_line)
    vertical_lines.append(LineString([top_right, bottom_right]))

    # Horizontal lines
    horizontal_lines = []
    for i in range(nb_row - 1):
        horizontal_points = []
        for index, line in enumerate(vertical_lines):
            line_coord = np.array(line)
            point = line_coord[0] + (line_coord[1] - line_coord[0]) / nb_row * (i + 1)
            horizontal_points.append(point)
        horizontal_line = LineString(horizontal_points)
        horizontal_lines.append(horizontal_line)

    return vertical_lines, horizontal_lines


def create_depth_polygons(s1_coordinates, horizontal_lines):
    """
    Create shapely polygon defined by horizontal lines and the polygon defined by s1_coordinates
    :param s1_coordinates:(np.array) of shape (nb_vertices, 2) containing S1 polygon coordinates (mm)
    :param horizontal_lines: list of horizontal LineString that defined the grid
    :return: list of shapely polygons representing S1 layers as fonction if brain depth
    """
    split_polygons = []
    polygon_to_split = Polygon(s1_coordinates)
    for line in horizontal_lines:
        split_result = split(polygon_to_split, line)

        polygon_to_split = split_result[1]
        split_polygons.append(split_result[0])

    split_polygons.append(polygon_to_split)
    return split_polygons


def count_nb_cell_per_polygon(cells_centroid_x, cells_centroid_y, split_polygons):
    """
    Count the number of cells located inside each polygons of split_polygons list
    :param cells_centroid_x:np.array of shape (number of cells, ) of type float
    :param cells_centroid_y:np.array of shape (number of cells, ) of type float
    :param split_polygons:list of shapely polygons representing S1 layers as function if brain depth
    :return: list of int: The number of cells located inside each polygons of split_polygons
    """
    nb_cell_per_polygon = [0] * len(split_polygons)
    for x, y in zip (cells_centroid_x, cells_centroid_y):
        for index, polygon in enumerate(split_polygons):
            if polygon.contains(Point([x,y])):
                nb_cell_per_polygon[index]+=1
    return nb_cell_per_polygon


def compute_cells_depth(split_polygons, cells_centroid_x, cells_centroid_y):
    """
    Plot polygons and cells depth
    :param split_polygons: list of shapely polygons representing S1 layers as function if brain depth
    :param cells_centroid_x: np.array of shape (number of cells, ) of type float
    :param cells_centroid_y: np.array of shape (number of cells, ) of type float
    """
    depthes = [-1] * len(cells_centroid_x)
    for cell_index, (x, y) in enumerate(zip(cells_centroid_x, cells_centroid_y)):
        for index, polygon in enumerate(split_polygons):
            if polygon.contains(Point([x, y])):
                depthes[cell_index] = index
    return depthes