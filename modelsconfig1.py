
import numpy as np
import matplotlib as mpl
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
from matplotlib import cm
import netCDF4
from netCDF4 import num2date
from dateutil import parser, tz
from datetime import datetime
from ncdump import ncdump
from subprocess import call
import os

# Parameters
select_model = 'hrrr'

# Retrieve model data from NOMADS server
def getmodel(select_model):
    datetoday = datetime.utcnow().strftime('%Y%m%d')
    mydate = raw_input('Enter YYYYMMDD: ') or datetoday
    mydate = str(mydate)
    cycle = raw_input('Enter UTC time: ')

    model = {
        'gfs'  : 'gfs_0p25/gfs'+mydate+'/gfs_0p25_'+cycle+'z',
        'arw'  : 'hiresw/hiresw'+mydate+'/hiresw_conusarw_'+cycle+'z',
        'nmm'  : 'hiresw/hiresw'+mydate+'/hiresw_conusnmmb_'+cycle+'z',
        'hrrr' : 'hrrr/hrrr'+mydate+'/hrrr_sfc_'+cycle+'z',
        'narre': 'narre/narre'+mydate+'/narre_130_mean_'+cycle+'z',
        'nww3' : 'wave/nww3/nww3'+mydate+'/nww3'+mydate+'_'+cycle+'z',
        'nam-hires': 'nam/nam'+mydate+'/nam_conusnest_'+cycle+'z',
        'rap'  : 'rap/rap'+mydate+'/rap_'+cycle+'z'
        }

    model_path = model.get(select_model,0)

    print 'Retrieving file...'
    url = 'http://nomads.ncep.noaa.gov:9090/dods/'+model_path
    print 'URL:', url

    global file
    file = netCDF4.Dataset(url)

    return select_model, url, file

# Calculate local times
def gettimes():
    validtimes = list()
    getmodel(select_model)
    time = file.variables['time'][:]
    timeunits = file.variables['time'].units
    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz('America/Chicago')
    for timesteps,validtime in enumerate(time):
        validtime = num2date(validtime,units=timeunits)
        validtime = validtime.replace(tzinfo=from_zone)
        validtime = validtime.astimezone(to_zone)
        validtime = validtime.strftime('%I %p CT, %A, %B %d, %Y')
        validtimes.append(validtime)

    return timesteps, validtimes

# Extract nearest array index from lat/lon points
def getnearpos(array, value):
    idx = (np.abs(array - value)).argmin()
    return idx

# Calculate lat/lon index
def mapindex():
    validtimes = list()
    lats  = file.variables['lat'][:]
    lons  = file.variables['lon'][:]
    lower_lat_idx = getnearpos(lats,lower_lat)
    upper_lat_idx = getnearpos(lats,upper_lat)
    left_lon_idx = getnearpos(lons,left_lon)
    right_lon_idx = getnearpos(lons,right_lon)
    lats = lats[lower_lat_idx:upper_lat_idx]
    lons = lons[left_lon_idx:right_lon_idx]

# Based on the domain, calculate the centerpoint latitude,
# centerpoint longitude, mapwidth, and mapheight
def mapdims(llat, ulat, llon, rlon):
    centerpt_lat = (llat + ulat) / 2
    centerpt_lon = (llon + rlon) / 2
    mapwidth = abs((llon - rlon) * 81541)
    mapheight = abs((ulat - llat) * 111092)
    return centerpt_lat, centerpt_lon, mapwidth, mapheight

#def drawlatlon():
    #m.drawparallels(np.arange(20,60,10),labels=[1,1,0,0])
    #m.drawmeridians(np.arange(-120,-60,20),labels=[0,0,0,1])

# Map Banner
def mapbanner(title):
    plt.title(''+title+'\n', fontsize=14, fontweight='bold')
    plt.title('\nValid '+validtimes[i]+'', fontsize=8, loc='left')
    plt.title('\nModel: NCEP '+str.upper(select_model)+'', fontsize=8,
              loc='right')

# Animated GIF using ImageMagick
def animated_gif(select_model, i):
    print 'Creating animated GIF'
    call(["convert","-delay","80","-loop","0",""+select_model+"*.png","-delay",
         "200","-loop","0",""+select_model+str(i)+".png","-resize","1024x512",
         ""+select_model+".gif"],cwd=select_model)
    print 'Finished creating animated GIF'

def mp4(select_model):
    print 'Creating MP4'
    call(["ffmpeg", "-framerate", "1/1", "-i", ""+select_model+"%02d.png",
         "-vcodec", "libx264", "-crf","25", "-pix_fmt", "yuv420p", "-y", "-vf",
         "scale=1024:512", ""+select_model+".mp4"], cwd=select_model)
    print 'Finished creating MP4'

# Define preset mapviews for ease of use
class Maps(object):
    @staticmethod
    def local():
        lower_lat = 41.6
        upper_lat = 44.4
        left_lon  = -92.2
        right_lon = -87.0
        return lower_lat, upper_lat, left_lon, right_lon
