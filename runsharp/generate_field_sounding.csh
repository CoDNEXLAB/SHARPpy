#!/bin/csh
setenv DISPLAY :5

set dateStr = $1
set loc = $2

# Determine what config file to load:
if ($3 != '') then
	set configFile = $3
else
	set  = 'severe_eff'
endif

# set file = $1
set baseDir = /home/apache/climate/data/forecast/sndgs
set pidFil = ${dateStr}_${loc}_pid.txt
set file = /home/apache/climate/sonde/submitted/${dateStr}.${loc}.txt

set fileSharp = ${baseDir}/${dateStr}_${loc}_${configFile}.png

/home/ldm/anaconda/envs/sharppy/bin/python /home/scripts/sharppy/SHARPpy/runsharp/codfield_gui.py $file $pidFil $configFile &

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
	rm $pidFil
	exit
endif

import -window root -crop 1180x780+0+20 $fileSharp
rm $pidFil

kill $pid
