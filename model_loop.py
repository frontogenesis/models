# NOMADS OpenDAP extraction and plotting script
# Modified by:  Ray Hawthorne

##################
# Import Modules #
##################
from mpl_toolkits.basemap import Basemap
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import netCDF4
from netCDF4 import num2date
from dateutil import parser, tz
from datetime import datetime
from ncdump import ncdump

########################################
# Define geographical domain and model #
########################################
lower_lat = 37.0
upper_lat = 50.0
left_lon  = -105
right_lon = -82
select_model = 'narre'

centerpt_lat = (lower_lat + upper_lat) / 2 #Calculate centerpoint lat
centerpt_lon = (left_lon + right_lon) / 2  #Calculate centerpoint lon
mapwidth  = abs((left_lon-right_lon)*81541)   #Calculate approx mapwidth
mapheight = abs((upper_lat-lower_lat)*111092) #Calculate approx mapheight

##################################################
# Retrieve today's date in UTC                   #
# Define the model cycle you want (00Z,12Z,etc.) #
##################################################
mydate = datetime.utcnow().strftime("%Y%m%d")
#mydate = str(20160323)
cycle  = '00'

###########################################
# Define model dataset from NOMADS server #
# Comment out the datasets you don't want #
###########################################
model = {'gfs'  : 'gfs_0p25/gfs'+mydate+'/gfs_0p25_'+cycle+'z',
         'arw'  : 'hiresw/hiresw'+mydate+'/hiresw_conusarw_'+cycle+'z',
         'nmm'  : 'hiresw/hiresw'+mydate+'/hiresw_conusnmmb_'+cycle+'z',
         'hrrr' : 'hrrr/hrrr'+mydate+'/hrrr_sfc_'+cycle+'z',
         'narre': 'narre/narre'+mydate+'/narre_130_mean_'+cycle+'z',
         'nww3' : 'wave/nww3/nww3'+mydate+'/nww3'+mydate+'_'+cycle+'z',
         'nam4k': 'nam/nam'+mydate+'/nam1hr_'+cycle+'z',
         'rap'  : 'rap/rap'+mydate+'/rap_'+cycle+'z'}

select_model = model.get(select_model,0)

########################################
# Define NOMADS Data URL               #
# Include model you want at end of URL #
########################################
url = 'http://nomads.ncep.noaa.gov:9090/dods/'+select_model
print 'URL:',url

#################
# Create lists #
################
validtimes = list()

#############################################################
# Build function to extract array index from lat/lon points #
# Define domain over which to plot the weather data         #
#############################################################
def getnearpos(array,value):
    idx = (np.abs(array-value)).argmin()
    return idx

##########################################
# Extract variables from the NETCDF file #
# Count the number of timesteps          #
# Convert valid times to UTC and local   #
##########################################
file = netCDF4.Dataset(url)
print 'File opened successfully! Processing data...'
lats  = file.variables['lat'][:]
lons  = file.variables['lon'][:]
lower_lat_idx = getnearpos(lats,lower_lat)
upper_lat_idx = getnearpos(lats,upper_lat)
left_lon_idx = getnearpos(lons,left_lon)
right_lon_idx = getnearpos(lons,right_lon)
lats = lats[lower_lat_idx:upper_lat_idx]
lons = lons[left_lon_idx:right_lon_idx]

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

i = -1
while i < timesteps:
    i = i+1
    print 'Creating image',i,'...'
    rain = file.variables['crainsfc'][0,i,lower_lat_idx:upper_lat_idx,
    left_lon_idx:right_lon_idx]
    snow = file.variables['csnowsfc'][0,i,lower_lat_idx:upper_lat_idx,
    left_lon_idx:right_lon_idx]
    sleet = file.variables['cicepsfc'][0,i,lower_lat_idx:upper_lat_idx,
    left_lon_idx:right_lon_idx]
    frzrain = file.variables['cfrzrsfc'][0,i,lower_lat_idx:upper_lat_idx,
    left_lon_idx:right_lon_idx]
    #qpf = file.variables['apcpl255'][i,lower_lat_idx:upper_lat_idx,
    #left_lon_idx:right_lon_idx]
    plt.figure()

#############################################################
# Plot the field using Basemap.  Start with setting the map #
# projection using the limits of the lat/lon data itself:   #
#############################################################
    m = Basemap(width=mapwidth,height=mapheight,\
                rsphere=(6378137.00,6356752.3142),\
                resolution='i',area_thresh=1000.,projection='lcc',\
                lat_1=lower_lat,lat_2=upper_lat,\
                lat_0=centerpt_lat,lon_0=centerpt_lon)

#################################################
# convert the lat/lon values to x/y projections #
#################################################
    x,y = m(*np.meshgrid(lons,lats))

# plot the field using the fast pcolormesh routine
# set the colormap to jet.
    clevs = [0.25,1]
    #clevs = [0.01,0.05,0.10,0.25,0.50,0.75,1.00,1.50,2.00,5.00]
    m.contourf(x,y,rain,clevs,colors='#00b300',zorder=4)
    m.contourf(x,y,snow,clevs,colors='#8080ff',zorder=4)
    m.contourf(x,y,sleet,clevs,colors='#ffcc80',zorder=4)
    m.contourf(x,y,frzrain,clevs,colors='#ff80bf',zorder=4)
    #m.contour(x,y,qpf/25.4,clevs,linewidths=[1],zorder=5)

    #m.pcolormesh(x,y,data,shading='flat',cmap=plt.cm.jet)

# Add legend patches
    snow_patch = mpatches.Patch(color='#8080ff', label='Snow')
    sleet_patch = mpatches.Patch(color='#ffcc80', label='Sleet')
    frzrain_patch = mpatches.Patch(color='#ff80bf', label='Frz Rain')
    rain_patch = mpatches.Patch(color='#00b300', label='Rain')
    l = plt.legend(handles=[snow_patch,sleet_patch,frzrain_patch,rain_patch])
    l.set_zorder(10)

################################################
# Build Map Features, like continents, states, #
# lat/lon lines, and other physical features   #
################################################
    m.drawcoastlines(linewidth=0.75,zorder=5)
    m.fillcontinents(color='#e6e6e6',lake_color='#b3ffff')
    m.drawcountries(linewidth=1.0,zorder=7)
    m.drawstates(linewidth=0.75,zorder=6)
    m.drawcounties(linewidth=0.3,color='gray',zorder=5)
    m.drawmapboundary(fill_color='#b3ffff')
    #m.drawparallels(np.arange(-90.,120.,30.),labels=[1,0,0,0])
    #m.drawmeridians(np.arange(-180.,180.,60.),labels=[0,0,0,1])

##############################################
# Add a title, and then show the plot.       #
# Save the plot as images to disk if desired #
##############################################
    plt.title('Precipitation Type \n'+validtimes[i]+'')
    plt.savefig('basemap'+str(i)+'.png', dpi=300, bbox_inches='tight')
    print 'Finished creating image',i
    #plt.show()

file.close()
print 'The program has completed. Enjoy your day!'
