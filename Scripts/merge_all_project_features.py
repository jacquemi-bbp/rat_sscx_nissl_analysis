import glob
from pathlib import Path


path = ('/gpfs/bbp.cscs.ch/project/proj53/LayerBoundariesProject/'
        'Production/20231102/datasets/Exported_Features/'
        'QuPath_exported_data/For_prediction/**/*Detections.txt'
)
file_list = glob.glob(path, recursive=True)


for  file_path in file_list:
    filename = file_path.split('/')[-1]
    print(f'old_path {file_path}')
    new_path = ('/gpfs/bbp.cscs.ch/project/proj53/LayerBoundariesProject/Production/'
    '20231102/datasets/Exported_Features/QuPath_exported_data/For_prediction/All/'
    )
    new_path+=filename
    print(f'new_path {new_path}')
    Path(file_path).rename(new_path)
