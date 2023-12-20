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
        files = listFiles('./paren/folder/', 'tif)
    '''
    import glob
    
    text = '/*'+pattern
    input_files = glob.glob(path + text)

    return(input_files)

# =========================================================================================== #
#               Calculate Line density 
# =========================================================================================== #

def lineDensity(input_vect: AnyStr, pixelSize: AnyStr, mask: Optional[bool]=False, maskData:Optional[AnyStr]=None, maskType:Optional[AnyStr]=None):
    '''
    Function to list all files with specific pattern within a folder path

    Parameters:
        path: folder path
        pattern: search pattern (e.g., tif)
        
    Example:
        files = listFiles('./paren/folder/', 'tif)
    '''
    from rasterio.transform import from_origin
    from rasterio.features import geometry_mask
    import numpy as np

    if mask is True:
        if str(maskType).upper() == 'RASTER':
            bounds = maskData.bounds
            minX, minY, maxX, maxY = bounds.left, bounds.bottom, bounds.right, bounds.top
        if str(maskType).upper() == 'VECTOR' or str(maskType).upper() == 'SHAPEFILE':
            minX, minY, maxX, maxY = maskData.total_bounds
            
        rows = int((maxY - minY) / pixelSize)
        cols = int((maxX - minX) / pixelSize)
    else:
        minX, minY, maxX, maxY = input_vect.total_bounds
        rows = int((maxY - minY) / pixelSize)
        cols = int((maxX - minX) / pixelSize)

    transform = from_origin(minX, maxY, pixelSize, pixelSize)
    
    data_array = np.zeros((rows, cols))

    for index, row in input_vect.iterrows():
        geometry = row['geometry']
        mask = geometry_mask([geometry], transform=transform, out_shape=(rows, cols), invert=True)
        data_array += mask
    
    return data_array

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



