#!/bin/csh
setenv DISPLAY :5

set vhr = $1
set mod = $2
set fhr = $3
set loc = $4

if ($vhr < 30) then
	set modDate = `date +"%Y%m%d"`
	set vhr = $modDate$vhr
endif

# Determine what config file to load:
if ($5 != '') then
	set configFile = $5
else
	set configFile = 'severe_ml'
endif

# set file = $1
set pidDir = "/home/scripts/sharppy/SHARPpy/runsharp/PIDfiles"
set baseDir = /home/apache/climate/data/forecast/sndgs
set pidFil = ${pidDir}/${vhr}_${mod}_${fhr}_${loc}_pid.txt
set file = ${baseDir}/${vhr}_${mod}_${fhr}_${loc}_vars.txt
set textFileTemp = ${baseDir}/${vhr}_${mod}_${fhr}_raw.txt
set textFile = ${baseDir}/${vhr}_${mod}_${fhr}_${loc}_raw.txt

set fileSharp = ${baseDir}/${vhr}_${mod}_${fhr}_${loc}_${configFile}.png

#set fileTemp = ${baseDir}/${vhr}_${mod}_${fhr}_raw.txt
#/usr/local/wxp/bin-20131106-OLD/grbsnd -me=fi:${fileTemp} -if=grib_${mod}:x=${fhr} -cf=/home/scripts/wxpsnd/sao.cty -mo=${mod} -cu=la -ho=${vhr} -ft=${fhr} -id=${loc} -pl=none
#mv -f $fileTemp $file
if ($mod == "NAMNST") then
	# Need this check, otherwise grbsnd will load NAM for NAM4KM.  Stupid WXP.
	set textMod = "NST"
else
	set textMod = $mod
endif
set textVhr = `echo ${vhr} | cut -c9-10`
echo "/usr/local/wxp/bin-20131106-OLD/grbsnd -me=fi:${textFileTemp} -if=grib_${textMod}:x=${fhr} -cf=/home/scripts/wxpsnd/sao.cty -mo=${textMod} -cu=la -ho=${textVhr} -ft=${fhr} -id=${loc} -pl=none; mv -f ${textFileTemp} ${textFile}"
/usr/local/wxp/bin-20131106-OLD/grbsnd -me=fi:${textFileTemp} -if=grib_${textMod}:x=${fhr} -cf=/home/scripts/wxpsnd/sao.cty -mo=${textMod} -cu=la -ho=${textVhr} -ft=${fhr} -id=${loc} -pl=none; mv -f ${textFileTemp} ${textFile} &

# Stupid Alaska:
if ($mod == "ALK") then
	set file = ${baseDir}/${vhr}_NAM_${fhr}_${loc}_vars.txt
	set fileSharp = ${baseDir}/${vhr}_NAM_${fhr}_${loc}_${configFile}.png
endif

if ($loc:q !~ *','*) then
	set loc = `/usr/bin/php /home/scripts/sharppy/sharppy-master/runsharp/site2coord.php $loc`
endif

echo "$vhr $mod $fhr $loc" > $file

echo $file
echo $pidFil
echo $mod
echo $configFile

/home/ldm/anaconda/envs/sharppy/bin/python /home/scripts/sharppy/SHARPpy/runsharp/cod_gui.py $file $pidFil $mod $configFile &

@ counter = 0
set success = "false"
while ($counter < 120)
	if (-f $pidFil) then
		set pid = `awk '{if (NR==1) print}' ${pidFil}`
		if ($pid != "FAIL") then
			set success = "true"
		endif
		break
	endif
	sleep .5
	@ counter++
end

if ($success == "false") then
	# We ran out of time, try to clean up.	
	set user = `ps axu | grep ${file} | grep -v grep | awk 'NR==1{print $1}'`
	set pid = `ps axu | grep ${file} | grep -v grep | awk 'NR==1{print $2}'`
	if ($user == 'www-data') then
		kill $pid
	endif

	# Attempt to remove PID file, but it probably doesn't exist:
	rm $pidFil

	# And we're done here.
	exit
endif

import -window root -crop 1180x780+0+20 $fileSharp
rm $pidFil
rm $file

kill $pid
