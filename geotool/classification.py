# Python 3.11.6
from typing import AnyStr, Dict, Optional

# =========================================================================================== #
#               
# =========================================================================================== #
def openRaster(input_path: AnyStr):
    '''
    ---

    Parameters:

    Example:
       
    '''
    import rasterio
    import os

    img = rasterio.open(input_path)
    basename = os.path.basename(input_path)
    meta = img.meta

    print(f"Open {basename} \n{meta}")

    return img
    
