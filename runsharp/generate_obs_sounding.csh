#!/bin/csh
setenv DISPLAY :5

set stn = $1      # Four letter
set stn = `echo $stn | tr "[a-z]" "[A-Z]"`  #str_to_upper
set dateStr = $2  # YYYYMMDD
set vhr = $3

# echo $stn
# echo $dateStr
# echo $vhr

# Determine what config file to load:
set configFile = 'severe_ml'

set pidDir = "/home/scripts/sharppy/SHARPpy/runsharp/PIDfiles"
#set baseDir = /home/apache/climate/zuranski/sharpraob
set baseDir = /home/data/apachefiles/raob/${stn}/sharppy
set textDir = /home/apache/climate/data/raob/${stn}/text
set pidFil = ${pidDir}/${vhr}_obs_${stn}_pid.txt
set file = ${textDir}/${stn}.${dateStr}.${vhr}.txt
set fileSharp = ${baseDir}/${stn}.sharppy.${dateStr}.${vhr}.png

# Just make sure our destination directory exists:
mkdir -p $baseDir

# Debug info:
# echo $file
# echo $pidFil
# echo $configFile
rm $pidFil

/home/ldm/anaconda/envs/sharppy/bin/python /home/scripts/sharppy/SHARPpy/runsharp/cod_gui2.py $file $pidFil Observed $configFile &

@ counter = 0
set success = "false"
while ($counter < 20)
	if (-f $pidFil) then
		set pid = `awk '{if (NR==1) print}' ${pidFil}`
		set success = "true"
		break
	endif
	sleep .5
	@ counter++
end

if ($success == "false") then
	# We ran out of time, try to clean up.	
	set user = `ps axu | grep ${file} | grep -v grep | awk 'NR==1{print $1}'`
	set pid = `ps axu | grep ${file} | grep -v grep | awk 'NR==1{print $2}'`
	if ($user == 'ldm') then
		kill $pid
	endif

	# Attempt to remove PID file, but it probably doesn't exist:
	rm $pidFil

	# And we're done here.
	exit
endif

echo $pid
if ($pid != "FAIL") then
	echo "Capping"
	import -window root -crop 1180x780+0+20 $fileSharp
	kill $pid
endif

rm $pidFil
