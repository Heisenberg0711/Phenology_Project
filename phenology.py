import numpy as np
import rasterio
from matplotlib import pyplot as plt

CDL pixel size: [0.000325888636548,-0.000325899193786]
    image size: [12329, 16993]

GCVI pixel size: [0.005418574049116,-0.005418574182687]
    image size: [742, 1023]



with rasterio.open('transformed.tif') as src:
    transformed_array = src.read(1)
plt.imshow(transformed_array)


#Step 1: Translate the GCVI to the CDL shape
gdal_translate -of GTiff -outsize 12329 16993 -r bilinear GCVI_filled_2016191.tif transformed.tif

#Step 2:Crop the scaled GCVI graph with county boundary (The attribute is called atlas_stco)
#See the metadata using Geopandas ?


#Step 3: Filter out all corn areas
