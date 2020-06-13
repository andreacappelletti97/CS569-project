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

from RA_DataStructures import *
import time
import os
import subprocess

def importdata():
	print "Importing Data..."
	if os.path.isfile('RepeatAnalyzer.dat'):
		with open(r'RepeatAnalyzer.dat','rb') as data:
			return pickle.load(data)#import data
			print "Data Imported."
	else:
		if (raw_input("Warning: the RepeatAnalyzer.dat file is missing. Make sure it is in the same folder as RepeatAnalyzer.py. If you are running the program for the first time, this is expected, so select 'y'. Go on (y/n)?")!='y'):
			sys.exit(0)
		else:
			return [Species(raw_input("Enter a species name:"))]
		
# This function pickles the data to a .dat, and stores the old .dat as backup. 
# older backups may be deleted.
def exportdata(speciesList):
	print "Exporting data..."
	if os.path.isfile('RepeatAnalyzer.dat.bak'):
		os.remove('RepeatAnalyzer.dat.bak')
	if os.path.isfile('RepeatAnalyzer.dat'):
		os.rename('RepeatAnalyzer.dat', 'RepeatAnalyzer.dat.bak')
	with open('RepeatAnalyzer.dat','wb') as data:
		pickle.dump(speciesList,data)		

#input a list of names, return a string of those names compressed
#ex. A A B C C C == 2[A]-B-3[C]
def compressNames(list, sep1='[', sep2=']', sep3='-'):
	lastname=list[0]
	count=1
	res=""
	firstloop=True
	list.append("")
	for name in list[1:]:
		if name==lastname:
			count+=1
		else:
			if firstloop==True:
				firstloop=False
			else:
				res+=sep3
			if count>1:
				res+=str(count)+sep1+lastname+sep2
			else:
				res+=lastname
			count=1
		lastname=name

	return res
		
def generateAutonames(species):
	updateGeocoding(species)
	for strain in species.strains:
		name=[]
		for (year, animalid, lstring) in strain.autoname: 
			repeats=compressNames(matchnames(strain.sequence, species.repeats))
			ccode="UNKN"
			pcode="UNKN"
			for l in strain.location:
				if l.locationstring==lstring:
					ccode=l.ccode
					pcode=l.pcode
					break
			pcodeOpt=","+pcode
			if len(pcode)>4:
				pcodeOpt=""
			name.append(repeats+"_"+ccode+pcodeOpt+"_"+year+"_"+animalid)
			print name[-1]
		strain.name=strain.name+list(set(name)-set(strain.name))
		strain.autoname=[]	
		while "" in strain.name and len(strain.name)>1: strain.name.remove("")
		
def codecoords(l):
	print "coding", l.getString()
	#try:
		#coords=geocoder.geocode(l.getString(),timeout=5)
	URL='https://maps.googleapis.com/maps/api/geocode/json?address='+l.getString().replace(' ','+')+'&key=AIzaSyA7p1KIlvZU3VupuRgw2S8nTL4iPbH6ikI'
	print "Loading data..."
	data = json.load(urllib2.urlopen(URL))
	#except GeocoderTimedOut as e:
	#	print "Error: Geocoder timed out, check your internet connection"
	#	return
	#except GeocoderQuotaExceeded: 
	if data['status']!="OK":
		print "Error: Check your internet connection for stability, \notherwise the error status below should give you an idea of what the problem is."
		print "The query status is:", data['status']
		return
	coords=data['results'][0]['geometry']['location']
	if coords!=None:
		#l.latitude=coords.latitude
		#l.longitude=coords.longitude
		l.latitude=coords['lat']
		l.longitude=coords['lng']
		#unify name formatting VVV
		#URL='https://maps.googleapis.com/maps/api/geocode/json?latlng='+str(l.latitude)+','+str(l.longitude)
		#data = json.load(urllib2.urlopen(URL))
		address=data['results'][0]['address_components']
		for element in address:
			if "country" in element['types']:
				l.country=element['long_name']
				l.ccode=element['short_name']
			if "administrative_area_level_1" in element['types'] and l.length>1:
				l.province=element['long_name']
				l.pcode=element['short_name']
			if "administrative_area_level_2" in element['types']and l.length==3:
				l.city=element['long_name']
		print "\t"+str(l.latitude)+", "+str(l.longitude)
		print "\t"+l.getString().encode("utf-8")
		l.stable=True
	else:
		print "\t Not found"
		
def updateGeocoding(species,  recodeStable=False):
	for ID in species.usedStrainIDs:
		s=getObjectbyID(ID, species.strains)
		if s==None:
			continue
		#geocoder=GoogleV3()
		i=0
		#s.location=[x for x in s.location if x.country!=""]
		for l in list(s.location):
			if (l.country==None or l.country=="") and ((l.latitude==None) or (l.longitude==None)):
				print "Removing blank location"
				s.location.remove(l)
		for l in s.location :
			#code for country names (if entered by coord)
			if (l.country=="" and l.latitude!=None and l.longitude!=None) or (l.stable==True and recodeStable==True):
				print "coding "+str(l.latitude)+", "+str(l.longitude)
				URL='https://maps.googleapis.com/maps/api/geocode/json?latlng='+str(l.latitude)+','+str(l.longitude)+'&key=AIzaSyA7p1KIlvZU3VupuRgw2S8nTL4iPbH6ikI'
				print "Loading data..."
				data = json.load(urllib2.urlopen(URL))
				try:
					address=data['results'][0]['address_components']
				except IndexError:
					print "Could not code ",l.getString()
					continue
				added=0
				for element in address:
					if "country" in element['types']:
						l.country=element['long_name']
						l.ccode=element['short_name']
						added+=1
					if "administrative_area_level_1" in element['types']:
						l.province=element['long_name']
						l.pcode=element['short_name']
						added+=1
					if "administrative_area_level_2" in element['types']:
						l.city=element['long_name']
						added+=1
				l.length=added
				l.stable=True
				print "\t"+l.getString().encode("utf-8")
				#print geocoder.reverse((38.364625, -99.667969),exactly_one=True)
				print "wait..."
				time.sleep(2)	
				
			#set coords and normalize names
			if (l.latitude==None) or (l.longitude==None):
				codecoords(l) 
				print "wait..."
				time.sleep(2)	
				
				
			#populate dummy locations
			species.addlocationdummies(l.getString())
			
		s.location=list(set(s.location))
		#for l in species.dummyLocations:
		#	if (l.latitude==None) or (l.longitude==None):
		#		codecoords(l) 
		#		time.sleep(.5)	
		
#returns a list as a string with sep separators.
def listtostring(list, sep):
	string=""
	if len(list)>0:
		string+=list[0]#.decode('utf-8')
	for item in list[1:]:
		string+=sep+item#.decode('utf-8')
	return string

# takes an ID and returns its name (plus aliases as strings)
def findnames(ID,list):
	names=""
	for entry in list:
		if ID==entry.ID:
			#if len (names)!=0:
			names+=listtostring(entry.name,";").decode('utf-8')
			#else:
			#	names=" ".join(entry.sequence)
			return names
	return names	

# takes a list of IDs and returns a list of their names from list (plus aliases as strings)
# list objects must have name element
def matchnames(IDs, list):#returns an array of names
	names=[]
	for id in IDs:
		names.append(findnames(id,list).encode('utf-8'))
	return names
	
#takes a DNA string and returns a protein string
def dnatoprotein(DNA):
	start = time.time()
	result=""
	#DNA=re.sub(r'[^atcg]','',DNA)
	codons=[]
	codontable = {
	#http://stackoverflow.com/questions/19521905/translation-dna-to-protein
    'ata':'i', 'atc':'i', 'att':'i', 'atg':'m',
    'aca':'t', 'acc':'t', 'acg':'t', 'act':'t',
    'aac':'n', 'aat':'n', 'aaa':'k', 'aag':'k',
    'agc':'s', 'agt':'s', 'aga':'r', 'agg':'r',
    'cta':'l', 'ctc':'l', 'ctg':'l', 'ctt':'l',
    'cca':'p', 'ccc':'p', 'ccg':'p', 'cct':'p',
    'cac':'h', 'cat':'h', 'caa':'q', 'cag':'q',
    'cga':'r', 'cgc':'r', 'cgg':'r', 'cgt':'r',
    'gta':'v', 'gtc':'v', 'gtg':'v', 'gtt':'v',
    'gca':'a', 'gcc':'a', 'gcg':'a', 'gct':'a',
    'gac':'d', 'gat':'d', 'gaa':'e', 'gag':'e',
    'gga':'g', 'ggc':'g', 'ggg':'g', 'ggt':'g',
    'tca':'s', 'tcc':'s', 'tcg':'s', 'tct':'s',
    'ttc':'f', 'ttt':'f', 'tta':'l', 'ttg':'l',
    'tac':'y', 'tat':'y', 'taa':'_', 'tag':'_',
    'tgc':'c', 'tgt':'c', 'tga':'_', 'tgg':'w',
	'gcn':'a', 'cgn':'r', 'mgr':'r', 'aay':'n',
	'gay':'d', 'tgy':'c', 'car':'q', 'gar':'e',
	'ggn':'g', 'cay':'h', 'ath':'i', 'ytr':'l',
	'ctn':'l', 'aar':'k', 'tty':'f', 'ccn':'p',
	'tcn':'s', 'agy':'s', 'acn':'t', 'tay':'y',
	'gtn':'v', 'tar':'_', 'tra':'_'
    }
	while len(DNA)>2:
		codons.append(DNA[:3])
		DNA=DNA[3:]
	for codon in codons:
		if codon in codontable:
			result+=codontable[codon]
		else:
			#print "Warning: This DNA sequence contains invalid codon",codon,"marked as X."
			result+="X"
		#else:
			#print "Error: check your DNA"
		#	return ""
	end = time.time()
	print("DNA conver timer")
	print(end - start)		
	
	return result

#for an id, returns an entity, either a species or repeat.
def getObjectbyID (id, list):
	for item in list:
		if item.ID==id:
			return item
	
	return None
	
#return all papers with the given strain or repeat (by ID) type=s or r
def getAllPapers(id, type, species):
	res=[]
	if type=='s':
		for p in species.paperList:
			if p.hasStrain(id)==True:
				res.append(p)
	
	if type=='r':
		for p in species.paperList:
			if p.hasRepeat(id)==True:
				res.append(p)
	
	return res

#given a repeat id, returns all strains containing that repeat
def getAllStrains(id, species):
	res=[]
	for strain in species.strains:
		for repeatID in strain.sequence:
			if repeatID==id:
				res.append(strain)
				break
	return res

#given a strain or repeat ID, return the locations associated with it
#if removeimplied = true take out entried at higher scope implied by a lower scope entry	
def getAllLocations(id, type, species, removeImplied=False):

	locs=[]
	if type=='s':
		locs= getObjectbyID(id, species.strains).location
	
	if type=='r':
		for strain in getAllStrains(id, species):
			for l in strain.location:
				if l in locs:
					continue
				else:
					locs.append(l)
	if type=='a':
		for s in species.strains:
			for l in s.location:
				if l in locs:
					continue
				else:
					locs.append(l)
	
	res=[]
	if removeImplied==True:
		for l in locs:
			isImplied=False
			for l2 in locs:
				if l.length<l2.length:
					if l.country==l2.country and ((l.length==2 and l.province==l2.province) or l.length==1):
						isImplied=True
			if isImplied==False:
				res.append(l)
	else:
		res=locs
	return res
	
#from a given location (as string), return all species objects from there
def getAllStrainsFrom(locationstring, species):
	res=[]
	loc=Location(locationstring)
	for strain in species.strains:
		for l in strain.location:
			#print "checking",l.getString(),"==",loc.getString()
			if l==loc:
				res.append(strain)
				break
			if loc.length==1:
				if sanitize(l.country)==sanitize(loc.country):
					res.append(strain)
					break
			if loc.length==2:
				if sanitize(l.country)==sanitize(loc.country) and sanitize(l.province)==sanitize(loc.province):
					res.append(strain)
					break
		
	return res

#for a given list of strains, return all repeats therein
def getAllRepeatsFrom(strains, species):
	res=[]
	ret=[]
	
	for strain in strains:
		for rID in strain.sequence:
			if not (rID in res):
				res.append(rID)
	for item in res:
		ret.append(getObjectbyID(item, species.repeats))
	
	return ret

#for a given list of strains, return all papers that report them	
def getAllPapersFrom(strains, species):
	res=[]
	
	for paper in species.paperList:
		for strain in strains:
			if strain.ID in paper.strains:
				if paper not in res:
					res.append(paper)

	
	return res
	
#for a set of repeats output its names and matching strain (if any)
def printresult(repeats,species,tabs=""):
	strain=identifystrain(repeats,species)
	res=u""
	if strain != None:
		res+= "\n"+tabs+"Strain: "+ findnames(strain,species.strains)
		s=getObjectbyID(strain, species.strains)
		res+="\n"+tabs+"Found at:"
		for l in s.location:
			res+="\n"+tabs+"\t"+l.getString()#.decode('utf-8')
		res+="\n"+tabs+"Referenced in:"
		papers=getAllPapers(strain, 's', species)
		for p in papers:
			res+="\n"+tabs+"\t"+p.line1.decode("utf-8")+"\n"+tabs+"\t\t"+p.line2.decode('utf-8')+"\n"+tabs+"\t\t"+p.line3.decode('utf-8')
	
	res+= "\n"+tabs+"Repeats: "+ listtostring(matchnames(repeats,species.repeats),' ')
		
	return res
	
def readdatafromfile(file, species):
	if "." not in file:
		file+=".txt"
	if os.path.isfile(file):
		for numpass in range(1,3):
			print "Pass", numpass, "in progress..."
			if (not os.access(file, os.R_OK)):
				print "Error: File cannot be read, check your permissions."
				return
			with open(file,'r') as input:
				lineat=0
				linecontent=1 #[1,3]=citation, 4=repeat 5=strain
				line1=""
				line2=""
				currentpaper=""

				for line in input: 
					lineat+=1 
					line=line.strip()


					if line=="":
						continue
					if line=="Repeats:":
						linecontent=4
						continue
					if line=="Strains:":
						linecontent=5
						continue
						
					if line=="Paper:":
						linecontent=1
						continue
						
					if line=="Unpublished:":
						linecontent=1
						
					if linecontent==1:
						line1=line.strip()
						linecontent=2
						continue
					
					if linecontent==2:
						line2=line.strip()
						linecontent=3
						continue
					
					if linecontent==3:
						currentpaper=""
						if line1 == "Unpublished:":
							for p in species.paperList:
								#line1="Unpublished"
								if p.line2==line2 and p.line3==line.strip():
									currentpaper=p
						else:
							for p in species.paperList:
								if p.title==line1:
									currentpaper=p
						if currentpaper=="":
							currentpaper=species.addPaper(Paper([line1,line2,line.strip()]))
					
					if linecontent==4:
						if numpass==2:
							continue
						erline=line
						line=line.split(":")
						if len(line)!=2:
							print "Error in input file at repeatline line",lineat
							print erline 
							break
						if species.addRepeat(line[0].strip(), sanitize(line[1].strip())) == 1:
							return
						if currentpaper=="":
							continue
						currentpaper.addRepeat(findID(line[0].strip(),species.repeats))
					
					if linecontent==5:
						if numpass==1:
							continue
						erline=line
						line=line.split(":")
						if len(line)<3:#adds ability to include accession code
							print "Error in input file at strain line",lineat
							print erline 
							break
						if len(line)==4:
							species.addStrain([line[0].strip()], line[1].strip(), line[2].strip(),line[3].strip())
						else:
							species.addStrain([line[0].strip()], line[1].strip(), line[2].strip())
						
						#print [line[0].strip()], line[1].strip(), line[2].strip()
						if currentpaper=="":
							continue
						currentpaper.addStrain(identifystrain(parserepeats(line[1].strip(),species),species))
	
	else:
		print "Error: The file could not be found"
		return
	
	calculateSubstrings(species)
		
	if sanitize(str(raw_input("Would you like to update geocoding now? (this may take a few minutes) (y/n)?")))=='y':
		print "Updating..."
		updateGeocoding(species)
		if sanitize(str(raw_input("Would you like to generate names for any unnamed strains? (y/n)?")))=='y':
			generateAutonames(species)

				
	return
	
def calculateSubstrings(species):
	for repeat in species.repeats:
		repeat.subsetOf=Set([])
		for r in species.repeats:
			if len(r.sequence)>len(repeat.sequence):
				for i in range(0,len(r.sequence)-len(repeat.sequence)+1):
					found=True
					for ind, char in enumerate(repeat.sequence):
						if char!=r.sequence[ind+i]:
							found=False
							break
				if found==True:
					repeat.subsetOf.add(r.ID)
	return

#This function prints a summary of current data for a given species
def printspeciesdata(species,loc):
	loc.write( "Name: "+species.name +"\n")
	loc.write("Repeats:\n")
	for repeat in species.repeats:
		loc.write( "	"+listtostring(repeat.name,'; ')+" : "+repeat.sequence+"\n")
	loc.write( "Strains:\n")
	for strain in species.strains:
		loc.write(  "	"+(listtostring(strain.name,'; ')+" : "))
		loc.write(  listtostring(matchnames(strain.sequence,species.repeats)," ")+"\n")
		for l in strain.location:
			loc.write(  "		"+listtostring(l.getList(), ", "))
			loc.write("\n")
		
	for paper in species.paperList:
		loc.write(paper.line1+"\n"+paper.line2+"\n"+paper.line3+"\n")
		loc.write("Repeats:\n")
		for r in paper.repeats:
			loc.write("	"+findnames(r,species.repeats)+"\n")
		loc.write( "Strains:\n")
		for s in paper.strains:
			loc.write("	"+findnames(s,species.strains)+"\n")

#http://rosettacode.org/wiki/Levenshtein_distance#Python
def levenshteinDistance(s1,s2):
    if len(s1) > len(s2):
        s1,s2 = s2,s1
    distances = range(len(s1) + 1)
    for index2,char2 in enumerate(s2):
        newDistances = [index2+1]
        for index1,char1 in enumerate(s1):
            if char1 == char2:
                newDistances.append(distances[index1])
            else:
                newDistances.append(1 + min((distances[index1],
                                             distances[index1+1],
                                             newDistances[-1])))
        distances = newDistances
    return distances[-1]
#END

def createRepeatMatrix(species):
	repeatmatrix=[]
	for row in range(len(species.repeats)):
		#Add new row to matrix
		repeatmatrix.append([])
		repeatmatrix[row].extend([0]*len(species.repeats))
	
	for row in range(len(species.repeats)):
		for col in range(row+1,len(species.repeats)):
			repeatmatrix[row][col]=levenshteinDistance(species.repeats[row].sequence,species.repeats[col].sequence)
			repeatmatrix[col][row]=repeatmatrix[row][col]

	return repeatmatrix	
			
# Knuth-Morris-Pratt string matching
# David Eppstein, UC Irvine, 28 Feb 2002
# https://www.ics.uci.edu/~eppstein/161/python/kmp.py
# Find occurrences of pattern as a contiguous subsequence of the text.
# For the KMP versions the pattern must be a list or string, because we
# perform array indexing into it, but the text can be anything that can
# be used in a for-loop.  The naive match shown first requires the text
# to be a list or string as well.
def kmpAllMatches(pattern, text):
	print("PATTERN: " + pattern)
	#print("text: " + text)
	shift = computeShifts(pattern)
	startPos = 0
	matchLen = 0
	result=[]
	for c in text:
		while matchLen >= 0 and pattern[matchLen] != c:
			startPos += shift[matchLen]
			matchLen -= shift[matchLen]
		matchLen += 1
		if matchLen == len(pattern):
			#yield startPos
			result.append(startPos)
			startPos += shift[matchLen]
			matchLen -= shift[matchLen]
	return result

def computeShifts(pattern):
        start = time.time()
        #print("computing shift...")
	shifts = [None] * (len(pattern) + 1)
	shift = 1
	for pos in range(len(pattern) + 1):
		while shift < pos and pattern[pos-1] != pattern[pos-shift-1]:
			shift += shifts[pos-shift-1]
		shifts[pos] = shift
	end = time.time()
	#print("timer total time shiftssss")
	#print(end - start)	
	#print(pattern)
	print("SHIFT COMPUTED")
	#print(shifts)
	return shifts
###### END		

# This function returns a list of repeat ids in order of occurrence 
# found in a given protein strand
def KMP(protein, repeats):
        print("KMP algorithm called")
        print("starting timer...")
        start = time.time()
        #for item in repeats:
            #print(item.sequence)
        #print("protein: " + protein)
	output={} #a dictionary of repeats and their starts
	for repeatID, repeat in enumerate (repeats):
		positions=kmpAllMatches(repeat.sequence,protein) #all positions where the repeat starts
		for pos in positions:
			if pos in output:
				if len(repeat.sequence)>len(repeats[output[pos]].sequence):
					output[pos]=repeatID #note this is the list position, not the assigned id
			else:
				output[pos]=repeatID #note this is the list position, not the assigned id
	
	outputreduced=output.copy()
        print("end of timer")
	end = time.time()
	print("timer total time")
	total_time = end - start
	print(total_time)
	
	
	#remove matches that are substrings of other matches
	for start, index in output.iteritems():
		for i in range(start, start+len(repeats[index].sequence)):
			if i in outputreduced:
				if len(repeats[output[i]].sequence)<len(repeats[index].sequence):
					del outputreduced[i]
				
	result=[] #a sorted list of repeat IDs
	for item in sorted(outputreduced.items(),key=operator.itemgetter(0)):
		result.append(repeats[item[1]].ID)

	timer_time = 'Total time: ' + str(total_time)
	result.append(timer_time)

	print("result")
	print(result)
	return result
	output={} #a dictionary of exact repeats and their starts
	#inexactresult=[]
	for repeatID, repeat in enumerate (repeats):
		positions=kmpAllMatches(repeat.sequence,protein,e) #all positions where the repeat starts
		for pos in positions:
		#	if error>0:
		#		inexactresult.append((repeatID,protein[pos:pos+len(repeat.sequence)+error], error))
			if pos in output:
				if len(repeat.sequence)>len(repeats[output[pos]].sequence):
					output[pos]=repeatID #note this is the list position, not the assigned id
			else:
				output[pos]=repeatID #note this is the list position, not the assigned id
	
	outputreduced=output.copy()
	
	#remove matches that are substrings of other matches
	for start, index in output.iteritems():
		for i in range(start, start+len(repeats[index].sequence)):
			if i in outputreduced:
				if len(repeats[output[i]].sequence)<len(repeats[index].sequence):
					del outputreduced[i]
				
	result=[] #a sorted list of repeat IDs
	for item in sorted(outputreduced.items(),key=operator.itemgetter(0)):
		result.append(repeats[item[1]].ID)

	timer_time = 'Total time: ' + str(total_time)
	result.append(timer_time)

	print("result")
	print(result)
	return result

def exportCSV(coords, names, file, species):
	#open a file
	firstLine="lon, lat"
	for index in names:
		firstLine+=", '"+names[index]+"'"
	with open(file,'w') as csv:
	#print columns to file (lon, lat, name1, name2,...nameN)
		csv.write(firstLine+"\n")
	#print each line to file (lon and lat value, with name boolean 1 or 0)
		for coord in coords:
			n=""
			for index in names:
				if index in coords[coord]:
					n+=", "+"1"
				else:
					n+=", "+"0"
			csv.write(str(coord[0])+", "+str(coord[1])+n+"\n")

def exportRepeatCSV(species, file):
	firstline = "Name, Sequence, Source"
	with open(file,'w') as csv:
		csv.write(u'\ufeff'.encode('utf-8'))
		csv.write(firstline+"\n")
		for repeat in species.repeats:
			csv.write('="'+listtostring(repeat.name,";")+'",="'+repeat.sequence+'",')
			csv.write('="')
			for ind, paper in enumerate(species.paperList):
				if repeat.ID in paper.repeats:
					csv.write("("+str(ind+1)+")")
			csv.write('"')
			csv.write("\n")
		csv.write("\n")
		csv.write("ID, Source\n")
		for ind, paper in enumerate(species.paperList):
			csv.write('"'+str(ind+1)+'",')
			csv.write('"'+paper.line1+"\n"+paper.line2+"\n"+paper.line3+'"')
			csv.write("\n")

def exportEditDistanceCSV(species, file):
	firstline=" ,"
	for repeat in species.repeats:
		firstline+=listtostring(repeat.name,";")+","
	
	d=[[0 for x in range(len(species.repeats))] for x in range(len(species.repeats))]
	
	with open(file, 'w') as csv:
		csv.write(u'\ufeff'.encode('utf-8'))
		csv.write(firstline+"\n")
		for ind, repeat in enumerate(species.repeats):
			csv.write(listtostring(repeat.name,";")+",")
			for i in range(0,ind):
				csv.write(str(d[i][ind])+",")
			for i in range(ind,len(species.repeats)):
				d[ind][i]=levenshteinDistance(repeat.sequence,species.repeats[i].sequence)
				csv.write(str(d[ind][i])+",")
			csv.write("\n")

def hist(data,title,xlabel,ylabel):

	fig, ax = mpl.subplots()
	ax.yaxis.grid()
	plot=ax.hist(data, bins=np.arange(max(min(data)-1.5,.5),max(data)+1.5,1), rwidth=.5)
	ax.set_axisbelow(True)
	
	mpl.title(title)
	mpl.xlabel(xlabel)
	mpl.ylabel(ylabel)
	mpl.xlim(max(min(data)-1,0),max(data)+1)
	mpl.ylim(0,stats.mode(data)[1][0]+1)
	
	if data.count(1)>5*data.count(2) and data.count(1)>30:
		#add plot insert
		a = mpl.axes([.4, .4, .45, .45])
		a.yaxis.grid()
		data2=filter(lambda x: x != 1, data)
		while data2.count(max(data2))<2:
			data2.remove(max(data2))
		a.hist(data2, bins=np.arange(max(min(data2)-1.5,.5),max(data2)+1.5,1), rwidth=.5)
		a.set_axisbelow(True)
		mpl.xlim(max(min(data2)-1,0),max(data2)+1)
		mpl.ylim(0,stats.mode(data2)[1][0]+1)
		#mpl.setp(a, xticks=[], yticks=[])
	
	#ax = fig.add_subplot(1,1,1)
	#ax.yaxis.grid(color='gray', linestyle='dashed')
	#ax.set_axisbelow(True)
	
	mpl.show(block=False)			
			
#Works for GD2 and GD3, but will always return 100 for GD1 due to storing only genotypes as strains
#possibility: feed in samples for a location, print out GD for that location?
#diversity (unique repeats)/(num repeats across all strains)
#uniformity avg for all repeats(frequency/length)
#variation? avg for each repeat (frequency/lengh)
def calculateGeneticDiversity(species, locationstring, plotFreq=True, plotLen=True, plotED=True):
	GD2=-1
	M1Local=-1
	M1Global=-1
	M2Local=-1
	M2Global=-1
	names={}

	if locationstring=="Any":
		strains=species.strains
		repeats=species.repeats
		locationstring="the World"
	else:
		location=Location(locationstring)
		strains=getAllStrainsFrom(locationstring, species)
		repeats=getAllRepeatsFrom(strains, species)
		
	totalstrains=len(strains)
	if totalstrains==0:
		return(GD2,M1Local,M1Global,M2Local,M2Global,names)
	
	totalrepeatcount=0
	for strain in strains:
		totalrepeatcount+=len(strain.sequence)
	totalrepeatsequences=len(repeats)
	
	GD2=round(totalrepeatsequences*1.0/totalstrains,4) #Legacy Diversity
	
	M1Local=0
	for strain in strains:
		M1Local+=len(set(strain.sequence))*1.0/len(strain.sequence)
	M1Local=M1Local*1.0/len(strains)
	
	M1Global=totalrepeatsequences*1.0/totalrepeatcount#Diversity 
	
	freq={}	
	for strain in strains:
		for repeat in set(strain.sequence):
			if repeat in freq:
				freq[repeat]+=1
			else:
				freq[repeat]=1
				
	frequencies=[] #=freq.values()
	for name,frequency in freq.iteritems():
		#print frequency,"/" ,totalrepeatcount
		frequencies.append(frequency)
		names[findnames(name,species.repeats)]=frequency

	if len(frequencies)>1 and plotFreq==True:
		hist(frequencies,"Frequency Distribution for "+locationstring,"Number of Occurrences","Number of SSR Sequences")	
	

	#Also plot length distribution 
	if plotLen==True:
		if len(repeats)>1:
			rLens=[]
			for repeat in repeats:
				rLens.append(len(repeat.sequence))
			hist(rLens,"Repeat Length Distribution for "+locationstring+"\n  "+r'$\mu=$'+str(round(np.mean(rLens),2))+", "+r'$\sigma=$'+str(round(np.std(rLens),2)),"Length","Number of SSR Sequences")
			
		if len(strains)>1:
			sLens=[]
			for strain in strains:
				sLens.append(len(strain.sequence))
			hist(sLens,"Genotype Length Distribution for "+locationstring+"\n  "+r'$\mu=$'+str(round(np.mean(sLens),2))+", "+r'$\sigma=$'+str(round(np.std(sLens),2)),"Length","Number of Genotypes")
	#Also plot average edit distance for repeats in each genotype
	
	freq={} #used in GDM2G score
	for strain in strains:
		for repeat in strain.sequence:
			if repeat in freq:
				freq[repeat]+=1
			else:
				freq[repeat]=1
	frequencies=freq.values()
	
	fReg=[]
	for f in frequencies:
		fReg.append(f*1.0/totalrepeatcount)
	
	M2Local=0
	for strain in strains:
		fGen={}
		for r in strain.sequence:
			if r in fGen:
				fGen[r]+=1
			else:
				fGen[r]=1
		
		M2Local+=np.std([x*1.0/len(strain.sequence) for x in fGen.values()])
		
		
	#for ind, val in fGen.iteritems():
	#	val=val/len(getObjectbyID(ind,repeats).sequence)
	
	M2Local=M2Local/len(strains)
	
	M2Global=np.std(fReg)
	
	return (GD2,M1Local,M1Global,M2Local,M2Global,names)

#Get the repeats unique to a given location (locationstring = country[,province][,county])
def getUnique(species, locationstring):
	names=[]
	location=Location(locationstring)
	if location==None:
		print "Error: invalid location"
		return names
	strains=getAllStrainsFrom(locationstring, species)
	repeats=getAllRepeatsFrom(strains, species)
	for repeat in repeats:
		Unique=True
		for strain in species.strains:
			if repeat.ID in strain.sequence:
				for loc in strain.location:
					if location.length==1:
						if sanitize(loc.country) != sanitize(location.country):
							Unique=False
							break
					if location.length==2:
						if sanitize(loc.country) != sanitize(location.country) or sanitize(loc.province) != sanitize(location.province):
							Unique=False
							break
					if location.length==3:
						if location==loc:
							continue
						else:
							Unique=False
							break
		if Unique==True:
			names.append(findnames(repeat.ID,species.repeats))
	return names
	
	
# count the number of unique places a repeat is found
# if type is p, also count unique provinces
# Otherwise only countries are counted	
def getMostCommonRepeats(num, type, list, species):
	locations=[]
	ret=[]
	for repeat in list:
		l=getAllLocations (repeat.ID, 'r', species)
		setl=Set([])
		for i in l:
			if i.country!=None:
				setl.add(i.country)
			if type=="p":
				if i.province!=None:
					setl.add(i.province)
		
		locations.append((len(setl),repeat))
		
	locations.sort()
	locations.reverse()
	
	return locations[0:num]

