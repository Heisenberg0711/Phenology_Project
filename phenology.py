import os
import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio
import rasterio.mask
from matplotlib import pyplot as plt
from rasterio import Affine
from rasterio.warp import reproject, Resampling

#Process the county sowing dataset
os.chdir('/home/heisenberg/my_repo/Data')
current_year = 2002
current_year_str = str(current_year)

df = pd.read_csv('maize.alldat.nolatlon.csv')
IL = (df['state']=='IL')&(df['YEAR']==current_year)
IL_county = df[IL]
col_list = ['FIPS','sday']
IL_county = IL_county[col_list]
IL_county = IL_county.groupby(['FIPS']).mean()
sow_date = list(IL_county['sday'])
del df

#Get all county FIPS in Illinois
county_FIPS = IL_county.index.values
county_FIPS = county_FIPS.tolist()
county_FIPS = list(map(str,county_FIPS))

#Get all counties in IL in the shape file
os.chdir('/home/heisenberg/my_repo/Data/County_Shape')
import geopandas as gpd
county_shape = gpd.read_file('CoUS_GCS12.shp')
county_shape = county_shape[county_shape['atlas_stco'].isin(county_FIPS)]
cols = ['atlas_stco','geometry']
county_shape = county_shape[cols]

#Read CDL data and change the CDL data to corn/non-corn
os.chdir('/home/heisenberg/my_repo/Data/CDL')
cdl_name = 'CDL_' + current_year_str + '.tif'
cdl = rasterio.open(cdl_name)
cdl_data = cdl.read(1)
cdl_data[cdl_data != 1] = 0

#Read state shape file
os.chdir('/home/heisenberg/my_repo/Data')
state = gpd.read_file('cb_2017_us_state_500k/')

#Mask by county function
def mask_by_county(county_shape, corn, i):
    img_clip, trans = rasterio.mask.mask(corn, [county_shape.iloc[i].geometry], crop=True)
    img_clip = img_clip.astype('float32')
    img_clip[img_clip == 0] = np.nan
    index = np.nanmean(img_clip)
    return (img_clip[0,:,:],index)


#Iterate every tif file in a specific year's gcvi directory.
Iterate every tif file in a specific year's gcvi directory.
gcvi_directory = os.fsdecode('/home/heisenberg/my_repo/Data/GCVI/'+ current_year_str)
index = 0
name_index = 2000055
All_GCVI = {}

# for file in os.listdir(gcvi_directory):
#     filename = os.fsdecode(file)
#     if filename.endswith(".tif"):
#         os.chdir(gcvi_directory)
#         # All_GCVI[index] = calculate_GCVI(filename)
#         # index += 1
#         print(type(filename))
#         continue
#     else:
#         print("Not a GCVI file")





#Function that returns GCVI index for each county for each GCVI GeoTIFF
def calculate_GCVI(filename, state, cdl, cdl_data, county_shape):
    gcvi = rasterio.open(filename)
    state.crs = gcvi.crs

    img_clip, trans = rasterio.mask.mask(gcvi, [state.iloc[1].geometry], crop=True)
    img_clip = img_clip.astype('float32')
    img_clip[img_clip == 0] = np.nan
    #plt.imshow(img_clip[0,:,:],vmin=0, vmax=800, cmap='Spectral')

    #Project the CDL to GCVI size
    newarr = np.empty(shape=(img_clip.shape[0],
                             img_clip.shape[1],img_clip.shape[2]))
    reproject(
        cdl_data, newarr,
        src_transform = cdl.transform,
        dst_transform = gcvi.transform,
        src_crs = cdl.crs,
        dst_crs = gcvi.crs,
        resampling = Resampling.average)

    #Bigger than 0.5 means there is corn, while smaller than 0.5 means no corn
    is_corn = newarr >= 0.5
    corn_field = is_corn.astype(int)
    corn_field = corn_field.astype(np.float64)

    #Finally mask the corn/non-corn matrix with gcvi to get gcvi indexes
    gcvi_corn = np.multiply(img_clip, corn_field)
    #plt.imshow(gcvi_corn.squeeze())

    #Re-Write the projected GCVI to a new tif file
    os.chdir('/home/heisenberg/my_repo/Data/Output/')
    new_dataset = rasterio.open('filter1.tif', 'w', driver='GTiff',
                                height = corn_field.shape[1], width = corn_field.shape[2],
                                count = 1, dtype = corn_field.dtype,
                                crs = gcvi.crs,
                                transform = gcvi.transform)

    new_dataset.write(gcvi_corn.squeeze(),1)
    new_dataset.close()

    #Change the projection of shape file to cdl file.
    county_shape.crs = cdl.crs
    num_of_county = len(county_shape.index)


    #Read saved gcvi_corn raster file for masking
    test = rasterio.open('filter1.tif')
    #corn_by_county = {}
    index_by_county = {}

    for county in range(num_of_county):
        result = mask_by_county(county_shape,test,county)
        #corn_by_county[county] = result[0]
        index_by_county[county] = result[1]
    os.remove('filter1.tif')
    return index_by_county


i = 17
plt.imshow(corn_by_county[i])
plt.colorbar()
print("Average vegetation index is "+ str(index_by_county[i]))
