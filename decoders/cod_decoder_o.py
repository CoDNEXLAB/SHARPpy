
import numpy as np

import sharppy.sharptab.profile as profile
import sharppy.sharptab.prof_collection as prof_collection
from sharppy.io.decoder import Decoder

from StringIO import StringIO
from datetime import datetime

__fmtname__ = "codomega"
__classname__ = "CODOmegaDecoder"

class CODOmegaDecoder(Decoder):
    def __init__(self, file_name):
        super(CODOmegaDecoder, self).__init__(file_name)

    def _parse(self):
        global dyn_inset
        file_data = self._downloadFile()
        ## read in the file
        data = np.array([l.strip() for l in file_data.split('\n')])

        ## necessary index points
        #title_idx = np.where( 'Station:' in data )
        date_idx = data[0]
        title_idx = data[1]
        #print date_idx
        #print title_idx
        start_idx = (np.where( np.char.find(data,'OMEGASTART') > -1 )[0][0]) + 1
        #print data[start_idx]
        finish_idx = np.where( np.char.find(data,'OMEGAEND') > -1 )[0][0]

        ## create the plot title
        location = title_idx
        time = datetime.strptime(date_idx, '%a %d %b %Y | %H%M UTC')
        #print time.strftime('%Y %M %d %H')

        # data_header = 'Location: ' + location + ' ' + data[date_idx]
        # if 'analysis' in data[date_idx]:
        #     #print "analysis"
        #     timeStr = str(data[date_idx].split('for ')[1]).upper()
        #     time = datetime.strptime(timeStr, '%H%MZ %d %b %y')
        # else:
        #     #print "forecast"
        #     timeStr = str(data[date_idx].split('valid ')[1]).upper()
        #     time = datetime.strptime(timeStr, '%HZ %a %d %b %y')

        
        # if time > datetime.utcnow(): #If the strptime accidently makes the sounding the future:
        #     # If the strptime accidently makes the sounding in the future (like with SARS archive)
        #     # i.e. a 1957 sounding becomes 2057 sounding...ensure that it's a part of the 20th century
        #     time = datetime.strptime('19' + data_header[1][:11], '%Y%m%d/%H%M')

        ## put it all together for StringIO
        full_data = '\n'.join(data[start_idx : finish_idx][:])
        sound_data = StringIO( full_data )


        #print datetime.strftime('%Y %m %d %H',time)

        #full_data = np.array(full_data)
        #print sound_data

        ## read the data into arrays
        p, T, Td, h, wspd, wdir, omeg = np.genfromtxt( sound_data, unpack=True, usecols=(0,1,2,3,4,5,6) )
        #idx = np.argsort(p, kind='mergesort')[::-1] # sort by pressure in case the pressure array is off.


        pres = p #[idx]
        hght = h #[idx]
        tmpc = T #[idx]
        dwpc = Td #[idx]
        wspd = wspd #[idx]
        wdir = wdir #[idxi]
        omeg = omeg #[idx]
        print omeg
        if dwpc[0] < 40:
            dyn_inset = 'winter'
        else:
            dyn_inset = 'severe'

        # Force latitude to be 35 N. Figure out a way to fix this later.
        prof = profile.create_profile(profile='raw', pres=pres, hght=hght, tmpc=tmpc, dwpc=dwpc, wdir=wdir, wspd=wspd, omeg=omeg, location=location, date=time, latitude=35.)
        prof_coll = prof_collection.ProfCollection({'':[ prof ]},[ time ],)
        prof_coll.setMeta('loc', location)
        print "Using Omega Decoder."
        return prof_coll
