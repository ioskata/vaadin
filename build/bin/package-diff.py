#!/usr/bin/python

import sys,os
from sets import Set

################################################################################
# Configuration
################################################################################
downloadsite = "http://vaadin.com/download"
latestfile   = "/LATEST"

################################################################################
# Utility Functions
################################################################################
def command(cmd, dryrun=0):
	if not dryrun:
		if os.system(cmd):
			print "Command '%s' failed, exiting." % (cmd)
			sys.exit(1)
	else:
		print "Dry run - not executing."

################################################################################
# List files in an archive.
################################################################################
def listfiles(archive):
	pin = os.popen("tar ztf %s | sort" % (archive), "r")
	files = map(lambda x: x.strip(), pin.readlines())
	pin.close()

	cleanedfiles = []
	for file in files:
		# Remove archive file name from the file names
		slashpos = file.find("/")
		if slashpos != -1:
			cleanedname = file[slashpos+1:]
		else:
			cleanedname = file

		# Purge GWT compilation files.
		if cleanedname.find(".cache.html") != -1:
			continue
		
		cleanedfiles.append(cleanedname)

	return cleanedfiles

################################################################################
# Difference of two lists of files
################################################################################
def diffFiles(a, b):
	diff = Set(a).difference(Set(b))
	difffiles = []
	for item in diff:
		difffiles.append(item)
	difffiles.sort()
	return difffiles

################################################################################
#
################################################################################

# Download the installation package of the latest version
wgetcmd = "wget -q -O - %s" % (downloadsite+latestfile)
pin = os.popen(wgetcmd, "r")
latestdata = pin.readlines()
pin.close()

latestversion  = latestdata[0].strip()
latestpath     = latestdata[1].strip()
latestURL      = downloadsite + "/" + latestpath + "/"
linuxfilename  = "vaadin-linux-%s.tar.gz" % (latestversion)
linuxpackage   = latestURL + linuxfilename
locallinuxpackage = "/tmp/%s" % (linuxfilename)

print "Latest version:      %s" % (latestversion)
print "Latest version path: %s" % (latestpath)
print "Latest version URL:  %s" % (latestURL)

# Check if it already exists
try:
	os.stat(locallinuxpackage)
	print "Latest package already exists in %s" % (locallinuxpackage)
	# File exists
except OSError:
	# File does not exist, get it.
	print "Downloading Linux package %s to %s" % (linuxpackage, locallinuxpackage)
	wgetcmd = "wget -q -O %s %s" % (locallinuxpackage, linuxpackage)
	command (wgetcmd)

# List files in latest version.
latestfiles  = listfiles(locallinuxpackage)

# List files in built version.
builtversion = sys.argv[1]
builtpackage = "build/result/vaadin-linux-%s.tar.gz" % (builtversion)
builtfiles = listfiles(builtpackage)

# Report differences

# New files
newfiles = diffFiles(builtfiles, latestfiles)
print "\n%d new files:" % (len(newfiles))
for item in newfiles:
	print item

# Removed files
removed = diffFiles(latestfiles, builtfiles)
print "\n%d removed files:" % (len(removed))
for item in removed:
	print item

# Purge downloaded package
command("rm %s" % (locallinuxpackage))
