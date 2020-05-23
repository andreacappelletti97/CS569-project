#!/usr/bin/env python
# coding: utf-8
#	 Copyright 2015 Helen Catanese

#    This file is part of RepeatAnalyzer.

#    RepeatAnalyzer is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    RepeatAnalyzer is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with RepeatAnalyzer.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals

from RA_Interface import *
from matplotlib import pyplot as plt
import pprint
import os
import subprocess


#from jellyfish import levenshtein_distance
#import numpy as np
#def d(coord):
#	i, j = coord
#	return levenshtein_distance(R[i], R[j])

def fancy_dendrogram(*args, **kwargs):
    max_d = kwargs.pop('max_d', None)
    if max_d and 'color_threshold' not in kwargs:
        kwargs['color_threshold'] = max_d
    annotate_above = kwargs.pop('annotate_above', 0)

    ddata = dendrogram(*args, **kwargs)

    if not kwargs.get('no_plot', False):
        plt.title('Hierarchical Clustering Dendrogram of Anaplasma marginale Repeats')
        plt.xlabel('Sample Name or (Cluster Size)')
        plt.ylabel('Distance')
        for i, d, c in zip(ddata['icoord'], ddata['dcoord'], ddata['color_list']):
            x = 0.5 * sum(i[1:3])
            y = d[1]
            if y > annotate_above:
                plt.plot(x, y, 'o', c=c)
                plt.annotate("%.3g" % y, (x, y), xytext=(0, -5),
                             textcoords='offset points',
                             va='top', ha='center')
        if max_d:
            plt.axhline(y=max_d, c='k')
    return ddata

#clusters = dictionary of clusters #: [rID1, rID2,...]
def printClusterMap(species, clusters):
	rlons=[]
	rlats=[]
	rIDs=[]
	cnames={}
	for key, c in clusters.iteritems():
		rlons.append([])
		rlats.append([])
		rIDs.append(key)
		allLocations=set()
		for repeatID in c:
			for location in getAllLocations(repeatID, 'r', species):
				allLocations.add(location)
		for location in list(allLocations):
			rlons[-1].append(location.longitude)
			rlats[-1].append(location.latitude)
			cnames[(location.longitude,location.latitude)]=location.getString()

	createMap(rlons, rlats, rIDs, [], [], [], cnames, species, 4.5, 1, 0, True)
	
def menuloop(speciesList,currentSpecies):
		#process=multiprocessing.Process(target=, args=())
		#process.start()
		goAgain=True
		while goAgain==True:
			print "\nWelcome to RepeatAnalyzer." 
			if speciesList!=[]:
				print "Currently working on", speciesList[currentSpecies].name+":", 
				print len(speciesList[currentSpecies].strains), "strains,",
				print len(speciesList[currentSpecies].repeats), "repeats."

			print "1: Identify repeats"
			print "2: Change current species"
			print "3: Search data"
			print "4: Map data"
			print "5: Input data from file"
			print "6: Regional diversity analysis"
			print "7: Remove a species"
			print "8: Remove a strain"
			print "9: Generate strain names"
			print "10: Print all species data"
			print "11: Update Geocodings"

			print "0: Exit Program" 

			try:
				command=int(raw_input("Please enter the number of the option you want: "))
			except ValueError:
				print "\nPlease enter an integer"
				continue
			if command==0: #Exit
				return
			
			#if command==9:
				#look into multiple sequence alignment for change ranking
				#align=MultipleSeqAlignment([])
				#with open
				#for repeat in speciesList[currentSpecies].repeats:
					#align.extend([SeqRecord(Seq(repeat.sequence, generic_dna),id=listtostring(repeat.name,"; "))])
			
			if command==1: #Find strain from amino acid sequence
				#idprocess=multiprocessing.Process(target=deployWindow, args=(speciesList,currentSpecies))
				#idprocess.start()
				
				deployWindow(speciesList,currentSpecies)
			
			if command==2: #Change current Species
				i=1
				print "0: Add a Species"
				for species in speciesList:
					print str(i)+": "+species.name
					i+=1
				new=int(raw_input("Please enter the number of the option you want: "))-1
				if new<0:
					name=str(raw_input("Please enter the name of the new species: "))
					print 'Is this information correct(y/n)? Name: "'+name+'"',
					if sanitize(str(raw_input(':'))) == 'y':
						speciesList.append(Species(name))
					else:
						print "Species not stored"
				if new>=len(speciesList):
					print "Error: Not a valid selection"
				else:
					currentSpecies=new
			
			if command==3: #Search by repeat, strain or location
				while goAgain==True:
					print "\n What criteria would you like to search by?"
					print "1: Search by repeat"
					print "2: Search by location"
					print "3: Search by strain"
					print "0: Return to main menu"
					try:
						command=int(raw_input("Please enter the number of the option you want: "))
					except ValueError:
						print "\nPlease enter an integer"
						continue

					
					if command==0:
						goAgain=False
			
					if command==1:
						searchByRepeat(speciesList[currentSpecies])
					
						#raw_input("Press 'Enter' to continue")	
						
					if command==2:
						searchByLocation(speciesList[currentSpecies])
						#raw_input("Press 'Enter' to continue")
						
					if command==3:
						searchByStrain(speciesList[currentSpecies])
						
						#raw_input("Press 'Enter' to continue")
						
				goAgain=True
				continue
				
			if command==4: #Search for mapping
				searchWindow(speciesList[currentSpecies])				
		
			if command==10: #Print summary
				with open(speciesList[currentSpecies].name+'.txt','wb') as out:
					printspeciesdata(speciesList[currentSpecies],out)
					
				exportRepeatCSV(speciesList[currentSpecies], speciesList[currentSpecies].name+' repeats.csv')
		
			if command==5: #Read in data
				readdatafromfile(str(raw_input("Enter the name of the file where the values are stored: ")),speciesList[currentSpecies])
			
			if command==6: #calculate Genetic Diversity
			
				#find=raw_input("Please enter the name of the location in the form [country](, [state/province/region](, [county/town/city])): ")
				#if len(find.split(","))>3:
				#	print "Error: too many commas in location. Remember to follow the format"
				#	continue
				
				getGDLocation(speciesList[currentSpecies])

					
			if command==7: #Remove species
				i=1
				for species in speciesList:
					print str(i)+":",species.name
					i+=1
				d=int(raw_input("Enter the number of the species you would like to delete: "))	
				if d>len(speciesList) or d<1:
					print "Error: Not a valid selection"
				else:
					print "You want to delete",speciesList[d-1].name,"is that correct",
					yn=str(raw_input("(y/n):"))
					if yn=='y':
						print speciesList[d-1].name, "Deleted"
						del speciesList[d-1]
					else:
						print "Deletion cancelled."
			
			if command==8: #Remove strain
				i=1
				d=str(raw_input("Enter the repeat sequence of the strain you would like to delete: "))	
				Srepeats=parserepeats(d.strip(), speciesList[currentSpecies])
				Sid=identifystrain(Srepeats,speciesList[currentSpecies])
				if Sid==None:
					print "Error: Not a valid strain"
				else:
					print "You want to delete",speciesList[currentSpecies].strains[Sid].name,"is that correct",
					yn=str(raw_input("(y/n):"))
					if yn=='y':
						print speciesList[currentSpecies].strains[Sid].name, "Deleted"
						del speciesList[currentSpecies].strains[Sid]
					else:
						print "Deletion cancelled."
					
			if command==11: #Update geocoding
				updateGeocoding(speciesList[currentSpecies], True)
				
			if command==12:
				exportEditDistanceCSV(speciesList[currentSpecies],speciesList[currentSpecies].name+'EditDistances.csv' )
				
			if command==9:
				generateAutonames(speciesList[currentSpecies])
				

				
			raw_input("Press 'Enter' to continue")
			exportdata(speciesList)

			
def main():
	speciesList=importdata()
	
	
	reload(sys)  
	sys.setdefaultencoding('utf8')
	
	os.chdir(os.path.dirname(os.path.realpath(__file__)))
	
	#print "C:"
	#for i in getMostCommonRepeats(15,'c',speciesList[0].repeats, speciesList[0]):
	#	print i[0]
	#	print listtostring(i[1].name,";")
	#	print ""
	
	#print"\n P:"
	#for i in getMostCommonRepeats(10,'p',speciesList[0].repeats, speciesList[0]):
	#	print i[0]
	#	print listtostring(i[1].name,";")
	#	print ""
	
	menuloop(speciesList,0)

	
if __name__ == '__main__':
	main()
