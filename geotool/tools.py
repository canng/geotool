from typing import AnyStr, Dict, Optional
from shapely.geometry import polygon
from shapely import speedups
speedups.disable()

import os
os.environ['GDAL_DATA'] = os.environ['CONDA_PREFIX'] + r'\Library\share\gdal'
os.environ['PROJ_LIB'] = os.environ['CONDA_PREFIX'] + r'\Library\share'

# =========================================================================================== #
#               Find all files in folder with specific pattern
# =========================================================================================== #
def listFiles(path: AnyStr, pattern: AnyStr):
    '''
    Function to list all files with specific pattern within a folder path

    Parameters:
        path: folder path
        pattern: search pattern (e.g., tif)
        
    Example:
        files = listFiles('./parent/folder/', 'tif)
    '''
    import glob
    
    text = '/*'+pattern
    input_files = glob.glob(path + text)

    return(input_files)

# =========================================================================================== #
#               Get common extent 
# =========================================================================================== #
def getExtent(inputList: AnyStr):
    '''
    Function to ...

    Parameters:
        
        
    Example:
        
    '''
    import rasterio

    general_extent = None

    for tif_file in inputList:
        with rasterio.open(tif_file) as dataset:
            
            # Get the dataset's bounding box
            dataset_extent = dataset.bounds

            if general_extent is None:
                general_extent = dataset_extent
            else:
                # Calculate the minimum bounding box that encompasses both extents
                general_extent = (
                    min(general_extent[0], dataset_extent[0]),
                    min(general_extent[1], dataset_extent[1]),
                    max(general_extent[2], dataset_extent[2]),
                    max(general_extent[3], dataset_extent[3])
                )
    # Create a GeoDataFrame with the general extent
    return general_extent



