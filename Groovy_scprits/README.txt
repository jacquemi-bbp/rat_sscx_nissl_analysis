1/ To export annotation and detection without running cellpose (In the case where the detections are already existing in the QuPath project)
login into linux workstation

prompt%> cd /home/jacquemi/working_dir/Rat_sscx_nissl/rat_sscx_nissl_analysis
prompt%> /usr/local/QuPath/QuPath/bin/QuPath script export_annation_and_detection_without_cellpose.groovy -p="/gpfs/bbp.cscs.ch/project/proj53/LayerBoundariesProject/Analysis/Nissl_2/01413829_RH_Nissl_2_QuPath/ProjectQuPath_01413829_RH_Nissl_2.qpproj" -a=/tmp/test

