# import matplotlib.pyplot as plt
# import rasterio
# import numpy as np
# import os, sys
# 
# def plot_tif(tif_path, out_png):
#     with rasterio.open(tif_path) as src:
#         arr = src.read(1)
#     plt.figure(figsize=(10,6))
#     plt.imshow(arr, cmap='RdBu', vmin=-1, vmax=1)
#     plt.colorbar(label='Phase / displacement (scaled)')
#     plt.title(os.path.basename(tif_path))
#     plt.axis('off')
#     plt.savefig(out_png, dpi=150)
#     plt.close()
#     return out_png
# 
# if __name__ == "__main__":
#     outdir = sys.argv[1] if len(sys.argv)>1 else "/opt/data/out"
#     tifs = [os.path.join(outdir,f) for f in os.listdir(outdir) if f.endswith('.tif')]
#     if not tifs:
#         print("No tif found")
#         sys.exit(1)
#     pngs = []
#     for t in tifs:
#         png = plot_tif(t, t + '.png')
#         pngs.append(png)
#     # minimal textual report
#     report = os.path.join(outdir, 'insar_report.txt')
#     with open(report, 'w') as fh:
#         fh.write("Mini InSAR Pipeline report\n")
#         fh.write("Outputs:\n")
#         for p in tifs:
#             fh.write(f"- {p}\n")
#     print("Report saved to", report)



import matplotlib.pyplot as plt
import rasterio
import numpy as np
import os, sys

def plot_tif(tif_path, out_png):
    with rasterio.open(tif_path) as src:
        arr = src.read(1)
    plt.figure(figsize=(10,6))
    plt.imshow(arr, cmap='RdBu', vmin=-1, vmax=1)
    plt.colorbar(label='Phase / displacement (scaled)')
    plt.title(os.path.basename(tif_path))
    plt.axis('off')
    plt.savefig(out_png, dpi=150)
    plt.close()
    return out_png

if __name__ == "__main__":
    outdir = sys.argv[1] if len(sys.argv)>1 else "/opt/data/out"
    tifs = [os.path.join(outdir,f) for f in os.listdir(outdir) if f.endswith('.tif')]
    if not tifs:
        print("No tif found")
        sys.exit(1)
    pngs = []
    for t in tifs:
        png = plot_tif(t, t + '.png')
        pngs.append(png)

    report = os.path.join(outdir, 'insar_report.txt')
    with open(report, 'w') as fh:
        fh.write("Mini InSAR Pipeline report\n")
        fh.write("Outputs:\n")
        for p in tifs:
            fh.write(f"- {p}\n")
    print("Report saved to", report)
