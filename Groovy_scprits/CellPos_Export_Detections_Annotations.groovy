import qupath.ext.biop.cellpose.Cellpose2D

def saveFolderPath =  this.args[0]
logger.info("Save folder: {}", saveFolderPath)

def saveFolder = new File(saveFolderPath)

def pathModel = '/home/jacquemi/working_dir/Rat_sscx_nissl/ProjectQuPath_1443459_RH_Nissl_4_v0.3.0/models/cellpose_residual_on_style_on_concatenation_off_train_2021_12_13_11_14_32.300178' 

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

def pathObjects = getObjects{ it.getPathClass().equals( getPathClass( "S1" ) ) }
//if (pathObjects.isEmpty()) {
//    Dialogs.showErrorMessage("Cellpose", "Please select a parent object!")
//}
println "Execute cellpose on $pathObjects"
println "imageData $imageData"
cellpose.detectObjects(imageData, pathObjects)

println 'Done!'


    
getDetectionObjects().each{ it.setPathClass( getPathClass("CellPose") ) }

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

println('Done')

// Imports
import org.locationtech.jts.io.WKTWriter
import org.slf4j.LoggerFactory;

