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

from __future__ import generators
import os, re, pickle, operator, random, math, time, multiprocessing, sys, subprocess,tkMessageBox,json,urllib2
from sets import Set
#from Tkinter import *
from ScrolledText import * 
import numpy as np
from mpl_toolkits.basemap import Basemap
from matplotlib.patches import Polygon
import matplotlib.pyplot as mpl
import matplotlib.colors as colors
import matplotlib.cm as cm
from scipy import stats
#from Bio import AlignIO
#from Bio.Alphabet import generic_dna
#from Bio.Seq import Seq
#from Bio.SeqRecord import SeqRecord
#from Bio.Align import MultipleSeqAlignment
#from Bio.Align.Applications import DialignCommandline
#from geopy.geocoders import GoogleV3
#from geopy.exc import GeocoderTimedOut, GeocoderQuotaExceeded

class Repeat:
	def __init__ (self,name,sequence,ID):#name=list, repeats=string
		self.ID=ID
		self.name=name
		self.sequence=sequence #the repeat
		self.subsetOf=[]
		
class Strain:
	def __init__ (self,name,repeats,ID,locationstring,accessionCode=[]):#name=list, repeats=list of IDs
		self.autoname=[]
		nparts=name[0].strip().split(',')
		if len(nparts)==2 and len(nparts[0].strip())==4:
			name=[""]
			self.autoname.append((nparts[0].strip(),nparts[1].strip(),locationstring))
		self.ID=ID
		self.name=name
		self.sequence=repeats
		self.location=[Location(locationstring)]
		self.subsetOf=[]
		self.accessionCode=accessionCode

class Species:
	def __init__ (self,name):
		self.name=name #the species name
		self.repeats=[] #the list of repeats
		self.strains=[] #the list of strains
		self.usedRepeatIDs=Set([])
		self.usedStrainIDs=Set([])
		self.paperList=[]
		self.dummyLocations=Set([])
	##This function takes the info for a new repeat and adds it, 
	##or if it has a new sequence with existing name asks the user if they want to replace it. 
	def addRepeat(self,name,sequence):
		from Tkinter import Tk
		found = findID(name,self.repeats)
		root = Tk()
		root.withdraw()

		for repeat in self.repeats:
			if repeat.ID==found and repeat.sequence!=sequence:
				if tkMessageBox.askyesno("Conflict", "The repeat "+name+" already exists with sequence "+repeat.sequence+" Would you like to replace it with the sequence "+sequence):
					repeat.sequence=sequence#update sequence
					return 0
				else:
					if tkMessageBox.askyesno("Conflict","Would you like to save "+name+" as a new repeat?"):
						tkMessageBox.showinfo("Instructions", "You will need to change the name of "+name+" in the input file."+"\n"+\
						"Be sure to also update the names of any strains referring to this same sequence"+sequence+"\n"+\
						"Ex. You could call this repeat "+name+"-1 or "+name+"(2)"+"\n"+\
						"Once you have updated the file, be sure to run this function again to read the rest of the input")
						return 1
			if repeat.sequence==sequence and (name not in repeat.name): 
				repeat.name.append(name)#add new names
				return 0
				
		if found==None:
			self.repeats.append(Repeat([name],sequence,newID(self.usedRepeatIDs)))
	def addStrain(self,name,repeats,locationstring,accessionCode=[]):#name=list, repeats=string of repeat names
		repeatIDs=parserepeats(repeats,self)
		if repeatIDs==[]:
			return
		nparts=name[0].strip().split(',')
		#print len(nparts), len(nparts[0])

		#check if the sequence exists
		found = identifystrain(repeatIDs, self)
		if found!=None:
			for strain in self.strains:
				if strain.ID==found:
					#if autogen naming, add name info
					if len(nparts)==2 and len(nparts[0].strip())==4:
						name=[""]
						if hasattr(strain,'autoname')==False:
							strain.autoname=[]
						strain.autoname.append((nparts[0].strip(),nparts[1].strip(),locationstring))
			
					#add name to found names
					strain.name=list(set(name)|set(strain.name))
					#add acc code to list
					strain.accessionCode=list(set(accessionCode)|set(strain.accessionCode))
					while "" in strain.name and len(strain.name)>1: strain.name.remove("")
				
					#add location to found locations
					l=Location(locationstring)
					locfound=False
					for loc in strain.location:
						if l==loc:
							locfound=True
							break
					if locfound==False:
						strain.location.append(l)
					return
		else:
			newstrain=Strain(name,repeatIDs,newID(self.usedStrainIDs),locationstring,accessionCode)
			if len(newstrain.sequence)>0:
				self.strains.append(newstrain)
		return		
	def addPaper(self,newpaper):
		if newpaper.type=='u':
			for paper in self.paperList:
				if newpaper.authors==paper.authors and newpaper.year==paper.year and paper.title==newpaper.title:
					return paper
		else:
			for paper in self.paperList:
				if paper.type!='u' and newpaper.PMID==paper.PMID:
					return paper

		self.paperList.append(newpaper)
		return newpaper
	def addlocationdummies(self, location):
		loc=location.split(',')
		if len(loc)>1:
			# add level 1 dummy
			self.dummyLocations.add(Location(loc[0]))
		if len(loc)==3:
			# add level 2 dummy
			self.dummyLocations.add(Location(loc[0]+","+loc[1]))
	
class Paper:
	def __init__(self, lines, type='p'):
		if len(lines)!=3:
			print "Error in input, citation formatted incorrectly"
			return
		
		self.line1=lines[0]
		self.line2=lines[1]
		self.line3=lines[2]
		self.authors=lines[1].strip().split(",.")
		for a in self.authors:
			a=a.strip()
		filter(lambda a: a != "", self.authors)
		self.repeats=Set([])
		self.strains=Set([])
		
		if lines[0]=="Unpublished:":
			self.title="Unpublished"
			self.type='u'
			self.year=lines[1].strip()
		else:
			self.type=type
			l3=lines[2].split(".")
			self.year=l3[1].strip().split(" ")[0]
			self.journal=l3[0]
			#print l3
			#print l3[-1].strip().split(" ")
			self.PMID=l3[-1].strip().split(" ")[-1]
			self.title=lines[0].strip()
			
		return
	def addRepeat(self, ID):
		self.repeats.add(ID)
		return
	def addStrain(self, ID):
		self.strains.add(ID)
		return
	def hasRepeat(self, ID):
		return ID in self.repeats
	def hasStrain(self, ID):
		return ID in self.strains
		
class Location:
	def __init__(self, string):
		string=string.strip()
		list=string.split(",")
		self.locationstring=string
		self.country="" #the country
		self.province=""
		self.city=""
		self.pcode=""
		self.ccode=""
		self.latitude=None
		self.longitude=None
		self.length=0
		self.stable=False
		if string == "":
			return
		try:
			self.latitude=float(list[0])
			if len(list)<2:
				print "Error, invalid location,",string,"missing longitude"
				return
			self.longitude=float(list[1])
		except ValueError:
			self.country=list[0].strip() #the country
			if len(list)>1:
				self.province=list[1].strip() #the province or region
			if len(list)>2:
				self.city=list[2].strip() #the city, town or county
			self.length=len(list)
			if self.length>3:
				self.length=3
	def __eq__(self, l):	
		if l==None:
			return False
		if l.length==0:
			return self.latitude==l.latitude and self.longitude==l.longitude
		return sanitize(self.country)==sanitize(l.country) and sanitize(self.province)==sanitize(l.province) and sanitize(self.city)==sanitize(l.city)			
	def getList(self):
		if self.length==1:
			return [self.country]
		if self.length==2:
			return [self.country, self.province]

		return [self.country, self.province, self.city]		
	def getString(self):
		if self.length==0:
			return "("+str(self.latitude)+", "+str(self.longitude)+")"
		if self.length==1:
			return self.country
		if self.length==2:
			return self.country+", "+self.province
		return self.country+", "+self.province+", "+self.city
	def __hash__(self):
		return hash(self.getString())
		
# This function takes a given IDlist and returns the earliest unused ID,
# also adding it to the list
def newID(IDlist):
	nextID=0
	for id in sorted(IDlist):
		if id==nextID:
			nextID+=1
		else:
			IDlist.add(nextID)
			return nextID
	IDlist.add(nextID)
	return nextID

# given a single entity name and a list of entities,
# returns the id of the entity in the list
def findID(name, list):
	name=name.strip()
	for item in list:
		for next in item.name:
			if next.decode('utf-8')==name.decode('utf-8'):
				return item.ID
	return None

#takes a string of whitespace separated repeats and returns a list of repeat ids
def parserepeats(string,species):#returns an array of IDs
	names = string.split()
	result=[]
	for name in names:
		id=findID(name,species.repeats)
		if id==None:
			print "Warning: '"+name+"' is not a repeat for",species.name,"check that it is defined in the input file."
			return []
		else:
			result.append(id)
	return result

#finds any strains in a protein list of repeats passed by ID
def identifystrain(repeats,species):
	for strain in species.strains:
		if strain.sequence==repeats:
			return strain.ID
	return None

#This function returns a sanitized protein with spaces and digits removed, and case set to lower		
def sanitize(string):
	string=re.sub(r'[^\w]','',string)	
	string=re.sub(r'[\d_]','',string)		
	string=string.lower()
	return string

