'''GET NOMADS OPENDAP MODEL DATA'''

import netCDF4
import numpy as np
from dateutil import tz

def model(select_model, date, cycle):
    '''Define model URLs on NOMADS OpenDAP server'''

    model_urls = {
        'GFS': 'gfs_0p25/gfs' + date + '/gfs_0p25_' + cycle + 'z',
        'GFSH': 'gfs_0p25_1hr' + '/gfs' + date + '/gfs_0p25_1hr_' + cycle + 'z',
        'ARW': 'hiresw/hiresw' + date + '/hiresw_conusarw_' + cycle + 'z',
        'NMM': 'hiresw/hiresw' + date + '/hiresw_conusnmmb_' + cycle + 'z',
        'HRRR': 'hrrr/hrrr' + date + '/hrrr_sfc_' + cycle + 'z',
        'NARRE': 'narre/narre' + date + '/narre_130_mean_' + cycle + 'z',
        'NWW3': 'wave/nww3/nww3' + date + '/nww3' + date + '_' + cycle + 'z',
        'NAM3K': 'nam/nam' + date + '/nam1hr_' + cycle + 'z',
        'RAP': 'rap/rap' + date + '/rap_' + cycle + 'z'
    }

    select_model = model_urls.get(select_model, 0)
    url = 'http://nomads.ncep.noaa.gov:9090/dods/' + select_model

    return url

def openfile(netcdf):
    '''Read netcdf file'''
    netcdf4 = netCDF4.Dataset(netcdf)
    return netcdf4

def closefile(netcdf):
    '''Close netcdf file'''
    netcdf.close()

def getnearpos(array, value):
    '''Retrieve nearest index value from lat/lon'''
    idx = (np.abs(array - value)).argmin()
    return idx

def geodomain(netcdf, coords):
    '''Calculate geographical domain'''
    lats = netcdf.variables['lat'][:]
    lons = netcdf.variables['lon'][:]
    llat = coords[0]
    ulat = coords[1]
    llon = coords[2]
    rlon = coords[3]

    llat_idx = getnearpos(lats, llat)
    ulat_idx = getnearpos(lats, ulat)
    llon_idx = getnearpos(lons, llon)
    rlon_idx = getnearpos(lons, rlon)

    lats_domain = lats[llat_idx : ulat_idx]
    lons_domain = lons[llon_idx : rlon_idx]

    return lats_domain, lons_domain, llat_idx, ulat_idx, llon_idx, rlon_idx

def time(netcdf):
    '''Retrieve valid forecast times'''
    times = netcdf.variables['time'][:]
    timeunits = netcdf.variables['time'].units
    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz('America/Chicago')

    validtimes = []
    for timesteps, validtime in enumerate(times):
        validtime = netCDF4.num2date(validtime, units=timeunits)
        validtime = validtime.replace(tzinfo=from_zone)
        validtime = validtime.astimezone(to_zone)
        validtime = validtime.strftime('%-I %p CT, %A, %B %-d, %Y')
        validtimes.append(validtime)
    timesteps = len(validtimes)

    return validtimes, timesteps

class Geography(object):
    '''Define Geographic Domains for maps'''

    def __init__(self, llat, ulat, llon, rlon):
        self.llat = llat
        self.ulat = ulat
        self.llon = llon
        self.rlon = rlon
        self.coords = (llat, ulat, llon, rlon, )

    def centerpoint(self):
        '''Calculate centerpoint of map domain'''
        latitude = (self.llat + self.ulat) / 2
        longitude = (self.llon + self.rlon) / 2
        return latitude, longitude

    def mapdimensions(self):
        '''Calculate Map Width and Map Height to fit weather data'''
        mapwidth = abs((self.llon - self.rlon) * 70000)
        mapheight = abs((self.ulat - self.llat) * 100000)
        return mapwidth, mapheight

WISCONSIN = Geography(41.5, 47.5, -94.0, -86.3)
MIDWEST = Geography(37.0, 50.0, -105.0, -82.0)

# Global models, like the GFS, require lons between 0 and 360
WISCONSIN_GLOBAL = Geography(41.5, 47.5, 266.0, 273.7)
MIDWEST_GLOBAL = Geography(37.0, 50.0, 255.0, 278.0)

# AREA = WISCONSIN
# FILENAME = model('RAP', '20180120', '06')
# CONTENTS = openfile(FILENAME)
# DOMAIN = geodomain(CONTENTS, AREA.coords)
# TIME = time(CONTENTS)

# closefile(CONTENTS)
