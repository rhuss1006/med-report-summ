"""
Dan Beecher, Rayd Hussain
4/13/2025
DS2500
Final Project Code
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from mpl_toolkits.basemap import Basemap

FILENAME = 'meteorite_land.csv'

def normalize_mass(gdf, column_name):
    gdf['normalized mass'] = ((gdf[column_name] - gdf[column_name].min()) /
                              (gdf[column_name].max() - gdf[column_name].min()))
    return gdf

def main():

    df = pd.read_csv(FILENAME)
    print(df.head())

    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df['reclong'], df['reclat'], crs='EPSG:4326'))
    gdf = normalize_mass(gdf, 'mass (g)')
    print(gdf.head())

    map = Basemap(lat_0=0, lon_0=0)
    map.drawcoastlines()
    map.fillcontinents(color = '#228B22', lake_color='#00008B')
    map.drawmapboundary(fill_color='#00008B')
    map.scatter(gdf.geometry.x, gdf.geometry.y, c='red', s=gdf['normalized mass'] * 20)
    plt.show()


    # gdf.plot(figsize=(10,10))
    # plt.show()


if __name__ == '__main__':
    main()