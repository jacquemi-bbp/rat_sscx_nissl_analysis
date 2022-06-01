import qupath.ext.biop.cellpose.Cellpose2D


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

// CIRCULARY CORRECTION START
import org.locationtech.jts.geom.util.GeometryFixer

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



// Imports
import qupath.ext.biop.cmd.VirtualEnvironmentRunner.EnvType;
import qupath.ext.biop.cellpose.CellposeSetup.CellposeVersion;
import qupath.ext.biop.cellpose.CellposeSetup
import org.locationtech.jts.io.WKTWriter
import org.slf4j.LoggerFactory;

