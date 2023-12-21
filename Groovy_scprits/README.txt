1/ To export annotations and detections without running cellpose (In the case where the detections are already existing in the QuPath project)
login into linux workstation

1.1/ Images without layers export annations
prompt%> cd /home/jacquemi/working_dir/Rat_sscx_nissl/rat_sscx_nissl_analysis
prompt%> mkdir /gpfs/bbp.cscs.ch/project/proj53/LayerBoundariesProject/Production/20231102/datasets/Exported_Features/QuPath_exported_data/For_prediction
prompt%> /usr/local/QuPath/QuPath/bin/QuPath script export_annation_and_detection_without_cellpose.groovy -p="/gpfs/bbp.cscs.ch/project/proj53/LayerBoundariesProject/Analysis/Nissl_2/01413829_RH_Nissl_2_QuPath/ProjectQuPath_01413829_RH_Nissl_2.qpproj" -a=/gpfs/bbp.cscs.ch/project/proj53/LayerBoundariesProject/Production/20231102/datasets/Exported_Features/QuPath_exported_data/For_prediction

prompt%> source ~/working_dir/Rat_sscx_nissl/venv_py310/bin/activate
prompt%> cd /home/jacquemi/working_dir/Rat_sscx_nissl/rat_sscx_nissl_analysis
edit the Config/linux/batch_convert_features_for_ml_prediction.ini file
prompt%> pyqupath_processing  batch-convert-for-ml --config-file-path Config/linux/batch_convert_features_for_ml_prediction.ini


1.2/ GroundTruth Images with layers export annations
prompt%> mkdir /gpfs/bbp.cscs.ch/project/proj53/LayerBoundariesProject/Production/20231102/datasets/Exported_Features/QuPath_exported_data/Ground_Truth
prompt%> /usr/local/QuPath/QuPath/bin/QuPath script export_annation_and_detection_without_cellpose.groovy -p="/gpfs/bbp.cscs.ch/project/proj53/LayerBoundariesProject/Analysis/Nissl_2/01413829_RH_Nissl_2_QuPath/ProjectQuPath_01413829_RH_Nissl_2.qpproj" -a=/gpfs/bbp.cscs.ch/project/proj53/LayerBoundariesProject/Production/20231102/datasets/Exported_Features/QuPath_exported_data/Ground_Truth

edit the Config/linux/batch_convert_features_for_ml_ground_truth.ini file
prompt%> pyqupath_processing  batch-convert-for-ml --config-file-path Config/linux/batch_convert_features_for_ml_ground_truth.ini
