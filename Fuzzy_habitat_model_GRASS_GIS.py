#!/usr/bin/env python
#
############################################################################
#
# SCRIPT:       Fish Habitat Modell, r.fuzzy.system habitat modell
#				For testing various combinations of Depth and Velocity
#				and the corresponding species-specific habitat suitability 
#
# AUTHOR(S):    Johannes Radinger

# DATE:         2014-09-12
#
#############################################################################

import sys
import os
import atexit
from datetime import datetime
import grass.script as grass


#Run in mapset: XY mapset

# New Min and Maxvalues Depth
Min_Depth = 0.0
Max_Depth = 1.5

# New Min and Maxvalues Depth
Min_Velocity = 0.0
Max_Velocity = 1.2

#desired extend
extend=50

#Set GRASS region to resolution
grass.run_command("g.region",
			flags = "a",
			s=0,
			w=0,
			n=extend,
			e=extend,
			res=1,
			overwrite = True)

region = grass.read_command("g.region",
			flags="p")
regiondict = dict(item.split(":") for item in region.replace(" ", "").splitlines())

###############################################################
##### Create New "artificial" Depth and Velocity maps #########
#NewValue = (((OldValue - OldMin) * (NewMax - NewMin)) / (OldMax - OldMin)) + NewMin

# for rows/depth
grass.mapcalc("$newmap = (((row() - $OldMin) * ($NewMax - $NewMin)) / ($OldMax - $OldMin)) + $NewMin",
			newmap="depth",
			NewMin=Min_Depth,
			NewMax=Max_Depth,
			OldMin=1,
			OldMax=regiondict["rows"],
			overwrite=True)

#for cols/velocity
grass.mapcalc("$newmap = (((col() - $OldMin) * ($NewMax - $NewMin)) / ($OldMax - $OldMin)) + $NewMin",
			newmap="velocity",
			NewMin=Min_Velocity,
			NewMax=Max_Velocity,
			OldMin=1,
			OldMax=regiondict["cols"],
			overwrite=True)

specieslist= ["Rutiilus_ad","Rutiilus_juv"]


#######################################################
# Before the first create point map to collect results
grass.run_command("r.to.vect",
			overwrite=True,
			input="velocity",
			output="Habitat_suitability_results",
			type="point")

grass.run_command("v.db.dropcolumn",
			map="Habitat_suitability_results",
			columns="value")


#add depth and velocity columns and update results vector
grass.run_command("v.db.addcolumn",
			map="Habitat_suitability_results",
			columns="Depth DOUBLE, Velocity DOUBLE")
grass.run_command("v.what.rast",
			map="Habitat_suitability_results",
			raster="depth",
			column="Depth")
grass.run_command("v.what.rast",
			map="Habitat_suitability_results",
			raster="velocity",
			column="Velocity")

# add species columns
grass.run_command("v.db.addcolumn",
			map="Habitat_suitability_results",
			columns=", ".join([x+" DOUBLE" for x in specieslist]))


###################################
##### Run for each species #######

for i in specieslist:
	# Get name of run
	grass.message("This is Species: "+i)

	# r.fuzzy
	grass.run_command("r.fuzzy.system",
			overwrite=True,
			maps="/path/to/Habitat.map",
			rules="/path/to/rules_folder/"+i+".rul",
			family="Zadeh",
			defuz="centroid",
			imp="minimum",
			res=100,
			output="fuzzy_output")
	
	# Dictionary for extrating information from r.univar
	d = {'n':5, 'min': 6, 'max': 7, 'mean': 9, 'sum': 14, 'median':16, 'range':8}

	# Get possible minimum and maximum of defuzzified output
	univar = grass.read_command("r.univar", map = "fuzzy_output", flags = 'e')
	minimum = float(univar.split('\n')[d['min']].split(':')[1])
	maximum = float(univar.split('\n')[d['max']].split(':')[1])
	minimum = min(minimum,0.2)
	maximum = max(maximum,0.8)

	# Rescale the output based on min and max
	grass.write_command("r.recode",
			flags = "d",
			overwrite = True,
			input="fuzzy_output",
			rules="-",
			stdin=str(minimum)+":"+str(maximum)+":"+"0:1",
			output="HS"+"_"+i)
		
	#Store Results in point vector
	grass.run_command("v.what.rast",
			map="Habitat_suitability_results",
			raster="HS"+"_"+i,
			column=i)
		
	
	# Remove files
	grass.run_command("g.remove",
			rast=["fuzzy_output"])

grass.run_command("v.out.ascii",
		flags="c",
		overwrite=True,
		input="Habitat_suitability_results",
		output="/path/to/output_file.txt",
		format="point",
		columns=specieslist + ["Depth", "Velocity"],
		separator="comma")


