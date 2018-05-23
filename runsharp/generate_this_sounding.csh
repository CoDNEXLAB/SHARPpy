#!/bin/csh
setenv DISPLAY :5
cd /home/scripts/sharppy/SHARPpy/runsharp

set fileName = $1

# Determine what config file to load:
if ($2 != '') then
	set configFile = $2
else
	set configFile = 'severe_ml'
endif

# set file = $1
set pidFil = /home/scripts/sharppy/SHARPpy/runsharp/PIDfiles/thissounding_pid.txt
#set baseDir = /home/data/apachefiles/forecast/sndgs
# set baseDir = /home/apache/climate/junkdrawer/sharppy # Not currently used
#set fileTemp = ${baseDir}/${vhr}_${mod}_${fhr}_raw.txt
set file = $fileName
#set file = http://climate.cod.edu/data/forecast/sndgs/${vhr}_${mod}_${fhr}_${loc}_raw.txt

set fileSharp = ${fileName}.png

#/usr/local/wxp/bin-20131106-OLD/grbsnd -me=fi:${fileTemp} -if=grib_${mod}:x=${fhr} -cf=/home/scripts/wxpsnd/sao.cty -mo=${mod} -cu=la -ho=${vhr} -ft=${fhr} -id=${loc} -pl=none
#mv -f $fileTemp $file

/home/ldm/anaconda/envs/sharppy/bin/python /home/scripts/sharppy/SHARPpy/runsharp/cod_gui.py $file $pidFil Observed $configFile &

@ counter = 0
set success = "false"
while ($counter < 120)
	if (-f $pidFil) then
		set pid = `awk '{if (NR==1) print}' ${pidFil}`
		set success = "true"
		break
	endif
	sleep .5
	@ counter++
end
if ($success == "false") then
	exit
endif

import -window root -crop 1180x780+0+20 $fileSharp
kill $pid
rm $pidFil
