import click

import pandas as pd
from paquo.projects import QuPathProject

from pathlib import Path
from paquo.projects import QuPathProject
from paquo.images import QuPathImageType
from paquo.classes import QuPathPathClass
from shapely.geometry import Point, Polygon, MultiPoint
import numpy as np
import matplotlib.pyplot as plt



layers_color = {"Layer 1": "#ff0000"
        , "Layer 2": "#ff0099"
        , "Layer 3": "#cc00ff"
        , "Layer 2/3": "#ff9900"
        , "Layer 4": "#ffcc00"
        , "Layer 5": "#ffcc99"
        , "Layer 6 a": "#ffcccc"
        , "Layer 6 b": "#ffff00"
                    }

@click.command()
@click.option("--qupath-project-path", required=True, help="QuPath project file path (*.qpproj)")
@click.option("--ml-prediction-file-path", required=True, help="Machine Learning prediction file")
@click.option("--image-name", type=str, required=False, default=None,
              help="If not set all the images inside the ML prediction files with be used")
@click.option("--pixel-size", required=False, default=0.3460130331522824,
              type=float, help="QuPath image pixel size")
@click.option("--visualisation-flag", required=False, is_flag=True)

def superpose_boundary(qupath_project_path, ml_prediction_file_path,
                       image_name, pixel_size, visualisation_flag):

    ml_result = pd.read_csv(ml_prediction_file_path)

    if image_name is None:
        image_names = np.unique(ml_result['Image'])
    else:
        image_names = [image_name]


    for image_name in image_names:
        ml_result = ml_result[ml_result['Image'] == image_name]


        annotations = []
        #for index, layer in enumerate(["Layer 1", "Layer 2", "Layer 3", "Layer 2/3",  "Layer 4", "Layer 5", "Layer 6 a", "Layer 6 b"]):
        for index, layer in enumerate(["Layer 1", "Layer 2", "Layer 3", "Layer 4", "Layer 5", "Layer 6 a", "Layer 6 b"]):
            layer_points = ml_result[ml_result['rf_prediction'] == layer][['Centroid X µm', 'Centroid Y µm']].to_numpy()
            layer_points = layer_points / pixel_size
            if layer_points.size > 0:
                annotations.append({layer: MultiPoint(layer_points)})

        with QuPathProject(qupath_project_path, mode='r+') as qp:
            print("--- INFO: read", qp.name)

            print(f'---INFO: there are {len(qp.images)}  images in this project')
            for image in qp.images:
                if image.image_name.find(image_name) > -1:
                    print(f'--- INFO: Found [{image.image_name}] ')
                    for index, annotation in enumerate(annotations):
                        for name, roi in annotation.items():
                            # add the annotations without a class set
                            path_class = QuPathPathClass(name='_' + name, color=layers_color[name])
                            image.hierarchy.add_annotation(roi=roi, path_class=path_class)
                    break

