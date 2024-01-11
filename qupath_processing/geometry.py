"""
Geometry module that contains geometric functions
"""

from math import sqrt
import numpy as np
from shapely.geometry import Point, LineString, Polygon, MultiLineString, shape
from shapely.ops import split
from qupath_processing.utilities import NotValidImage


def distance(pt1, pt2):
    """
    Return the euclidian distance from two 2D points
    :param pt1:  np.array of shape (2,): X,Y coordinates
    :param pt2:  np.array of shape (2,): X,Y coordinates
    :return:  float : The euclidian distance  form p1 to p2

    """
    return sqrt((pt1[0] - pt2[0]) ** 2 + (pt1[1] - pt2[1]) ** 2)


def get_extrapoled_segement(segment_endpoints_coordinates, extrapol_ratio=1.5):
    """
    Extrapolates a segment in both directions of extrapol_ratio ratio
    :param segment_endpoints_coordinates:(np.array) of shape(2, 2): coordinates of the segment's
     endpoints
    :param extrapol_ratio: Ratio used to extrapolate the segment endpoints coordianates
    :return: (np.array) of shape(2, 2) the extrapolated segment's endpoints
    """
    pt1 = segment_endpoints_coordinates[0]
    pt2 = segment_endpoints_coordinates[1]
    new_pt1 = (
        pt2[0] + extrapol_ratio * (pt1[0] - pt2[0]),
        pt2[1] + extrapol_ratio * (pt1[1] - pt2[1]),
    )
    new_pt2 = (
        pt1[0] + extrapol_ratio * (pt2[0] - pt1[0]),
        pt1[1] + extrapol_ratio * (pt2[1] - pt1[1]),
    )
    return np.array([new_pt1, new_pt2])


def create_grid(quadrilateral, s1_coordinates, nb_row, nb_col):
    """
    Create a grid on a polygon defined by s1_coordinates.
    - The vertical lines are straight. There endpoints coordinates are computed from the
         quadrilateral top and bottom
     lines in order to split them in a regular way.
    - The horizontal "lines" are composed of several segments that "follow" the quadrilateral
         top and bottom
     lines shape to represent the brain's depth

    :param quadrilateral:(np.array) of shape(5, 2) containing the following points coordinates(mm)
                        direction:top_left, top_right, bottom_right, bottom_left, top_left
    :param s1_coordinates:(np.array) shape (nb_vertices, 2) containing S1 polygon coordinates (mm)
    :param nb_row:(int) grid number of rows
    :param nb_col:(int) grid number of columns
    :return: tuple:
        - list of horizontal LineString that defined the grid

    """
    vertical_lines = vertical_line_splitter(quadrilateral, s1_coordinates, nb_col)
    return horizontal_line_splitter(vertical_lines, nb_row), vertical_lines


def vertical_line_splitter(quadrilateral, s1_coordinates, nb_col):
    """
    Create some vertical lined on a polygon defined by s1_coordinates.
    - The vertical lines are straight. There endpoints coordinates are computed from the
     quadrilateral top and bottom
     lines in order to split them in a regular way.

    :param quadrilateral:(np.array) shape(5, 2) containing the following points coordinates(mm)
                        in clockwise direction: top_left, top_right, bottom_right, bottom_left,
                        top_left
    :param s1_coordinates:(np.array) of shape (nb_vertices, 2) containing S1 polygon coordinates
                          (mm)
    :param nb_col:(int) number of columns

    :return  list of vertical LineString
    """
    top_left = quadrilateral[0]
    top_right = quadrilateral[1]
    bottom_right = quadrilateral[2]
    bottom_left = quadrilateral[3]
    # Vertical lines
    vertical_lines = [
        LineString(
            [[top_left[0] - 2000, top_left[1]], [bottom_left[0] - 2000, bottom_left[1]]]
        )
    ]
    for i in range(nb_col - 1):
        top_point = top_left + (top_right - top_left) / nb_col * (i + 1)
        bottom_point = bottom_left + (bottom_right - bottom_left) / nb_col * (i + 1)
        line_coordinates = get_extrapoled_segement(
            [(top_point[0], top_point[1]), (bottom_point[0], bottom_point[1])], 1.3
        )
        intersection_line = LineString(line_coordinates).intersection(
            Polygon(s1_coordinates)
        )
        if isinstance(intersection_line, MultiLineString):
            for line in intersection_line.geoms:
                vertical_lines.append(line)
                break
        else:
            vertical_lines.append(intersection_line)
        """
        try:
            intersection_line = \
                Polygon(s1_coordinates).intersection(LineString(line_coordinates)).coords
            vertical_lines.append(intersection_line)

        except NotImplementedError:
            print('WARNING: A VerticalLine on {} not created'.format(nb_col))
            '''
             In some case, several point of S1 intersect with the LineString and produce
             shapely NotImplementedError error. In this case, we just de not create the
             corresponding vertical line. If the number of row is important (~100). This will
             not change the result a lot. Just the "shape" of corresponding polygon will be average
             from prev and next VerticalLine
            '''
        """
    vertical_lines.append(
        LineString(
            [
                [top_right[0] + 2000, top_right[1]],
                [bottom_right[0] + 2000, bottom_right[1]],
            ]
        )
    )
    return vertical_lines


def horizontal_line_splitter(vertical_lines, nb_row):
    """
    Create a grid on a polygon defined by s1_coordinates.
    - The vertical lines are straight. There endpoints coordinates are computed from the
          quadrilateral top and bottom
     lines in order to split them in a regular way.
    - The horizontal "lines" are composed of several segments that "follow" the quadrilateral
          top and bottom
     lines shape to represent the brain's depth

    :param vertical_lines: list of vertical LineString that defined the grid
    :param nb_row:(int) grid number of rows
    :return list of horizontal LineString
    """
    horizontal_lines = []
    for i in range(nb_row - 1):
        horizontal_points = []
        for line in vertical_lines:
            line_coords = np.array(line.coords)
            point = line_coords[0] + (line_coords[1] - line_coords[0]) / nb_row * (
                i + 1
            )
            horizontal_points.append(point)

        horizontal_line = LineString(horizontal_points)
        horizontal_lines.append(horizontal_line)
    return horizontal_lines


def create_depth_polygons(s1_coordinates, horizontal_lines):
    """
    Create shapely polygon defined by horizontal lines and the polygon defined
     by s1_coordinates
    :param s1_coordinates:(np.array) of shape (nb_vertices, 2) containing
                          S1 polygon coordinates (mm)
    :param horizontal_lines: list of horizontal LineString that defined the grid
    :return: list of shapely polygons representing S1 layers as fonction
             if brain depth
    """
    # try:
    split_polygons = []
    polygon_to_split = Polygon(s1_coordinates)
    for line in horizontal_lines:
        split_result = split(polygon_to_split, line).geoms
        try:
            polygon_to_split = split_result[1]
            split_polygons.append(split_result[0])
        except IndexError:
            pass

    split_polygons.append(polygon_to_split)
    return split_polygons
    # except IndexError:
    # raise NotValidImage


def count_nb_cell_per_polygon(cells_centroid_x, cells_centroid_y, split_polygons):
    """
    Count the number of cells located inside each polygon of split_polygons list
    :param cells_centroid_x:np.array of shape (number of cells, ) of type float
    :param cells_centroid_y:np.array of shape (number of cells, ) of type float
    :param split_polygons:list of shapely polygons representing S1 layers as
                          function if brain depth
    :return: list of int:The number of cells located inside each polygons of
                         split_polygons
    """
    #print(f'DEBUG cells_centroid_x {cells_centroid_x}')
    #print(f'DEBUG cells_centroid_y {cells_centroid_y}')
    #for poly in split_polygons:
    #``    print(f'DEBUG poly {poly}')
    nb_cell_per_polygon = [0] * len(split_polygons)
    for x_coord, y_coord in zip(cells_centroid_x, cells_centroid_y):
        for index, polygon in enumerate(split_polygons):
            if polygon.contains(Point([x_coord, y_coord])):
                nb_cell_per_polygon[index] += 1
    return nb_cell_per_polygon


def compute_cells_depth(split_polygons, cells_centroid_x, cells_centroid_y):
    """
    Plot polygons and cells depth
    :param split_polygons: list of shapely polygons representing S1 layers as
                           function if brain depth
    :param cells_centroid_x: np.array of shape (number of cells, ) of type float
    :param cells_centroid_y: np.array of shape (number of cells, ) of type float
    """
    depthes = [-1] * len(cells_centroid_x)
    for cell_index, (x_coord, y_coord) in enumerate(
        zip(cells_centroid_x, cells_centroid_y)
    ):
        for index, polygon in enumerate(split_polygons):
            if polygon.contains(Point([x_coord, y_coord])):
                depthes[cell_index] = index
    return depthes
