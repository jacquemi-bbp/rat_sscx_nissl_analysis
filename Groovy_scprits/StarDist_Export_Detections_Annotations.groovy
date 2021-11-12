// Run StarDist Detection on images that contain the metadata key "Analyze" with value "True"
// Otherwise the image is skipped
// Olivier Burri, EPFL - PTECH - SV - BIOP
// For Julie Meystre, Markram Group and Jean Jacquemier
// Last Update: October 25th 2021

def logger = LoggerFactory.getLogger(this.class);

// Define location for saved annotations and detection measurements from command line arguments
def saveFolderPath = this.args[0]
logger.info("Save folder: {}", saveFolderPath)

def saveFolder = new File(saveFolderPath)

// Specify the model directory (you will need to change this!)
def model = 'julie-nissl-round2_nissl-2_r16_p128_g2_k3_e400_se100_b32_aug.pb'
//def model = 'julie-1-slice_nissl_r16_p128_g2_k3_e400_se100_b32_aug.pb'


// Pick up current image name to append to the resulting files
def imageName = getCurrentServer().getMetadata().getName()


// 0. Run StarDist Detection
def pathModel = buildFilePath(PROJECT_BASE_DIR, "models", model)

def entry = getProjectEntry()

println "Detecting Cells for $entry"
def stardist = StarDist2D.builder(pathModel)
            .threshold(0.47)                // Probability (detection) threshold//
            .normalizePercentiles(1, 99.8)  // Percentile normalization
            .pixelSize(0.6920)              // Resolution for detection
            .ignoreCellOverlaps(false)      // Set to true if you don't care if cells expand into one another
            .measureShape()                 // Add shape measurements
            .measureIntensity()             // Add cell measurements (in all compartments)
            .includeProbability(true)       // Add probability as a measurement (enables later filtering)
            .simplify(1)                    // Control how polygons are 'simplified' to remove unnecessary vertices
            .doLog()                        // Use this to log a bit more information while running the script
            .build()
            
// Run detection for the selected objects
def imageData = getCurrentImageData()
def pathObjects = getObjects{ it.getPathClass().equals( getPathClass( "S1" ) ) }
    
stardist.detectObjects(imageData, pathObjects)
    
println 'Done!'
    
getDetectionObjects().each{ it.setPathClass( getPathClass("StarDist") ) }

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
 
def file = new File(saveFolder,imageName + '_annotations.json' )
annotations.each {
    println writer.write( it.getROI().getGeometry() )
    file.withWriter('UTF-8') {
        gson.toJson( annotations,it )
    }
}

println('Done')

// Imports
import qupath.ext.stardist.StarDist2D
import org.locationtech.jts.io.WKTWriter
import org.slf4j.LoggerFactory;
