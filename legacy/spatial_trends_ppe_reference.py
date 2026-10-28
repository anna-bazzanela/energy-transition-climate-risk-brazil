#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reference snapshot of the supplied research script (June 6, 2026).
Author: Anna Carolina Bazzanela

Only paths, comments and identifiers were sanitized for public sharing.
The executable plotting logic and disabled historical blocks are retained.
Run from the repository root only after supplying all required GIS/data files.
Do not assume this is a portable or validated reproduction. See legacy/README.md.
"""

import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import pymannkendall as mk
import pandas as pd

import cartopy.feature as cfeature
import cartopy.crs as ccrs
from cartopy.feature import NaturalEarthFeature
from matplotlib.colors import ListedColormap
import matplotlib as mpl
from cartopy.io.shapereader import Reader

import geopandas as gpd
import regionmask as rmk


input_data_path = 'data/indices/'
ocean_shape_path = 'data/shapes/ocean.shp'
output_data_path = 'data/precomputed/'
regions_shape_path = 'data/shapes/brazil_regions.shp'
south_america_shape_path = 'data/shapes/south_america.shp'

# Brazilian region mask
br_reg = gpd.read_file(regions_shape_path)
br_reg_mask = rmk.from_geopandas(br_reg)

# Country mask
br = gpd.read_file(south_america_shape_path)
br_mask = rmk.from_geopandas(br)

df = pd.DataFrame({'Regions':['S','SE','N','NE','CO']})
df_clim = pd.DataFrame({'Regions':['S','SE','N','NE','CO']})

font_gl = {'family': 'serif', 'size': 22, 'color': 'black'}


colors_prcptot = ['#b05606','#e68d23','#fdca88','#fde2bb','#ffffff',
             '#ffffff','#d9dbeb','#c2bedc','#887cb2','#502382']

cmapprcptot = ListedColormap(colors_prcptot)
cmapprcptot.set_over("#2d004b")    
cmapprcptot.set_under('#7f3b08')
tick_prcptot = [-120, -80, -60, -40,  -20,  0,  20,   40,  60,  80, 120]
normprcptot = mpl.colors.BoundaryNorm(boundaries=tick_prcptot, ncolors=len(colors_prcptot))


colors_r95p = ['#b05606','#e68d23','#fdca88','#fde2bb','#ffffff',
             '#ffffff','#d9dbeb','#c2bedc','#887cb2','#502382']
cmapr95p = ListedColormap(colors_r95p)
cmapr95p.set_over("#2d004b")    
cmapr95p.set_under('#7f3b08')

tickr95p = [-120, -80, -60, -40,  -20,   0,   20,   40,  60,  80, 120]
normr95p = mpl.colors.BoundaryNorm(boundaries=tickr95p, ncolors=len(colors_r95p))


colors_temp = ['#3a54a4','#5c90c2','#90c3dd','#c5e6f0','#f0f9db','#ffffff',
             '#ffffff','#fff0a8','#fdc778','#f98e52','#e54e35','#bd1726']
cmaptemp = ListedColormap(colors_temp)
cmaptemp.set_over("#a50026")    
cmaptemp.set_under('#313695')

colors_cdd = ['#005046','#1a7e76','#58b0a7','#a3dbd3','#def0ed','#ffffff',
              '#ffffff','#f5efdc','#ead59f','#cfa256','#a5691b','#6e4007']
cmapcdd = ListedColormap(colors_cdd)
cmapcdd.set_over('#543005')    
cmapcdd.set_under("#003c30")

tickcwd = [-10,  -8,  -6,  -4,  -2,  -1, 0, 1,   2,   4,   6,   8,  10]
normcdd = mpl.colors.BoundaryNorm(boundaries=tickcwd, ncolors=len(colors_cdd))


lv_temp = np.arange(-1,1.2,0.2)

cmaps = [ cmaptemp,cmaptemp]#cmapcdd,cmapprcptot,cmapr95p,

indices = ['TNx','TXx']#,'CDD','PRCPTOT','R95p',

labels= ['°C/dec','°C/dec']#'days/dec','mm/dec','mm/dec',

ticks = [lv_temp, lv_temp]#tickcwd,tick_prcptot,tickr95p,
         
levels = ticks

#norms = [normcdd,normprcptot, normr95p]'none'

gdf = gpd.read_file("data/shapes/substations.shp")

figure_output_path = 'outputs/figures/'

for k in range(len(indices)):  
    
    '''    
    
    if k==2:
        ds = ds['TXx']-273.15
    
    elif k==1:
        
        ds = ds[list(ds.data_vars)[0]]

        prcptot_dataset = (xr.open_dataset(input_data_path+'PRCPTOT_monthly_complete.nc')).sel(lat=slice(-35,10), lon=slice(-75, -30))
        new_dataset = ds*prcptot_dataset.PRCPTOT
        
        ds = new_dataset.isel(percentiles=0)
       
    else:
        
        ds = ds[list(ds.data_vars)[0]]
    
    
    seasonal_dataset = ds.groupby('time.season')
    '''
    '''
    ds = xr.open_dataset(input_data_path+indices[k]+'_annual_obs.nc')
    #ds = ds.rename({'latitude':'lat','longitude':'lon'})
    
    #if k ==1:
    #    ds = ds.rename({'latitude':'lat','longitude':'lon'})     
        
    ds = ds.sel(lat=slice(-35,10), lon=slice(-75, -30))
    seasonal_data = ds[list(ds.data_vars)[0]]
    
    output_trend = []
    output_pvalue = []
    for i in np.arange(len(seasonal_data.lat.values)):
        for j in np.arange(len(seasonal_data.lon.values)):
            
            try:
        
                d = seasonal_data[:,i,j]#.interpolate_na(dim='time')
                slope_val = mk.original_test(d).slope
                p_val = mk.original_test(d).p
                
                if p_val <= 0.05:
                    slope_val=slope_val
                    p_val = np.nan
                    #p_val = p_val
                    
                else:
                    slope_val=slope_val
                    p_val = p_val
                    #p_val = np.nan
                
            except:
                slope_val=np.nan
                p_val = np.nan

            output_trend.append(slope_val)
            output_pvalue.append(p_val)
    
    
    output_trend = np.copy(output_trend).reshape(seasonal_data.lat.size,seasonal_data.lon.size)
    trends = xr.DataArray(output_trend,dims=('lat','lon'),coords={'lat':seasonal_data.lat.values,'lon':seasonal_data.lon.values},name='trends')
    t = (trends*10).sel(lat=slice(-35,10), lon=slice(-75, -30)) 
    t.to_netcdf(output_data_path+'trend/'+indices[k]+'_dec_trend_BR.nc')
    
    
    output_pvalue = np.copy(output_pvalue).reshape(seasonal_data.lat.size,seasonal_data.lon.size)
    pvalues = xr.DataArray(output_pvalue,dims=('lat','lon'),coords={'lat':seasonal_data.lat.values,'lon':seasonal_data.lon.values},name='pvalues')
    p = pvalues.sel(lat=slice(-35,10), lon=slice(-75, -30))
    p.to_netcdf(output_data_path+'pvalue/'+indices[k]+'_dec_pvalue_BR.nc')

    mask_trend = br_mask.mask(t)
    trend_mask = t.where(mask_trend==2)
    
    mask_p = br_mask.mask(p)
    p_mask = p.where(mask_p==2)
    '''
    
    t = xr.open_dataset(output_data_path+'/trend/'+indices[k]+'_dec_trend_BR.nc')
    p = xr.open_dataset(output_data_path+'/pvalue/'+indices[k]+'_dec_pvalue_BR.nc')
    
    mask_trend = br_mask.mask(t)
    trend_mask = t.where(mask_trend==2)
    
    mask_p = br_mask.mask(p)
    p_mask = p.where(mask_p==2)
    
    plt.rcParams['font.family'] = 'Times New Roman' 
    
    fig,ax = plt.subplots(figsize=(20,15),subplot_kw=dict(projection=ccrs.PlateCarree()))
    
    ax.coastlines()
    states = NaturalEarthFeature(category = 'cultural', scale = '50m', 
                                 name = 'admin_1_states_provinces_lines')
    ax.add_feature(states, edgecolor = 'black', facecolor = 'none', linewidth = 0.8, linestyle = '-')
    
    ax.add_geometries(Reader(regions_shape_path).geometries(),
                         ccrs.PlateCarree(),linewidth = 4, edgecolor = 'black', facecolor = 'none')
    
    
    ax.add_geometries(Reader(ocean_shape_path).geometries(),
                         ccrs.PlateCarree(),linewidth = 2, edgecolor = 'black', facecolor = '#83bade')
    
    ax.add_geometries(Reader('data/shapes/transmission_lines.shp').geometries(),
                         ccrs.PlateCarree(),linewidth = 1, edgecolor = 'red', facecolor = 'none',linestyle = '-',alpha=0.5)
    
    ax.set_facecolor('#cdcdcd')
    
    #plt.contourf(trend_mask.lon,trend_mask.lat,trend_mask.trends,transform=ccrs.PlateCarree(), cmap = cmaps[k], levels=levels[k], norm = norms[k], extend = 'both')#levels=np.arange(-2,2.2,0.2),
    plt.contourf(trend_mask.lon,trend_mask.lat,trend_mask.trends,transform=ccrs.PlateCarree(), cmap = cmaps[k], levels=levels[k], extend = 'both')#levels=np.arange(-2,2.2,0.2),

    ax.pcolor(p_mask.lon,p_mask.lat,p_mask.pvalues, hatch='..', zorder=1, alpha=0.0, transform=ccrs.PlateCarree())
    '''
    gl = ax.gridlines(crs = ccrs.PlateCarree(), draw_labels = True, alpha = 0)
    gl.top_labels = False; gl.bottom_labels = True; gl.left_labels = True; gl.right_labels = False
    gl.xpadding = 4; gl.ypadding = 4
    gl.xlabel_style = font_gl; gl.ylabel_style = font_gl
    '''
    gdf.plot(ax=ax, color='#8C001A', marker='s', markersize=35,alpha=0.5)
    plt.rcParams['axes.unicode_minus'] = False    
    
    plt.title(indices[k], fontsize=48, loc='center')
    
    b = plt.colorbar(ticks=ticks[k],shrink=1, pad=0.02, aspect=40,orientation='vertical')#
    b.outline.set_linewidth(1.5)
    b.ax.tick_params(labelsize = 38, width = 1, length = 2, pad = 1)
    b.ax.set_title(labels[k],fontsize=32)
    
    plt.savefig(figure_output_path +indices[k]+'-SpatialTrend_'+'decade_BR.png',dpi = 150, bbox_inches = 'tight')
    
    plt.close()
    

