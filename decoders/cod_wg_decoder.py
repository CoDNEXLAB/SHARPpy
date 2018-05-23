
import numpy as np

import sharppy.sharptab.profile as profile
import sharppy.sharptab.prof_collection as prof_collection
from sharppy.io.decoder import Decoder

from StringIO import StringIO
from datetime import datetime

__fmtname__ = "cod_wg"
__classname__ = "CODDecoderWG"

class CODDecoderWG(Decoder):
    def __init__(self, file_name):
        super(CODDecoderWG, self).__init__(file_name)

    def _parse(self):
        global dyn_inset
        file_data = self._downloadFile()
        ## read in the file
        # print "WG"
        data = np.array([l.strip() for l in file_data.split('\n')])

        ## necessary index points
        #title_idx = np.where( 'Station:' in data )
        # title_idx = np.where( np.char.find(data,'Station: ') > -1)[0][0]
        # date_idx = np.where( np.char.find(data,'Date: ') > -1 )[0][0]
        date_line = data[0]
        title_line = data[1]
        start_idx = (np.where( np.char.find(data,'DATASTART') > -1 )[0][0]) + 1
        finish_idx = np.where( np.char.find(data,'DATAEND') > -1 )[0][0]

        ## create the plot title        
        location = title_line
        timeStr = str(date_line.split('valid ')[1])
        time = datetime.strptime(timeStr, '%HZ %a %d %b %y')
        #     time = datetime.strptime(timeStr, '%HZ %a %d %b %y')
        # location = data[title_idx].split('Station: ')[1]
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

        #print full_data

        ## read the data into arrays
        #p, h, T, Td, wdir, wspd = np.genfromtxt( sound_data, unpack=True, usecols=(1,2,3,4,8,9) )
        p, T, Td, h, wspd, wdir = np.genfromtxt( sound_data, unpack=True, usecols=(0,1,2,3,4,5) )
        #idx = np.argsort(p, kind='mergesort')[::-1] # sort by pressure in case the pressure array is off.

        pres = p #[idx]
        hght = h #[idx]
        tmpc = T #[idx]
        dwpc = Td #[idx]
        wspd = wspd #[idx]
        wdir = wdir #[idxi]
	if dwpc[0] < 40:
		dyn_inset = 'winter'
	else:
		dyn_inset = 'severe'

        # Force latitude to be 35 N. Figure out a way to fix this later.
        prof = profile.create_profile(profile='raw', pres=pres, hght=hght, tmpc=tmpc, dwpc=dwpc, wdir=wdir, wspd=wspd, location=location, date=time, latitude=35.)
        prof_coll = prof_collection.ProfCollection({'':[ prof ]},[ time ],)
        prof_coll.setMeta('loc', location)
        print "Using WG decoder."
        return prof_coll
