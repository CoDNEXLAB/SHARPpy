
import numpy as np

import sharppy.sharptab.profile as profile
import sharppy.sharptab.prof_collection as prof_collection
from sharppy.io.decoder import Decoder

from StringIO import StringIO
from datetime import datetime

__fmtname__ = "codobs"
__classname__ = "CODObsDecoder"

class CODObsDecoder(Decoder):
    def __init__(self, file_name):
        super(CODObsDecoder, self).__init__(file_name)

    def _parse(self):
        global dyn_inset
	file_data = self._downloadFile()
        ## read in the file
        data = np.array([l.strip() for l in file_data.split('\n')])

        ## necessary index points
        #title_idx = np.where( 'Station:' in data )
        title_idx = np.where( np.char.find(data,'Station:') > -1)[0][0]
        date_idx = np.where( np.char.find(data,'Date: ') > -1 )[0][0]
        start_idx = np.where( np.char.find(data,'SFC') > -1 )[0][0]
        finish_idx = np.where( np.char.find(data,'TRP') > -1 )[0][0]

        ## create the plot title
        location = data[title_idx].split('Station: ')[1]
        data_header = 'Location: ' + location + ' ' + data[date_idx]
        timeStr = str(data[date_idx].split('Date: ')[1]).upper()
        time = datetime.strptime(timeStr, '%H%MZ %d %b %y')

        
        # if time > datetime.utcnow(): #If the strptime accidently makes the sounding the future:
        #     # If the strptime accidently makes the sounding in the future (like with SARS archive)
        #     # i.e. a 1957 sounding becomes 2057 sounding...ensure that it's a part of the 20th century
        #     time = datetime.strptime('19' + data_header[1][:11], '%Y%m%d/%H%M')

        # ---------------------------- Clean up the data ------------------------------#
        # Make sure we have the right number of fields.
        # Commonly at the end of the sounding, wind speed and direciton are missing.
        # This check takes care of that, eliminating a row if it's undersized.

        dirtyData = data[start_idx : (finish_idx)][:]
        cleanData = []
        for line in dirtyData:
            numItems = 0
            items = line.split(' ')
            for item in items:
                if item != '':
                    numItems += 1
            if numItems == 15:
                cleanData.append(line)
        # -----------------------------------------------------------------------------#

        ## put it all together for StringIO
        full_data = '\n'.join(cleanData)
        sound_data = StringIO( full_data )

        ## read the data into arrays
        p, h, T, Td, wdir, wspd = np.genfromtxt( sound_data, unpack=True, usecols=(1,2,3,4,8,9) )
        #idx = np.argsort(p, kind='mergesort')[::-1] # sort by pressure in case the pressure array is off.

        # ----------------------- More Cleaning ----------------------- #
        # SHARPpy doesn't like directions of 360, convert those to 0:
        wdir = [0 if x==360 else x for x in wdir]

        # If there is a duplicate height entry (common),
        # Just add an extra meter, and that'll be our little secret.  ;)
        for key,height in enumerate(h):
            if key == 0:
                continue
            if height == h[key-1]:
                h[key] += 1
        # ------------------------------------------------------------- #

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
        return prof_coll
