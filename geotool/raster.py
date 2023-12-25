# Python 3.11.6
from typing import AnyStr, Dict, Optional

# =========================================================================================== #
#               Open raster geotif file
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
    
# =========================================================================================== #
#               Open shapefile
# =========================================================================================== #
def openVect(input_path: AnyStr):
    '''
    ---

    Parameters:

    Example:
       
    '''
    import geopandas as gpd
    import os
    
    vect = gpd.read_file(input_path)
    basename = os.path.basename(input_path)
    crs = vect.crs
    datashape = vect.shape

    print(f"Open {basename} \n crs: {crs} \n Data shape {datashape}")

    return vect


# =========================================================================================== #
#               Merge  geotif files in a list using GDAL and VRT
# =========================================================================================== #
def merge_geotif_vrt(input_files: AnyStr, output_file: AnyStr, compress: bool=True):
    '''
    Merge multiple geotif file using gdal VRT for better perfomance speed

    Parameters:
        input_files: List of input geotif files
        output_file: path of output tif file

    Example:
       input_list = tools.listFiles('./test/', 'tif)
       raster.merge_geotif_vrt(input_list, './test/output.tif')
    '''

    import os
    from osgeo import gdal
    #  Create a temp vrt file
    vrt_file = 'merged.vrt'

    if compress is True:
        gdal.BuildVRT(vrt_file, input_files, options=['COMPRESS=LZW'])
        gdal.Translate(output_file, vrt_file, format='GTiff', creationOptions=['COMPRESS=LZW'])
        os.remove(vrt_file)
    else:
        gdal.BuildVRT(vrt_file, input_files)
        gdal.Translate(output_file, vrt_file)
        os.remove(vrt_file)
    
    print(f"Finished merge raster files, the output is at {output_file}")
    

# =========================================================================================== #
#               Merge  geotif files in a list using Rasterio
# =========================================================================================== #
def merge_geotif_rio(input_files: AnyStr, output_file: AnyStr, compress: bool=True):
    '''
    Merge multiple geotif file using Rasterio 

    Parameters:
        input_files: List of input geotif files
        output_file: path of output tif file

    Example:
       input_list = tools.listFiles('./test/', 'tif)
       raster.merge_geotif_vrt(input_list, './test/output.tif')
    '''
    import rasterio
    from rasterio import merge 

    src_files = []
    for file in input_files:
        ds = rasterio.open(file)
        src_files.append(ds)

    fun_sum = merge.copy_sum
    fun_count = merge.copy_count

    mosaic_sum, out_trans = merge.merge(src_files, method=fun_sum)
    mosaic_count, out_trans = merge.merge(src_files, method=fun_count)

    mosaic_out = mosaic_sum / mosaic_count
    
    out_meta = src_files[0].meta.copy()
    out_meta.update({"driver": "GTiff",
                                    "height": mosaic_out.shape[1],
                                    "width": mosaic_out.shape[2],
                                    "transform": out_trans})
    
    if compress is True:
        out_meta.update({'compress': 'LWZ'})
    else:
        pass
    
    with rasterio.open(output_file, "w", **out_meta) as dest:
        dest.write(mosaic_out)
    
    print(f"Finished merge raster files, the output is at {output_file}")


# =========================================================================================== #
#               Stack layer of geotif images
# =========================================================================================== #
def stackLayer(input_files: AnyStr, output_file: AnyStr, compress: bool=True):
    '''
    Stack layers for different geotif images with the same extent and each image may have more than 1 band

    Parameters:
        input_files: List of input geotif files
        output_file: path of output tif file

    Example:
       input_list = tools.listFiles('./test/', 'tif)
       raster.merge_geotif_vrt(input_list, './test/output.tif')
    '''
    import numpy as np
    import rasterio
    import os
    
    # Open each GeoTIFF file and read bands
    src_files_to_mosaic = []
    bands_stack = []

    for img in input_files:
        path = os.path.join(img)
        src = rasterio.open(path)
        src_files_to_mosaic.append(src)
        
        for band in range(1, src.count + 1):
            # Read each band as a separate numpy array
            band_data = src.read(band)
            bands_stack.append(band_data)

    stacked_array = np.stack(bands_stack, axis=-1)

    # Extract meta data as reference for the output
    with rasterio.open(input_files[0]) as src:
        meta = src.meta
    # Update number of bands
    meta.update(count= stacked_array.shape[2])
    # Compress option
    if compress is True:
        meta.update({'compress': 'LWZ'})
    else:
        pass
    
    # Write the output as geotif file
    with rasterio.open(output_file, 'w', **meta) as dst:
        for i in range(0, stacked_array.shape[2]):
            band_data = stacked_array[:, :, i]
            dst.write(band_data, i+1)

    print(f"Finished stack raster layers, the output is at {output_file}")


# =========================================================================================== #
#               Compress file size and write geotif
# =========================================================================================== #
def writeRaster_rio(input_Arr: AnyStr, output_name: AnyStr, profile: Dict[str, AnyStr], compress: bool = False, compress_opt: Optional[AnyStr] = None):
    '''
    Write raster Geotif from data Array using Rasterio.

    Parameters:
        input_Arr: Data array.
        output_name: Output file path.
        profile: Rasterio profile settings.
        compress: Boolean indicating whether to compress the output.
        compress_opt: Compression algorithm (optional).

    Example:
       ...
    '''
    import rasterio

    class RasterWriteError(Exception):
        pass

    if compress is True:
        if compress_opt is None:
            raise RasterWriteError('compress_opt is not provided')
        if str(compress_opt).upper() == 'LZW':
            compress_algorithm = 'LZW'
        elif str(compress_opt).upper() == 'DEFLATE':
            compress_algorithm = 'DEFLATE'
        profile.update(**{'compress': compress_algorithm})
    else:
        profile = profile

    profile['count'] = int(input_Arr.shape[0])

    with rasterio.open(output_name, 'w', **profile) as dst:
        for i in range(0, int(input_Arr.shape[0])):
            data = input_Arr[i]
            dst.write(data, i + 1)

    print(f"Finished writing raster files, the output is at {output_name}")

# =========================================================================================== #
#              Crop and Mask raster using shapefile
# =========================================================================================== #
def cropRaster(img: AnyStr, roi: AnyStr, maskout: bool= False):
    '''
    Crop and mask raster opened by rasterio by shapefile vector.

    Parameters:
        img: image raster file opened by rasterio
        roi: region of interest opened by geopandas 
    Example:
       img = rasterio.open('./landsat_multi/landsat_img_test.tif', 'r')
       roi = gpd.read_file('./roi/roi.shp')

       masked = raster.maskRaster(img, roi)

       import earthpy.plot as ep
       ep.plot_rgb(masked, stretch=True, rgb=(3,2,1))
    '''
    from rasterio import mask
    from shapely.geometry import mapping
    from shapely.geometry import box
    import geopandas as gpd

    if maskout is True:
        polys = roi
    else:
        minx, miny, maxx, maxy = roi.total_bounds
        bbox = box(minx, miny, maxx, maxy)
        polys = gpd.GeoDataFrame({'geometry': [bbox]}, crs=roi.crs)
    
    masked_img, geotranform = mask.mask(dataset=img, shapes=polys.geometry.apply(mapping), crop=True)
    
    return masked_img


