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
        , "Layer 2": "#0f00f0"
        , "Layer 3": "#0000ff"
        , "Layer 2/3": "#ffff00"
        , "Layer 4": "#f0f0f0"
        , "Layer 5": "#00f5ff"
        , "Layer 6 a": "#0ffff0"
        , "Layer 6 b": "#00ff00"
                    }

@click.command()
@click.option("--qupath-project-path", required=True, help="QuPath project file path (*.qpproj)")
@click.option("--ml-prediction-file-path", required=True, help="Machine Leraning prediction file")
@click.option("--image-name", type=str, required=True,  help="QuPath image Name")
@click.option("--pixel-size", required=False, default=0.3460130331522824,
              type=float, help="QuPath image pixel size")
@click.option("--visualisation-flag", required=False, is_flag=True)

def superpose_boundary(qupath_project_path, ml_prediction_file_path,
                       image_name, pixel_size, visualisation_flag):

    ml_result = pd.read_csv(ml_prediction_file_path)
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

