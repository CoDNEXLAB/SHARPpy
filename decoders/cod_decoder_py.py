
import sharppy.sharptab.profile as profile
import sharppy.sharptab.prof_collection as prof_collection
from sharppy.io.decoder import Decoder
from sharppy.sharptab import utils

from datetime import datetime, timedelta

import sys
sys.path.append('/home/scripts/fsonde')
import fsonde_decoder


__fmtname__ = "codpy"
__classname__ = "CODDecoderPy"

def writeTimes(file, string):
    time = datetime.now().time()
    time = str(time)
    with open(file, "a") as myfile:
        myfile.write(string+' '+time)

class CODDecoderPy(Decoder):
    def __init__(self, file_name):
        super(CODDecoderPy, self).__init__(file_name)

    def _parse(self):

        # time = datetime.now()

        file_data = self._downloadFile()
        modInit, modName, fHour, coords = file_data.split(' ')
        # if len(modInit) == 2:
        #     import time
        #     modInit = time.strftime('%Y%m%d')+modInit

        locationStr = coords.strip('\n')

        textFile = '/home/apache/climate/data/forecast/sndgs/'+modInit+'_'+modName+'_'+fHour+'_'+coords.strip('\n')+'_raw.txt'
        #writeTimes(textFile, 'Begin')

        data_header = 'Location: '

        time = datetime.strptime(modInit, '%Y%m%d%H') + timedelta(hours=int(fHour))

        # Determine if it's a site ID:
        if ',' not in coords:
            import numpy as np
            sites, siteCoords = np.genfromtxt('/home/apache/climate/hanis/model/fsound/text/sid.txt', dtype=str, unpack=True, delimiter=' ')
            i = np.where(sites == 'KORD')
            coords = siteCoords[i[0][0]]

        variables = fsonde_decoder.decode(modInit, modName, fHour, coords)
        #writeTimes(textFile, 'After Decode')

        pres = variables['pres']
        hght = variables['hght']
        tmpc = variables['temp']
        dwpc = variables['dewp']
        u = variables['ugrd']
        v = variables['vgrd']
        omeg = variables['omeg']
        
        wdir, wspd = utils.comp2vec(u, v)
        # wspd = [s*1.94384 for s in wspd]

        # Force latitude to be 35 N. Figure out a way to fix this later.
        prof = profile.create_profile(profile='raw', pres=pres, hght=hght, tmpc=tmpc, dwpc=dwpc, wdir=wdir, wspd=wspd, omeg=omeg, location=locationStr, date=time, latitude=35.)
        prof_coll = prof_collection.ProfCollection({'':[ prof ]},[ time ],)
        prof_coll.setMeta('loc', locationStr)
        #writeTimes(textFile, 'End')
        return prof_coll
