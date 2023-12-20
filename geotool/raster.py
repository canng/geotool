# Python 3.11.6
from typing import AnyStr, Dict, Optional

# =========================================================================================== #
#               Merge  geotif files in a list using GDAL and VRT
# =========================================================================================== #
def merge_geotif_vrt(input_files: AnyStr, output_file: AnyStr, compress: bool=True):
    '''
    Function to merge multiple geotif file using gdal VRT for better perfomance speed

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
        gdal.BuildVRT(vrt_file, input_files, options=['COMPRESS=DEFLATE'])
        gdal.Translate(output_file, vrt_file, format='GTiff', creationOptions=['COMPRESS=DEFLATE'])
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
    Function to merge multiple geotif file using Rasterio 

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
        out_meta.update({'compress': 'deflate'})
    else:
        pass
    
    with rasterio.open(output_file, "w", **out_meta) as dest:
        dest.write(mosaic_out)
    
    print(f"Finished merge raster files, the output is at {output_file}")


# =========================================================================================== #
#               Compress file size and write geotif
# =========================================================================================== #
def writeRaster_rio(input_Arr: AnyStr, output_name: AnyStr, profile: Dict[str, AnyStr], compress: bool = False, compress_opt: Optional[AnyStr] = None):
    '''
    Function to write raster Geotif from data Array using Rasterio.

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



