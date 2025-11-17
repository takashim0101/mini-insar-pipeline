import matplotlib.pyplot as plt
import rasterio
import numpy as np
import os
import sys

def convert_tif_to_png(tif_path, png_path):
    """
    Converts a GeoTIFF file to a PNG image.
    """
    with rasterio.open(tif_path) as src:
        # Read the first band
        arr = src.read(1)
        
        # Get metadata
        meta = src.meta
        
        # Get the colormap from the metadata if it exists
        try:
            cmap = meta['colormap'][1]
            # Normalize the array to the colormap range
            arr = np.interp(arr, (arr.min(), arr.max()), (0, 255)).astype(np.uint8)
        except (KeyError, IndexError):
            # Use a default colormap if one is not found in the metadata
            cmap = 'viridis'

    plt.figure(figsize=(10, 10))
    plt.imshow(arr, cmap=cmap)
    plt.axis('off')
    plt.savefig(png_path, bbox_inches='tight', pad_inches=0)
    plt.close()
    print(f"Successfully converted {tif_path} to {png_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python convert_tif_to_png.py <input_tif> <output_png>")
        sys.exit(1)
        
    input_tif = sys.argv[1]
    output_png = sys.argv[2]
    
    convert_tif_to_png(input_tif, output_png)
