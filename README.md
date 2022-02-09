# Processing for rat somatosensory cortex QuPath Nissl data 

## General idea
EPFL LNMC laboratory provides some rat somatosensory cortex Nissl microscopy images.
From these images and some QuPath annotations, this package can generate: 
  - cells densities as a function of the percentage of depth inside the somatosensory cortex.
  - Layers bottom boundaries (um) . The bottom of each layer since it's assumed that Layers 1 starts at 0.


<img src="Doc/layer_boundaries.png" alt="Doc/layer_boundaries.png" width="400"/>
<img src="Doc/percentage_grid.png" alt="Doc/percentage_grid.png" width="400"/>
<img src="Doc/percentage_of_depth.png" alt="Doc/percentage_of_depth.png" width="400"/>

# The pipeline consists of two main steps:
1. (groovy + QuPath) Cells detection, export annotations, and cells coordinates
2. (python) Processing for rat somatosensory cortex QuPath Nissl data
 
# Lexicon
The following definitions will stay in effect throughout the code.
-S1 annotation: S1 annotation in QuPath that defines the rat somatosensory cortex

# Processing Steps
- Convert annotations to cartesian point coordinates and shapely polygon.
- Split the S1 polygon following the S1 "top and bottom lines" shapes in n polygons (named spitted_polygon)
- Count the number of cells located in each spitted_polygon
- Compute the volume of each spitted_polygon (mm3)
- Compute the cells densities as function of the percentage of the sscx depth
- Write result files

## Installation
- QuPath: https://qupath.github.io/
- Python library
```shell
$ git clone ssh://bbpcode.epfl.ch/molecularsystems/qupath_processing
$ cd qupath_processing
$ pip install .

```
### Third parties 
- python third parties libraries are installed during package installation.
see requirements.txt
- QuPath v0.3.0
- QuPath qupath-extension-stardist-0.3.0.jar and qupath-extension-tensorflow-0.3.0.jar extensions

#  Input data
## Input data for groovy script
- QuPath project including the images to process and these 5 annotations: S1, top_left, top_right, bottom_left and bottom_right 
- StartDist model used in StarDist_Export_Detections_Annotations.groovy script to detect cells
## Input data for python single image processing
- The date bellow is generated by the Groovy_scprits/StarDist_Export_Detections_Annotations.groovy script
- cell position file:  created with the groovy saveDetectionMeasurements command
- annotations file:
1. top_left, top_right, bottom_left and bottom_right annotation points
2. S1 polygon annotation
- pixel size file:  a single text file with a float number that represents the pixel size


# Run the batch processing
- modify ./Config/batch_config.ini with your configuration
- execute the python script
```shell
$ pyqupath_processing batch_density --config-file-path ./Config/batch_config.ini 
```
