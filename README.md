# Processing for rat somatosensory cortex  QuPath Nissl data [![pipeline status](https://bbpgitlab.epfl.ch/molsys/skeletonizer/badges/main/pipeline.svg)](https://bbpgitlab.epfl.ch/molsys/qupath_processing/-/commits/main) [![coverage report](https://bbpgitlab.epfl.ch/molsys/qupath_processing/badges/main/coverage.svg)](https://bbpgitlab.epfl.ch/molsys/qupath_processing/-/commits/main)

## General idea
EPFL LNMC laboratory provided some rat somatosensory cortex Nissl microscopy images
and QuPath project with image annotations
This qupath_processing python package allows to generates densities as function
 of percentage of sscx depth from QuPath data.

# Lexicon
The following definitions will stay in effect throughout the code.
-S1 annotation: S1 annotation in QuPath that defines rat sscx

#  Input Data
## Input data for single image processing
- cell position file 
- annotations  file
- pixel size file 

# Processing Steps
- Convert annotations to cartesian coordinates and shapely polygon.
- Split the S1 polygon following the S1 shape in n row (names spitted_polygon)
- Count the number of cells located in each spitted_polygon
- Compute the volume of each spitted_polygon (mm3)
- Compute the densities as function of percentage of sscx depth
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
