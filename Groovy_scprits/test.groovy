import qupath.ext.biop.cellpose.Cellpose2D

def defaultEnvType = EnvType.VENV // or EnvType.VENV
def defaultVersion = CellposeVersion.OMNIPOSE // or CellposeVersion.CELLPOSE
def defaultEnvPath = "/Users/jacquemi/working_dir/cellpose/cellpose"

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



// Specify the model name (cyto, nuc, cyto2 or a path to your custom model)
def pathModel = 'cyto'

def cellpose = Cellpose2D.builder(pathModel)
        .channels('Green')            // Select detection channel(s)
        .normalizePercentiles(1, 99) // Percentile normalization
        .pixelSize(1.0)              // Resolution for detection
        .diameter(27.5)                // Average diameter of objects in px (at the requested pixel sie)
//        .cellExpansion(5.0)          // Approximate cells based upon nucleus expansion
        .cellConstrainScale(1.5)     // Constrain cell expansion using nucleus size
        .measureShape()              // Add shape measurements
        .measureIntensity()          // Add cell measurements (in all compartments)
        .build()

// Run detection for the selected objects
// Run detection for the selected objects
def imageData = getCurrentImageData()
def pathObjects = getObjects{ it.getPathClass().equals( getPathClass( "S1" ) ) }

if (pathObjects.isEmpty()) {
    Dialogs.showErrorMessage("Cellpose", "Please select a parent object!")
    return
}
cellpose.detectObjects(imageData, pathObjects)
println 'Done!'


   
import qupath.ext.biop.cmd.VirtualEnvironmentRunner.EnvType;
import qupath.ext.biop.cellpose.CellposeSetup.CellposeVersion;
import qupath.ext.biop.cellpose.CellposeSetup
import javafx.beans.property.ObjectProperty;
import javafx.beans.property.StringProperty;
import qupath.lib.gui.prefs.PathPrefs;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
