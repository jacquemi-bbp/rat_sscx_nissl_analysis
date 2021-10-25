# Processing for rat somatosensory cortex QuPath Nissl data 

## General idea
EPFL LNMC laboratory provides some rat somatosensory cortex Nissl microscopy images.
From these images and some QuPath annotations, this qupath_processing python package generates
 cells densities as a function of the percentage of depth inside the somatosensory cortex.


# Lexicon
The following definitions will stay in effect throughout the code.
-S1 annotation: S1 annotation in QuPath that defines the rat somatosensory cortex

#  Input Data
## Input data for single image processing
- cell position file:  created with the groovy saveDetectionMeasurements command
- annotations file:
    1. top_left, top_right, bottom_left and bottom_right annotation points
    2. S1 polygon annotation
- pixel size file:  a single text file with a float number that represents the pixel size

# Processing Steps
- Convert annotations to cartesian point coordinates and shapely polygon.
- Split the S1 polygon following the S1 "top and bottom lines" shapes in n polygons (named spitted_polygon)
- Count the number of cells located in each spitted_polygon
- Compute the volume of each spitted_polygon (mm3)
- Compute the cells densities as function of the percentage of the sscx depth
- Write result files

## Installation

```shell
$ git clone ssh://bbpcode.epfl.ch/molecularsystems/qupath_processing
$ cd qupath_processing
$ pip install .


```
### Third parties 
python third parties libraries are installed during package installation.
see requirements.txt

# Run the batch processing
```shell
$ pyqupath_batch_processing --config-file-path ./Config/batch_config.ini 
```

# Documentation
[Online Documentation]()

### Integration test
