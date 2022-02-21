// To be executed on QuPath project that contains Rat Nissl microscopy images.
// Sript steps:
//   - Create the OutOfPia annotation
//   - Detect cells with cellpose
//   - Add features (distance, Delaunay and smooth)
//   - Export cells measurements (including cell feature) and QuPath annotations 




def saveFolderPath =  this.args[0]
logger.info("Save folder: {}", saveFolderPath)

def saveFolder = new File(saveFolderPath)


// Workaroud on Linux, the cellpose conf must be force by reseting it
def defaultEnvType = EnvType.VENV // or EnvType.VENV
def defaultVersion = CellposeVersion.OMNIPOSE // or CellposeVersion.CELLPOSE
def defaultEnvPath = "/home/jacquemi/working_dir/Rat_sscx_nissl/Venv_install/env-cellpose-py38"

 // Get an instance of the cellpose options
CellposeSetup options = CellposeSetup.getInstance();

//Set cellpose options to some fixed values (this does not change the qupath preferences values)
options.setEnvironmentType(defaultEnvType)
options.setVersion(defaultVersion)
options.setEnvironmentNameOrPath(defaultEnvPath)

logger.warn( "Currently set Environement Path: {}", options.getEnvironmentNameOrPath() )
logger.warn( "Currently set Environement Type: {}", options.getEnvironmentType() )
logger.warn( "Currently set Cellpose Version: {}", options.getVersion() )
logger.warn( "=====================================\n" )



// Expand S1HL Annotation tp crete Outside Pia
selectObjectsByPathClass( getPathClass( "S1HL" ) )
runPlugin('qupath.lib.plugins.objects.DilateAnnotationPlugin', '{"radiusMicrons": 200.0,  "lineCap": "Round",  "removeInterior": false,  "constrainToParent": false}');

// Pick up the dilated annotation, which is the one with the same class but largest area
def s1hl = getAnnotationObjects().findAll{ it.getPathClass() == getPathClass("S1HL") }.max{ it.getROI().getArea() }

// Pick up the SliceContour to subtract it from the dilated S1HL
def sliceC = getAnnotationObjects().find{ it.getPathClass() == getPathClass( "SliceContour" ) }

// Do some sexy geometry
def outPiaROI = RoiTools.combineROIs( s1hl.getROI(), sliceC.getROI(), RoiTools.CombineOp.SUBTRACT )

// Create the Outside Pia Annotation
def outPia = PathObjects.createAnnotationObject(outPiaROI, getPathClass( "Outside Pia" ) )
addObject( outPia )

// Delete original dilated S1HL
removeObject(s1hl, true)

// Cleanup and show
resetSelection()
fireHierarchyUpdate()



def pathModel = '/home/jacquemi/working_dir/Rat_sscx_nissl/rat_sscx_nissl_analysis/CellposeModel/cellpose_residual_on_style_on_concatenation_off_train_2022_01_11_16_14_20.764792'

// Model trained on full size image, with cyto2 model as base for 1200 epochs
def cellpose = Cellpose2D.builder(pathModel)
        .pixelSize(0.3460)
        .tileSize(2048)
        .diameter(30)                // Average diameter of objects in px (at the requested pixel sie)
        .measureShape()              // Add shape measurements
        .measureIntensity()          // Add cell measurements (in all compartments)
        .classify("Cellpose Julie Full")
        .build()

// Run detection for the selected objects
def imageData = getCurrentImageData()

def pathObjects = getObjects{ it.getPathClass().equals( getPathClass( "S1HL" ) ) }

println "Execute cellpose on $pathObjects"
println "imageData $imageData"
cellpose.detectObjects(imageData, pathObjects)

println 'INFO: Done: Cellpose algorithm for cellular segmentation'

// Add features for classifer and run it
detectionToAnnotationDistances(true)
selectAnnotations()
runPlugin('qupath.opencv.features.DelaunayClusteringPlugin', '{"distanceThresholdMicrons": 0.0,  "limitByClass": false,  "addClusterMeasurements": true}')
runPlugin('qupath.lib.plugins.objects.SmoothFeaturesPlugin', '{"fwhmMicrons": 50.0,  "smoothWithinClasses": false}')

println 'INFO: Done: Add cells features'


// Save Detection Measurements, keeping useful lines from `save_detection_measurement.groovy`
setImageType('BRIGHTFIELD_OTHER');
setColorDeconvolutionStains('{"Name" : "H-DAB default", "Stain 1" : "Hematoxylin", "Values 1" : "0.65111 0.70119 0.29049", "Stain 2" : "DAB", "Values 2" : "0.26917 0.56824 0.77759", "Background" : " 255 255 255"}');
resetSelection();
createAnnotationsFromPixelClassifier("CountourFinder", 1000000.0, 1000000.0)
runPlugin('qupath.lib.plugins.objects.SplitAnnotationsPlugin', '{}')
saveDetectionMeasurements( saveFolder.getAbsolutePath() )

// 2. Save annotations to folder from 'export_annotations_for_pipeline'
def annotations = getAnnotationObjects()
def writer = new WKTWriter()
def gson = GsonTools.getInstance(true)
// Pick up current image name to append to the resulting files
def imageName = getCurrentServer().getMetadata().getName()

def file = new File(saveFolder,imageName + '_annotations.json' )
annotations.each {
    //println writer.write( it.getROI().getGeometry() )
    writer.write( it.getROI().getGeometry() )
    file.withWriter('UTF-8') {
        gson.toJson( annotations,it )
    }
}

println('Export and save Detection Measurements and annotations Done')

// Imports
import qupath.ext.biop.cellpose.Cellpose2D
import qupath.ext.biop.cmd.VirtualEnvironmentRunner.EnvType;
import qupath.ext.biop.cellpose.CellposeSetup.CellposeVersion;
import qupath.ext.biop.cellpose.CellposeSetup
import org.locationtech.jts.io.WKTWriter
import org.slf4j.LoggerFactory;

