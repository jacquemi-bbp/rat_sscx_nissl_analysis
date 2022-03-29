def saveFolderPath =  this.args[0]
logger.info("Save folder: {}", saveFolderPath)
def saveFolder = new File(saveFolderPath)


// Add features for classifer and run it
detectionToAnnotationDistances(true)
//runObjectClassifier("/home/jacquemi/working_dir/Rat_sscx_nissl/Cellpose_Classifier_Training_20220225/classifiers/object_classifiers/classify_by_layer_only.json")
runObjectClassifier("./Classifyers/classify_by_layer_only_with_L23.json")
println 'Add features for classifer and run it Done!'
selectAnnotations();
runPlugin('qupath.opencv.features.DelaunayClusteringPlugin', '{"distanceThresholdMicrons": 0.0,  "limitByClass": false,  "addClusterMeasurements": false}');
runPlugin('qupath.lib.plugins.objects.SmoothFeaturesPlugin', '{"fwhmMicrons": 25.0,  "smoothWithinClasses": false}');
runPlugin('qupath.lib.plugins.objects.SmoothFeaturesPlugin', '{"fwhmMicrons": 50.0,  "smoothWithinClasses": false}');

    
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
    writer.write( it.getROI().getGeometry() )
    file.withWriter('UTF-8') {
        gson.toJson( annotations,it )
    }
}

println('Export and save Detection Measurements and annotations Done')

// Imports
import org.locationtech.jts.io.WKTWriter
import org.slf4j.LoggerFactory;

