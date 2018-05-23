<?php
$location = $argv[1];

$foundSite = false;
if (!strstr($location, ',')) { // easy way to identitfy lat/lon vs ID
	if (strlen($location) === 3) {
		$location = 'K'.$location;  // Let's just assume this, k?
	}
	$location = strtoupper($location);
	if (preg_match("/[A-Z]{4}/", $location)) {
		// This is a site ID, find the location:
		$stations = file('/home/apache/climate/hanis/model/fsound/text/sid.txt');
		foreach ($stations as $key => $station) {
			list($site,$coords) = explode(' ', $station);
			if ($site === $location) {
				#list($lat,$lon) = explode(',', trim($coords));
				print $coords;
				$foundSite = true;
				break;
			}
		}
	}
	if (!$foundSite) {
		die("Site could not be found.");
	}
}
?>