import qupath.ext.biop.cellpose.Cellpose2D

def saveFolderPath =  this.args[0]
logger.info("Save folder: {}", saveFolderPath)

def saveFolder = new File(saveFolderPath)



// Expand S1HL Annotation
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


// Create needed annotation for the Object Classifier
def layers = [ "Layer 1",
               "Layer 2",
               "Layer 3",
               "Layer 4",
               "Layer 5",
               "Layer 6 a",
               "Layer 6 b",
               "Outside Pia",
               "S1HL",
               "SliceContour"
              ]

def colors = rainbowPower( layers.size() )



def available = getQuPath().getAvailablePathClasses()

def pathClasses = [layers, colors].transpose().collect{ name, color ->
    def newClass = PathClassFactory.getPathClass(name)
    newClass.setColor(color)
    return newClass
}
Platform.runLater{
    getQuPath().resetAvailablePathClasses()
    available.addAll( pathClasses )
}


def rainbowPower(int n) {
    return (1..n).collect{ i -> Color.HSBtoRGB( (1.0/n)*i, 1.0f, 1.0f) }
}
println 'Add annotations Done !'



def pathModel = '/Users/jacquemi/working_dir/Rat_Nissl/QuPathProject/Cellpose_Training_20211227_v2/Cellpose-Models/cellpose_residual_on_style_on_concatenation_off_train_2021_10_28_14_00_38.096441' 

//def pathModel = '/Users/jacquemi/working_dir/Molcular_systems/Rat_sscx_nissl/QuPath/ProjectQuPath_1443459_RH_Nissl_4_v0.3.0/models/cellpose_residual_on_style_on_concatenation_off_train_2021_12_13_11_14_32.300178'

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
//if (pathObjects.isEmpty()) {
//    Dialogs.showErrorMessage("Cellpose", "Please select a parent object!")
//}
println "Execute cellpose on $pathObjects"
println "imageData $imageData"
cellpose.detectObjects(imageData, pathObjects)

println 'Cellpose algorithm for cellular segmentation Done!'
// CIRCULARITY CORRECTION START

// Run this code after cellpose

def cells = getDetectionObjects()

def multis = cells.findAll{ it.getROI().getGeometry() instanceof org.locationtech.jts.geom.MultiPolygon }

// fix
def fixedMultis = multis.collect{ cell ->
    def geom = cell.getROI().getGeometry()
    // Get the largest geometry and assume that it is the cell
    def idx = (0..< geom.getNumGeometries()).max{ geom.getGeometryN( it ).getArea() }

    def newROI = GeometryTools.geometryToROI( geom.getGeometryN( idx ), null )
    def newcell = PathObjects.createDetectionObject( newROI, cell.getPathClass(), cell.getMeasurementList() )
}

// Add what is needed and remove the old ones
removeObjects( multis, false )
addObjects( fixedMultis )
fireHierarchyUpdate()

// Re-compute measurements
selectDetections()
addShapeMeasurements("AREA", "LENGTH", "CIRCULARITY", "SOLIDITY", "MAX_DIAMETER", "MIN_DIAMETER", "NUCLEUS_CELL_RATIO")
// CIRCULARY CORRECTION END


// Add features for classifer and run it
detectionToAnnotationDistances(true)
selectAnnotations()
runPlugin('qupath.opencv.features.DelaunayClusteringPlugin', '{"distanceThresholdMicrons": 0.0,  "limitByClass": false,  "addClusterMeasurements": true}')
runPlugin('qupath.lib.plugins.objects.SmoothFeaturesPlugin', '{"fwhmMicrons": 25.0,  "smoothWithinClasses": false}')
runPlugin('qupath.lib.plugins.objects.SmoothFeaturesPlugin', '{"fwhmMicrons": 50.0,  "smoothWithinClasses": false}')
runObjectClassifier("Layer Classiffier")

println 'Add features for classifer and run it Done!'

    
//getDetectionObjects().each{ it.setPathClass( getPathClass("CellPose") ) }

// 1. Save Detection Measurements, keeping useful lines from `save_detection_measurement.groovy`
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
    println writer.write( it.getROI().getGeometry() )
    file.withWriter('UTF-8') {
        gson.toJson( annotations,it )
    }
}

println('Export and save Detection Measurements and annotations Done')

// Imports
import org.locationtech.jts.io.WKTWriter
import org.slf4j.LoggerFactory;

