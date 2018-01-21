'''Forecast Weather Data Plots'''

from mpl_toolkits.basemap import Basemap
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import wxdata

MODEL = 'GFS'
DATE_INIT = '20180120'
CYCLE = '18'
TITLE = 'Precipitation Type'
FPREFIX = 'ptype'
AREA = wxdata.WISCONSIN

FILENAME = wxdata.model(MODEL, DATE_INIT, CYCLE)
CONTENTS = wxdata.openfile(FILENAME)
TIME = wxdata.time(CONTENTS)
DOMAIN = wxdata.geodomain(CONTENTS, AREA.coords)

LATS = DOMAIN[0]
LONS = DOMAIN[1]
MAPWIDTH = AREA.mapdimensions()[0]
MAPHEIGHT = AREA.mapdimensions()[1]
LOWER_LAT = AREA.llat
UPPER_LAT = AREA.ulat
LLAT_I = DOMAIN[2]
ULAT_I = DOMAIN[3]
LLON_I = DOMAIN[4]
RLON_I = DOMAIN[5]
CENTERPT_LAT = AREA.centerpoint()[0]
CENTERPT_LON = AREA.centerpoint()[1]

VALIDTIMES = TIME[0]
TIMESTEP = 0
TIMESTEPS = TIME[1]

BASEMAP = Basemap(width=MAPWIDTH, height=MAPHEIGHT,
                  rsphere=(6378137.00, 6356752.3142),
                  resolution='l', area_thresh=1000., projection='lcc',
                  lat_1=LOWER_LAT, lat_2=UPPER_LAT,
                  lat_0=CENTERPT_LAT, lon_0=CENTERPT_LON)

X, Y = BASEMAP(* np.meshgrid(LONS, LATS))


def mapfeatures():
    '''Defines how the map will look'''
    #BASEMAP.drawcoastlines(linewidth=0.75, zorder=5)
    BASEMAP.fillcontinents(color='#e6e6e6', lake_color='#b3ffff')
    #BASEMAP.drawcountries(linewidth=1.0, zorder=7)
    BASEMAP.readshapefile('../../GIS/us_states/cb_2016_us_state_5m', 'states',
                          linewidth=0.75, zorder=10)
    BASEMAP.readshapefile('../../GIS/wi_county/co55_d00', 'counties',
                          zorder=6, linewidth=0.3, color='gray')
    BASEMAP.drawmapboundary(fill_color='#b3ffff')


def mapfigure(title, fprefix):
    '''Generate image on the disk'''
    plt.title(title + '\n' + VALIDTIMES[TIMESTEP] + '')
    plt.savefig(fprefix + str(TIMESTEP) + '.png', dpi=300, bbox_inches='tight')
    print('Finished creating image', TIMESTEP)


def plotprecip():
    '''Plot precipitation type areas'''
    rain = CONTENTS.variables['crainsfc'][TIMESTEP, LLAT_I:ULAT_I, LLON_I:RLON_I]
    snow = CONTENTS.variables['csnowsfc'][TIMESTEP, LLAT_I:ULAT_I, LLON_I:RLON_I]
    sleet = CONTENTS.variables['cicepsfc'][TIMESTEP, LLAT_I:ULAT_I, LLON_I:RLON_I]
    frzrain = CONTENTS.variables['cfrzrsfc'][TIMESTEP, LLAT_I:ULAT_I, LLON_I:RLON_I]
    clevs = [0.25, 1]

    BASEMAP.contourf(X, Y, rain, clevs, colors='#00b300', zorder=4)
    BASEMAP.contourf(X, Y, snow, clevs, colors='#8080ff', zorder=4)
    BASEMAP.contourf(X, Y, sleet, clevs, colors='#ffcc80', zorder=4)
    BASEMAP.contourf(X, Y, frzrain, clevs, colors='#ff80bf', zorder=4)

    snow_patch = mpatches.Patch(color='#8080ff', label='Snow')
    sleet_patch = mpatches.Patch(color='#ffcc80', label='Sleet')
    frzrain_patch = mpatches.Patch(color='#ff80bf', label='Frz Rain')
    rain_patch = mpatches.Patch(color='#00b300', label='Rain')
    legend = plt.legend(handles=[snow_patch, sleet_patch,
                                 frzrain_patch, rain_patch])
    legend.set_zorder(10)


for TIMESTEP in range(0, TIMESTEPS):
    plt.figure()
    plotprecip()
    mapfeatures()
    mapfigure(TITLE, FPREFIX)

wxdata.closefile(CONTENTS)
print('The program has completed.')
