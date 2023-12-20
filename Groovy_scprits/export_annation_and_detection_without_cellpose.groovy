// Imports
import org.locationtech.jts.geom.util.GeometryFixer
import org.locationtech.jts.io.WKTWriter
import org.slf4j.LoggerFactory;

def saveFolderPath =  this.args[0]
logger.info("Save folder: {}", saveFolderPath)

def saveFolder = new File(saveFolderPath)

def entry = getProjectEntry()
def entryMetadata = entry.getMetadataMap()
def imageData = getCurrentImageData()


if (entryMetadata['Analyze'] == 'True') {
    def pathObjects = getObjects{ it.getPathClass().equals( getPathClass( "S1HL" ) ) }
    if (pathObjects.isEmpty()) {
        Dialogs.showErrorMessage("Cellpose", "Please select a parent object!")
    }
    else {
	    println "imageData $imageData"
    
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

            saveDetectionMeasurements( saveFolder.getAbsolutePath() )
        
	    // Add what is needed and remove the old ones
	    removeObjects( multis, false )
	    addObjects( fixedMultis )
	    fireHierarchyUpdate()
    
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
	}
}

