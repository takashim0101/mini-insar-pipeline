# import rasterio
# from rasterio import Affine
# import glob, os, sys
# 
# if __name__ == "__main__":
#     outdir = sys.argv[1] if len(sys.argv)>1 else "/opt/data/out"
#     tiles = glob.glob(os.path.join(outdir, '*.vrt')) + glob.glob(os.path.join(outdir, '*.tif'))
#     for t in tiles:
#         if t.endswith('.tif'):
#             continue
#         out_tif = t.replace('.vrt', '.tif')
#         with rasterio.open(t) as src:
#             meta = src.meta.copy()
#             meta.update(driver='GTiff', compress='lzw')
#             data = src.read()
#             with rasterio.open(out_tif, 'w', **meta) as dst:
#                 dst.write(data)
#         print("Saved", out_tif)



import rasterio
import glob, os, sys

if __name__ == "__main__":
    outdir = sys.argv[1] if len(sys.argv)>1 else "/opt/data/out"
    tiles = glob.glob(os.path.join(outdir, '*.vrt')) + glob.glob(os.path.join(outdir, '*.tif'))
    for t in tiles:
        if t.endswith('.tif'):
            continue
        out_tif = t.replace('.vrt', '.tif')
        with rasterio.open(t) as src:
            meta = src.meta.copy()
            meta.update(driver='GTiff', compress='lzw')
            data = src.read()
            with rasterio.open(out_tif, 'w', **meta) as dst:
                dst.write(data)
        print("Saved", out_tif)
