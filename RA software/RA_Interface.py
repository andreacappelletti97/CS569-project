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


from RA_Functions import *
from Tkinter import *
import sys
import os


#sets the window title to the appropriate data
def updateTitle (window,speciesList,currentspecies):
	window.wm_title("Working on "+speciesList[currentspecies].name+": "+	 
					str(len(speciesList[currentspecies].strains))+" strains,  "+
					str(len(speciesList[currentspecies].repeats))+" repeats.")
	window.update()

#removes any frames from the main window
def clearFrames(frames):
	for frame in frames:
		frame.pack_forget()
	
#changes current species in the match frame
def changeSpecies(window,speciesList,new,frames):
	updateTitle(window,speciesList,new)
	clearFrames(frames)
	newframe=populatematchframe(window, speciesList[new])
	frames.pop(0)
	frames.insert(0,newframe)
	newframe.pack()

#returns FASTA elements as a list
def decodeFASTA(string):
	if string[0]!=">":
		return string,""
	return "\n".join(string.split("\n")[1:]),string.split("\n")[0]
	
#http://crazyhottommy.blogspot.com/2013/10/python-code-for-getting-reverse.html
def reverseComplement(seq):
	seq=list(seq)
	seq_dict = {'a':'t','t':'a','g':'c','c':'g'}
	for ind,char in enumerate(seq):
		if char in seq_dict:
			seq[ind]=seq_dict[char]
	return "".join(reversed(seq))

#prints a DNA match to window	
def matchDNA(species,input):
	res=u""	
	p=input.split(">")
	if len(p)>1:
		for n,i in enumerate(p):
			p[n]='>'+i

	c=0
	for i in p:
		if sanitize(i)=="":
			continue
		c+=1
		i,name=decodeFASTA(i)
		res+="Sequence "+str(c)+" :\n"
		if name != "":
			res+=name+"\n"
		res+=i+"\n"
		DNA=sanitize(i)
		#convert DNA to proteins for each frame
		#and find the repeats for each
		repeatsFrame1=KMP(dnatoprotein(DNA),species.repeats)
		repeatsFrame2=KMP(dnatoprotein(DNA[1:]),species.repeats)
		repeatsFrame3=KMP(dnatoprotein(DNA[2:]),species.repeats)
		reverserepeatsFrame1=KMP(dnatoprotein(reverseComplement(DNA)),species.repeats)
		reverserepeatsFrame2=KMP(dnatoprotein(reverseComplement(DNA)[1:]),species.repeats)
		reverserepeatsFrame3=KMP(dnatoprotein(reverseComplement(DNA)[2:]),species.repeats)

		#show results for each frame
		res += "Frame 1: "
		if repeatsFrame1 == []:
			res += "No repeats found.\n"
		else:
			res += printresult(repeatsFrame1,species,"\t")+"\n"
		res +=  "\nFrame 2: "
		if repeatsFrame2 == []:
			res +=  "No repeats found.\n"
		else:
			res += printresult(repeatsFrame2,species,"\t")+"\n"
		res +=  "\nFrame 3: "
		if repeatsFrame3 == []:
			res += "No repeats found.\n"
		else:
			res += printresult(repeatsFrame3,species,"\t")+"\n"
			
		res += "\nReverse Frame 1: "
		if reverserepeatsFrame1 == []:
			res += "No repeats found.\n"
		else:
			res += printresult(reverserepeatsFrame1,species,"\t")+"\n"
		res +=  "\nReverse Frame 2: "
		if reverserepeatsFrame2 == []:
			res +=  "No repeats found.\n"
		else:
			res += printresult(reverserepeatsFrame2,species,"\t")+"\n"
		res +=  "\nReverse Frame 3: "
		if reverserepeatsFrame3 == []:
			res += "No repeats found.\n\n"
		else:
			res += printresult(reverserepeatsFrame3,species,"\t")+"\n\n"
		
	#process=multiprocessing.Process(target=popupWindow, args=("DNA Match", res+"\n"))
	#process.daemon = True
	#process.start()
	#popupWindow("DNA Match", res+"\n")
	sys.exit()
	return

#prints a protein match to window	
def matchProtein(species,input):
	res=u""
	p=input.split(">")
	if len(p)>1:
		for n,i in enumerate(p):
			p[n]='>'+i
	
	c=0
	for i in p:
		if sanitize(i)=="":
			continue
		c+=1 
		i,name=decodeFASTA(i)
		res+="Sequence "+str(c)+" :\n"
		res+=name+"\n"+i+"\n"
		protein=sanitize(i)

		
		#os.system('./host source_kmp.xclbin')
		
		repeatList= KMP(protein,species.repeats) #returns the list of repeat IDS for a given protein sequence in order. 
		if repeatList == []:
			res+= "No repeats found.\n"
		else:
			res+=printresult(repeatList,species)+"\n"
		#res+="\nInexact matches:\n"
		#for name,seq,error in inexact:
		#	res+=name+", with "+error+" errors: "+seq
			
			
	print(res)	
	print("TOTAL TIME")
	print(repeatList[len(repeatList) -1])
	#process=multiprocessing.Process(target=popupWindow, args=("Amino Acid Match", res))
	#process.daemon = True
	#process.start()
	#popupWindow("Amino Acid Match", res)
	sys.exit()
	return



	#prints a protein match to window	
def matchKmpFpga():
	os.system('./host source_kmp.xclbin')
		
	
	sys.exit()
	return


#clears data from the identification window
def clearMatchData(inputbox):
	inputbox.delete("1.0",END)

#populates the identify window
def populatematchframe(window,species):
#	proteinbutton=Button(matchbuttonframe,text="Protein",command=lambda:matchProtein(species,inputbox.get("1.0",END)))
#	from Tkinter import Tk, Label, Frame, Text, Button, END
	matchframe=Frame(window)
	instructions=Label(matchframe, text="Select which KMP implementation run")
	instructions.pack()
	matchframe.pack()
	#inputbox=Text(matchframe)
	#inputbox.pack()
	matchbuttonframe=Frame(matchframe)
	matchbuttonframe.pack()
	inputFileDNA = "./input/string.fasta"
	DNAInput = open(inputFileDNA,'r')
	DNAToSend = DNAInput.read()
	DNAbutton=Button(matchbuttonframe,text="FPGA",command=lambda:matchKmpFpga())
	DNAbutton.pack(side="right")
	inputFile = "./input/string.fasta"
	proteinInput = open(inputFile,'r')
	proteinToSend = proteinInput.read()
	proteinbutton=Button(matchbuttonframe,text="Repeat Analyzer",command=lambda:matchProtein(species, proteinToSend))
	#proteinbutton=Button(matchbuttonframe,text="Protein",command=lambda:matchProtein(species,inputbox.get("1.0",END)))
	proteinbutton.pack(side="left")
	#clearbutton=Button(matchframe,text="Clear",command=lambda:clearMatchData(inputbox))
	#clearbutton.pack()

	return matchframe
	
#Builds the identify window
def deployWindow(speciesList,currentspecies):

#	from Tkinter import Tk, Menu, Frame
	window = Tk()
	updateTitle(window,speciesList,currentspecies)
	
	frameList=[]
	
	menubar=Menu(window)
	speciesmenu=Menu(menubar, tearoff=0)
	for index, species in enumerate(speciesList):
		speciesmenu.add_command(label=species.name,command=lambda index=index: changeSpecies(window,speciesList,index,frameList) )
	speciesmenu.add_separator()
	speciesmenu.add_command(label="Cancel")
	menubar.add_cascade(label="Select KMP", menu=speciesmenu)
	
	##populate the matching frame and display it
	matchframe=populatematchframe(window,speciesList[currentspecies])
	frameList.append(matchframe)

	##------
	deletespeciesframe=Frame(window)
	frameList.append(deletespeciesframe)
	deletestrainframe=Frame(window)
	frameList.append(deletestrainframe)
	addrepeatframe=Frame(window)
	frameList.append(addrepeatframe)
	addstrainframe=Frame(window)
	frameList.append(addstrainframe)
	addspeciesframe=Frame(window)
	frameList.append(addspeciesframe)
	##-------

	window.config(menu=menubar)
	window.mainloop()

#highlight is an array of locations of characters to highlight red (to show changed characters for similar repeats)
def popupWindow(title, contents):

#	from Tkinter import Tk, NONE, Scrollbar, RIGHT, LEFT, Y, Text, BOTH

	popup = Tk()
	popup.wm_title(title)
	popup.update()
	
	scrollbary = Scrollbar(popup)
	scrollbary.pack(side=RIGHT, fill=Y)
	#scrollbarx = Scrollbar(popup, orient=HORIZONTAL)
	#scrollbarx.pack(side=BOTTOM, fill=X)
	
	text=Text(popup, borderwidth=0, wrap=NONE)
	text.insert(1.0, contents)
	text.pack(fill=BOTH, expand=True)
	text.configure(state="disabled")
	
	text.config(yscrollcommand=scrollbary.set)
	scrollbary.config(command=text.yview)
	#text.config(xscrollcommand=scrollbarx.set)
	#scrollbarx.config(command=text.xview)
	
	popup.mainloop()

#Deploys a search window
def searchWindow(species):

#	from Tkinter import Tk, Label, Frame, Text, END, LEFT, RIGHT, StringVar, OptionMenu, IntVar, Checkbutton, Button, X
	search=Tk()
	search.wm_title("Search")
	search.update()
	
	instructions=Label(search, text="Please enter the names or sequences of the repeats and/or strains you would like to view separated by SEMICOLONS. \nIf you are interested in only data on a specific region, enter that as well.")
	repeatframe=Frame(search)
	strainframe=Frame(search)
	locationframe=Frame(search)
	modframe=Frame(search)
	mapframe=Frame(search)
	
	repeatL=Label(repeatframe, text="Repeat Name or Sequence", height=1)
	repeat=Text(repeatframe, height=1, width=50)
	repeat.insert(END, "All")
	repeatL.pack(side=LEFT, pady=10)
	repeat.pack(side=RIGHT, pady=10)
	
	strainL=Label(strainframe, text="Strain Name or Sequence", height=1)
	strain=Text(strainframe, height=1, width=50)
	strain.insert(END, "All")
	strainL.pack(side=LEFT, pady=10)
	strain.pack(side=RIGHT, pady=10)
	
	locationV=StringVar(search)
	locations=getAllLocations(-1,'a',species)
	loclist=set([l.getString() for l in species.dummyLocations])
	if len(locations)>0:
		for l in locations:
			if l.length!=0:
				loclist.add(l.getString())
	loclist=sorted(list(loclist))
	loclist.insert(0,"Any")
	locationV.set(loclist[0])
	
	locationL=Label(locationframe, text="Region", height=1)
	location=apply(OptionMenu,(locationframe, locationV)+tuple(loclist))

	sizemodV=StringVar(search)	
	sizemodV.set("1")
	sizemodL=Label(modframe,text="Multiply circle size by:", height=1)
	sizemod=apply(OptionMenu,(modframe, sizemodV)+tuple([.5,.6,.7,.75,.8,.85,.9,.95,1,1.05,1.1,1.15,1.2,1.25,1.3,1.4,1.5,1.6,1.7,1.8,1.9,2,2.5,3,3.5,4]))
	
	legendmodV=StringVar(search)	
	legendmodV.set("best")
	legendmodL=Label(modframe,text="Place legend", height=1)
	legendmod=apply(OptionMenu,(modframe, legendmodV)+tuple(['best','upper right','center right','lower right','upper left','center left','lower left','upper center','lower center']))
	
	reduceNoiseval=IntVar()
	reduceNoise=Checkbutton(locationframe, text="Ignore single location items", height=1, variable=reduceNoiseval, onvalue=True, offvalue=False)
	
	location.pack(side=RIGHT, pady=10)
	locationL.pack(side=RIGHT, pady=10)
	legendmod.pack(side=RIGHT, pady=10)
	legendmodL.pack(side=RIGHT, pady=10)
	reduceNoise.pack(side=LEFT, pady=10)
	sizemodL.pack(side=LEFT, pady=10)
	sizemod.pack(side=LEFT, pady=10)

	
	mapval=IntVar()
	map=Checkbutton(mapframe, text="Create a map", height=1, variable=mapval, onvalue=True, offvalue=False)
	map.select()
	go=Button(mapframe, text="Search", command=lambda:displaySearchResult(species, repeat.get("1.0",END), strain.get("1.0",END), locationV.get(), mapval.get(), search, float(sizemodV.get()), legendmodV.get(), reduceNoiseval.get()))
	map.pack(side=LEFT, pady=10)
	go.pack(side=RIGHT, pady=10)
	
	instructions.pack(padx=20,fill=X)
	repeatframe.pack(padx=20,fill=X)
	strainframe.pack(padx=20,fill=X)
	modframe.pack(padx=20,fill=X)
	locationframe.pack(padx=20,fill=X)
	mapframe.pack(fill=X, padx=20)
	
	search.mainloop()
	
	return

def mapPopup(loclat,loclon, rlons, rlats, r, slons, slats, s, coordnames, species, showMap, sizemod, legendmod, reduceNoise):

	#from Tkinter import Tk

	title="Search Result (Map may take time to load)"
	printstring="Repeats:"
	
	for repeat in r:
		repeat=getObjectbyID(repeat,species.repeats)
		printstring+= "\n\t"+listtostring(repeat.name, "; ")+" : "+repeat.sequence
	printstring+="\nStrains:"
	for strain in s:
		strain=getObjectbyID(strain,species.strains)
		printstring+="\n\t"+listtostring(strain.name, "; ")+ " : "+ listtostring(matchnames(strain.sequence, species.repeats), " ")
	
	printstring+="\nPapers:"
	found=False
	for paper in species.paperList:
		for repeat in r:
			if paper.hasRepeat(repeat):
				printstring+= "\n\t"+paper.line1+"\n\t\t"+paper.line2+"\n\t\t"+paper.line3
				found=True
				break
		if found==False:
			for strain in s:
				if paper.hasStrain(strain):
					printstring+= "\n\t"+paper.line1+"\n\t\t"+paper.line2+"\n\t\t"+paper.line3
					break

	

#	from Tkinter import Tk, NONE, BOTH
	popup = Tk()
	popup.wm_title(title)
	popup.update()
	
	text=ScrolledText(popup, borderwidth=0, wrap=NONE)
	text.insert(1.0, printstring)
	text.pack(fill=BOTH, expand=True)
	text.configure(state="disabled")
 
	#mapprocess = multiprocessing.Process(target=popup.mainloop, args=())
	#mapprocess.start()
     	if showMap==True:
          popup.after(2000, createMap, rlons, rlats, r, slons, slats, s, coordnames, species, sizemod, legendmod, reduceNoise)	
	popup.mainloop()	

 

def searchByRepeat(species):

#	from Tkinter import Tk, Label, Frame, LEFT, RIGHT, Text, X, Spinbox, Button, END
	search=Tk()
	search.wm_title("Search")
	search.update()
	
	instructions=Label(search, text="Please enter the name or protein sequence of the repeat. \nYou may also enter multiple sequences in FASTA format.")
	repeatframe=Frame(search)
	editframe=Frame(search)
	buttonframe=Frame(search)
	
	repeatL=Label(repeatframe, text="Repeat Name or Sequence", height=1)
	repeat=Text(repeatframe, height=2, width=50)
	repeatL.pack(side=LEFT, pady=10)
	repeat.pack(side=RIGHT, pady=10)
	
	editL=Label(editframe, text="Show Similar Repeats with maximum edit distance of ", height=1)
	edit=Spinbox(editframe, from_=0, to=10)
	editL.pack(side=LEFT, pady=10)
	edit.pack(side=RIGHT, pady=10)
	
	go=Button(buttonframe, text="Search", command=lambda:displayRepeatSearchResult(species, repeat.get("1.0",END),int(edit.get())))
	go.pack(side=RIGHT, pady=10)
	
	repeatframe.pack(padx=20,fill=X)
	editframe.pack(padx=20)
	buttonframe.pack(padx=20,fill=X)
	
	search.mainloop()
	
def searchByStrain(species):

#	from Tkinter import Tk, Label, Frame, LEFT, RIGHT, Text, X, Button, END
	search=Tk()
	search.wm_title("Search")
	search.update()
	
	instructions=Label(search, text="Please enter the name or repeat sequence of the strain.")
	strainframe=Frame(search)
	buttonframe=Frame(search)
	
	strainL=Label(strainframe, text="Strain Name or Sequence", height=1)
	strain=Text(strainframe, height=1, width=50)
	strainL.pack(side=LEFT, pady=10)
	strain.pack(side=RIGHT, pady=10)
	
	go=Button(buttonframe, text="Search", command=lambda:displayStrainSearchResult(species, strain.get("1.0",END)))
	go.pack(side=RIGHT, pady=10)
	
	strainframe.pack(padx=20,fill=X)
	buttonframe.pack(padx=20,fill=X)
	
	search.mainloop()
	
def searchByLocation(species):

#	from Tkinter import Tk, Label, Frame, LEFT, RIGHT, Text, X, StringVar, OptionMenu, Button
	search=Tk()
	search.wm_title("Search")
	search.update()
	
	instructions=Label(search, text="Please select the appropriate location.")
	locationframe=Frame(search)
	buttonframe=Frame(search)
	
	locationV=StringVar(search)
	locations=getAllLocations(-1,'a',species)
	loclist=set([l.getString() for l in species.dummyLocations])
	if len(locations)>0:
		for l in locations:
			if l.length!=0:
				loclist.add(l.getString())
	loclist=sorted(list(loclist))
	locationV.set(loclist[0])

	
	locationL=Label(locationframe, text="Location", height=1)
	location=apply(OptionMenu,(locationframe, locationV)+tuple(loclist))

	locationL.pack(side=LEFT, pady=10)
	location.pack(side=RIGHT, pady=10)
	
	go=Button(buttonframe, text="Search", command=lambda:displayLocationSearchResult(species, locationV.get()))
	go.pack(side=RIGHT, pady=10)
	
	locationframe.pack(padx=20,fill=X)
	buttonframe.pack(padx=20,fill=X)
	
	#search.lift()
	search.mainloop()

def getGDLocation(species):

#	from Tkinter import Tk, Label, StringVar, Frame, IntVar, OptionMenu, LEFT, RIGHT, Checkbutton, X, Button
	search=Tk()
	search.wm_title("Search")
	search.update()
	
	instructions=Label(search, text="Please select the appropriate location.")
	locationframe=Frame(search)
	buttonframe=Frame(search)
	checkframe=Frame(search)
	checkframe2=Frame(search)
	
	locationV=StringVar(search)
	locations=getAllLocations(-1,'a',species)
	loclist=set([l.getString() for l in species.dummyLocations])
	if len(locations)>0:
		for l in locations:
			if l.length!=0:
				loclist.add(l.getString())
	loclist=sorted(list(loclist))
	loclist.insert(0,"Any")
	locationV.set(loclist[0])

	
	locationL=Label(locationframe, text="Location", height=1)
	location=apply(OptionMenu,(locationframe, locationV)+tuple(loclist))

	locationL.pack(side=LEFT, pady=10)
	location.pack(side=RIGHT, pady=10)
	
	freqval=IntVar()
	freq=Checkbutton(checkframe, text="Show Frequency Distribution", height=1, variable=freqval, onvalue=True, offvalue=False)
	freq.select()
	
	lengthval=IntVar()
	length=Checkbutton(checkframe2, text="Show Length Distributions", height=1, variable=lengthval, onvalue=True, offvalue=False)
	length.select()
	
	freq.pack(side=LEFT, pady=10)
	length.pack(side=LEFT, pady=10)
	
	go=Button(buttonframe, text="Search", command=lambda:displayGeneticDiversity(locationV.get(),species,freqval.get(),lengthval.get()))
	go.pack(side=RIGHT, pady=10)
	
	locationframe.pack(padx=20,fill=X)
	checkframe.pack(padx=20,fill=X)
	checkframe2.pack(padx=20,fill=X)
	buttonframe.pack(padx=20,fill=X)
	
	search.mainloop()
	
def displayGeneticDiversity(find, species, plotFreq, plotLen):
	GD=calculateGeneticDiversity(species, find.strip(), plotFreq,plotLen)
	unique=getUnique(species, find.strip())
	
	title="Genetic Diversity Report for "+find.strip()
	
	printstring=""
	
	occurrences={}
	
	names=GD[-1]
	for name,occ in names.iteritems():
		if occ in occurrences:
			occurrences[occ].append(name)
		else:
			occurrences[occ]=[name]
	printstring+="Total Number of Occurrences:"
	for occ,lst in occurrences.iteritems():
		printstring+="\n\t"+str(occ)+" : "+listtostring(lst,", ")

	printstring+= "\n\nRepeats Unique to the Region:"
	for u in unique:
		printstring+="\n"+ "\t"+u
	if len(unique)==0:
		printstring+="\n"+ "\tNone"
	printstring+="\n"+ "\nGenetic Diversity:"
	printstring+="\n"+ "\tGD2b="+str(GD[0]*100)
	printstring+="\n"+ "\tGDM1(Local)="+str(GD[1])
	printstring+="\n"+ "\tGDM1(Global)="+str(GD[2])
	printstring+="\n\n"+ "Variance in Repeat Frequency:"
	printstring+="\n"+ "\tGDM2(Local)="+str(GD[3])
	printstring+="\n"+ "\tGDM2(Global)="+str(GD[4])+"\n"
	
	printstring+="\n"+ "Values defined in user guide"
	#printstring+="\n"+ "1: total unique repeats/total strains"
	#printstring+="\n"+ "2: total unique repeats/total repeats"
	#printstring+="\n"+ "3: avg(regularized repeat frequency/total repeats)"
	#printstring+="\n"+ "4: avg(regularized repeat frequency in each strain/repeats in strain)"
	#printstring+="\n"+ "ex. Strains={ABCD,ABE,DDEF} \n'1'=6/3, \n'2'=6/10, \n'3'=(2/10+2/10+1/10+3/10+2/10+1/10)/6=11/60, \n'4'=((1/4+1/4+1/4+1/4)/4+(1/3+1/3+1/3)/3+(2/3+1/3+1/3)/4)/3=(1/4+1/3+4/9)/3=37/108"

	
	#process=multiprocessing.Process(target=popupWindow, args=(title, printstring))
	#process.daemon = True
	#process.start()
	popupWindow(title, printstring)
	
def displayRepeatSearchResult(species, find,maxdistance):
	printstring=""
	
	#find=str(find)#.decode('utf-8')
	
	p=find.split(">")
	if len(p)>1:
		for n,i in enumerate(p):
			if i.strip()!="":
				p[n]='>'+i

	title="Repeat Search Result"
	c=0
	for i in p:
		if i.strip()=="":
			continue
		c+=1
		i,name=decodeFASTA(i)
	
		id=findID(i,species.repeats)
		if id==None:
			for repeat in species.repeats:
				if sanitize(i)==repeat.sequence:
					id=repeat.ID
					break
		
		printstring+="Sequence "+str(c)+":\n"
		
		if name != "":
			printstring+=name+"\n"
		
		if id==None:
			printstring+= "Error: no repeat found with sequence or name "+i+"\n\n"
			continue
			
		repeat=getObjectbyID(id, species.repeats)
		printstring+="Result: "+listtostring(repeat.name, "; ")+ " : "+ repeat.sequence
		#highlight=[]
		#line=1
		printstring+="\n\tSubset of: "
		if len(repeat.subsetOf)==0:
			printstring+="None"
		else:
			for id in repeat.subsetOf:
				#line+=1
				printstring+="\n\t\t"+findnames(id, species.repeats)
		if maxdistance>0:
			distances={}
			furthest=0
			far=[]
			for r in species.repeats:
				d=levenshteinDistance(r.sequence,repeat.sequence)
				if d==furthest:
					far.append(r)
				if d>furthest:
					furthest=d
					far=[r]
				if d<=maxdistance and d>0:
					#line+=1
					#if len(repeat.sequence)>=len(r.sequence):
					#	for ind, char in repeat.sequence:
					#		if r[ind]!=
					#else:
					#	for ind, char in r.sequence:
					#printstring+="\n\t\t"+listtostring(r.name,"; ")+" : "+r.sequence+" : distance "+str(distance)
					distances[r]=d
					
			printstring+= "\n\tSimilar repeats:"
			for ind,dist in sorted(distances.items(), key=operator.itemgetter(1)):
				printstring+="\n\t\t"+listtostring(ind.name,"; ")+" : "+ind.sequence+" : distance "+str(dist)
			
			printstring+="\n\tRepeats at maximum distance, "+str(furthest)+":"
			for r in far:
				printstring+="\n\t\t"+listtostring(r.name,"; ")+" : "+r.sequence
			
		printstring+= "\n\tLocations:"
		for location in getAllLocations(id, 'r', species):
			printstring+= "\n\t\t"+location.getString()
		printstring+= "\n\tStrains:"
		for strain in getAllStrains(id, species):
			printstring+="\n\t\t"+listtostring(strain.name, "; ")+ " : "+ listtostring(matchnames(strain.sequence, species.repeats), " ")
			for location in strain.location:
				printstring+="\n\t\t\t"+location.getString()
		printstring+= "\n\tPapers:"
		for paper in getAllPapers(id, 'r', species):
			printstring+= "\n\t\t"+paper.line1+"\n\t\t\t"+paper.line2+"\n\t\t\t"+paper.line3
		
		printstring+="\n"
		
	#process=multiprocessing.Process(target=popupWindow, args=(title, printstring))
	#process.daemon = True
	#process.start()
	popupWindow(title, printstring)

def displayStrainSearchResult(species, find):
	id=findID(find,species.strains)
	if id==None:
		repeats=parserepeats(find.strip(), species)
		id=identifystrain(repeats,species)
	
	if id==None:
		print "Error: no strain found with given sequence or name"
		return
		
	strain=getObjectbyID(id, species.strains)
	title=listtostring(strain.name, "; ")+ " : "+ listtostring(matchnames(strain.sequence, species.repeats), " ")
	printstring="Edit Distance Between Repeats:"
	distances={}
	uniqueRs=getAllRepeatsFrom([strain],species)
	if len(uniqueRs)>1:
		for ind, r in enumerate(uniqueRs):
			for r2 in uniqueRs[ind+1:]:
				distances[(findnames(r.ID,uniqueRs),findnames(r2.ID,uniqueRs))]=levenshteinDistance(r.sequence,r2.sequence)
	else:
		distances [(findnames(uniqueRs[0].ID,uniqueRs),findnames(uniqueRs[0].ID,uniqueRs))]=0
	for ind,dist in sorted(distances.items(), key=operator.itemgetter(1)):
		printstring+="\n\t"+ind[0]+" to "+ind[1]+" : "+str(dist)
	
	printstring+="\n\tMean:"+str(np.mean(distances.values()))
	printstring+="\nLocations:"
	for location in getAllLocations(id, 's', species):
		printstring+= "\n\t"+location.getString()
	printstring+="\nPapers:"
	for paper in getAllPapers(id, 's', species):
		printstring+= "\n\t"+paper.line1+"\n\t\t"+paper.line2+"\n\t\t"+paper.line3
	
	#process=multiprocessing.Process(target=popupWindow, args=(title, printstring))
	#process.daemon = True
	#process.start()
	popupWindow(title, printstring)

def displayLocationSearchResult(species,find):
	if len(find.split(","))>3:
		print "Error: too many commas in location. Remember to follow the format"
		return
		
	strains=getAllStrainsFrom(find, species)
	repeats=getAllRepeatsFrom(strains, species)
	papers=getAllPapersFrom(strains, species)
	
	title=Location(find).getString()
	printstring="Repeats:"
	for repeat in repeats:
		printstring+= "\n\t"+listtostring(repeat.name, "; ")+" : "+repeat.sequence
	printstring+="\nStrains:"
	for strain in strains:
		printstring+="\n\t"+listtostring(strain.name, "; ")+ " : "+ listtostring(matchnames(strain.sequence, species.repeats), " ")
	printstring+="\nPapers:"
	for paper in papers:
		printstring+="\n\t"+paper.line1+"\n\t\t"+paper.line2+"\n\t\t"+paper.line3
		
	#process=multiprocessing.Process(target=popupWindow, args=(title, printstring))
	#process.daemon = True
	#process.start()
	popupWindow(title, printstring)
	
def displaySearchResult(species, repeats, strains, location, makeMap, win, sizemod, legendmod, reduceNoise):
	repeats=repeats.strip().split(';')
	strains=strains.strip().split(';')
	location=location.strip()
	
	repeatIDs=[]
	strainIDs=[]
	
	r=[] #list of input repeat IDs
	rlats=[]
	rlons=[]
	s=[] #list of input strain IDs
	slats=[]
	slons=[]
	rwhite=[]
	swhite=[]
	
	#geocoder=GoogleV3()
	
	#geocode entered location
	FilterCountry=None
	FilterProvince=None
	if location!="" and location!=None and location!='Any':
		latitude=0
		longitude=0
		st=getAllStrainsFrom(location, species)
		rep=getAllRepeatsFrom(st, species)
		fl=location.split(',')
		FilterCountry=fl[0].strip()
		if len(fl)>1:
			FilterProvince=fl[1].strip()
		
	else:
		st=species.strains
		rep=species.repeats
		latitude=0
		longitude=0
		
	for i in st:
		if reduceNoise == True:
			countries=set()
			provinces=set()
			counties=set()
			if len(i.location)>=2:
				for l in i.location:
					countries.add(l.country)
					if l.length>1:
						provinces.add(l.province)
					if l.length>2:
						counties.add(l.city)
			if len(countries)<2 and len(provinces)<2 and len(counties)<2:
				continue
		swhite.append(i.ID)

	for i in rep:
		if reduceNoise == True:
			locs=getAllLocations(i.ID, "r", species)
			countries=set()
			provinces=set()
			counties=set()
			if len(locs)>=2:
				for l in locs:
					countries.add(l.country)
					if l.length>1:
						provinces.add(l.province)
					if l.length>2:
						counties.add(l.city)
			if len(countries)<2 and len(provinces)<2 and len(counties)<2:
				#print listtostring(matchnames(seq, species.repeats)+" only found once"
				continue
		rwhite.append(i.ID)
			
	if 'All' in repeats:
		repeatIDs=rwhite
		rwhite=[]
	elif repeats==[""] or repeats==["\n"]:
		repeatIDs=[]
	else:
		for repeat in repeats:
			repeat=repeat.strip()
			id=findID(repeat, species.repeats)
			if id==None:
				for rp in species.repeats:
					if sanitize(repeat)==rp.sequence:
						id=rp.ID
						break
			if id!=None:
				repeatIDs.append(id)
		
	if 'All' in strains:
		strainIDs=swhite
		swhite=[]
	elif strains==[""] or strains==["\n"]:
		strainIDs=[]
	else:
		for strain in strains:
			strain=strain.strip()
			id=findID(strain, species.strains)
			if id==None:
				rlist=parserepeats(strain.strip(), species)
				id=identifystrain(rlist,species)
			if id!=None:
				strainIDs.append(id)
	
	cnames={}
	
	#parse repeats/strains and store lats & lons
	for repeat in repeatIDs:
		if repeat in rwhite or rwhite==[]:
			r.append(repeat)
			rlat=[]
			rlon=[]
			loc=getAllLocations(repeat, "r", species, True)
			for l in loc:
				if l.latitude==None or l.longitude==None :
					print "Attention: coordinates could not be found for", l.getString(),". This point will be skipped. If this is a valid location, run the geocoding command in the main menu again.\n"
					#gcl=geocoder.geocode(l.getString())
					#if gcl==None:
					#	print "Attention: coordinates could not be found for", l.getString(),". This point will be skipped."
					#	l.latitude=-1000
					#	l.longitude=-1000
					#	continue
					#l.latitude=gcl.latitude
					#l.longitude=gcl.longitude
					#rlat.append(gcl.latitude)
					#rlon.append(gcl.longitude)
					continue
				elif l.latitude==-1000 or l.longitude==-1000 :
					print "Attention: coordinates could not be found for", l.getString(),". This point will be skipped."
					continue
				else:
					rlat.append(l.latitude)
					rlon.append(l.longitude)
				cnames[(l.longitude,l.latitude)]=l.getString()
			rlats.append(list(rlat))
			rlons.append(list(rlon))
		
	for strain in strainIDs:
		if strain in swhite or swhite==[]:		
			s.append(strain)
			slat=[]
			slon=[]
			loc=getAllLocations(strain, "s", species, True)
			for l in loc:
				if l.latitude==None or l.longitude==None:
					print "Attention: coordinates could not be found for", l.getString(),". This point will be skipped. If this is a valid location, run the geocoding command in the main menu again.\n"
					#gcl=geocoder.geocode(l.getString())
					#if gcl==None:
					#	print "Attention: coordinates could not be found for", l.getString(),". This point will be skipped."
					#	l.latitude=-1000
					#	l.longitude=-1000
					#	continue
					#l.latitude=gcl.latitude
					#l.longitude=gcl.longitude
					#slat.append(gcl.latitude)
					#slon.append(gcl.longitude)
					continue
				elif l.latitude==-1000 or l.longitude==-1000 :
					print "Attention: coordinates could not be found for", l.getString(),". This point will be skipped."
					continue
				else:
					slat.append(l.latitude)
					slon.append(l.longitude)
				cnames[(l.longitude,l.latitude)]=l.getString()
			slats.append(list(slat))
			slons.append(list(slon))
	#add errors for missing lons&lats
	
	#mapPopup(latitude, longitude, rlons, rlats, r, slons, slats, s, cnames, species, makeMap)
	
	#process=multiprocessing.Process(target=mapPopup, args=(latitude, longitude, rlons, rlats, r, slons, slats, s, cnames, species, makeMap, sizemod, legendmod, reduceNoise))
	#process.start()
	mapPopup(latitude, longitude, rlons, rlats, r, slons, slats, s, cnames, species, makeMap, sizemod, legendmod, reduceNoise)
	
	return

#http://www.geophysique.be/2010/11/15/matplotlib-basemap-tutorial-05-adding-some-pie-charts/
#added colors parameter, fixed plot appearance with 1 and 2 colors
#plots a pie chart on a given axis of a basemap
def draw_pie(ax,ratios, X, Y, size, colors, borderColor='black'):
	N = len(ratios)

	xy = []

	start = 0.

	for ratio in ratios:
		x = [0] + np.cos(np.linspace(2*math.pi*start,2*math.pi*(start+ratio), 30)).tolist()
		y = [0] + np.sin(np.linspace(2*math.pi*start,2*math.pi*(start+ratio), 30)).tolist()

		xy1 = zip(x,y)
		xy.append(xy1)
		start += ratio

	ax.scatter([X],[Y], marker='o', s=math.pi*((math.sqrt(size/math.pi)+1.5)**2), c=borderColor, alpha=1, zorder=2, edgecolors=borderColor)
	for i, xyi in enumerate(xy):
		ax.scatter([X],[Y] , marker=(xyi,0), s=size, facecolor=colors[i], linewidth=0, alpha=1, zorder=2)	
		
def combineCoordinates(lons,lats,IDs):
	coords={}

	#initialize
	for i in range(len(lons)):
		for j in range(len(lons[i])):
			if (lons[i][j],lats[i][j]) not in coords:
				coords[(lons[i][j],lats[i][j])]=[]
	
	#set
	for i in range(len(IDs)):
		for j in range(len(lons[i])):
			coords[(lons[i][j],lats[i][j])].append(IDs[i])
	
	return coords

#deprecated	
def plotBorders(map, axis, location):
	r = shapefile.Reader(location)
	shapes = r.shapes()
	records = r.records()

	for record, shape in zip(records,shapes):
		lons,lats = zip(*shape.points)
		data = np.array(map(lons, lats)).T
	 
		if len(shape.parts) == 1:
			segs = [data,]
		else:
			segs = []
			for i in range(1,len(shape.parts)):
				index = shape.parts[i-1]
				index2 = shape.parts[i]
				segs.append(data[index:index2])
			segs.append(data[index2:])
	 
		lines = LineCollection(segs,antialiaseds=(1,))
		lines.set_edgecolors('black')
		lines.set_linewidth(0.25)
		axis.add_collection(lines)

#loclat=latitude of map center
#loclon=longitude of map center
#lons=2D array of longitudes for each repeat or strain
#lats=2D array of latitudes for each repeat or strain
#IDs=id of each repeat or strain (number and order for lons, lats and IDs must match!)
#species=species of interest
#s for strain, r for repeat	
#if clusters=True, rIDs is treated as a list of cluster IDs, strains should not be passed
def createMap(rlons, rlats, rIDs, slons, slats, sIDs, coordnames, species, sizemod, legendmod, reduceNoise, clusters=False):

#	from Tkinter import Tk
	
	rcoords=combineCoordinates(rlons,rlats,rIDs) #repeat IDs mapped to their respective coordinates ex. (12,-39)<-[2,5,45,1]
	scoords=combineCoordinates(slons,slats,sIDs) #strain IDs mapped to their respective coordinates ex. (12,-39)<-[2,5,45,1]

	rnames=[]
	snames=[]
	rn={}
	sn={}
	
	#openQgis()
	if clusters==False:
		for id in sIDs:
			seq=getObjectbyID(id, species.strains).sequence
			snames.append("("+listtostring(matchnames(seq, species.repeats), " ")+")")
			sn[id]="("+listtostring(matchnames(seq, species.repeats), " ")+")"
			
		for id in rIDs:
			n=getObjectbyID(id, species.repeats).name
			rnames.append(listtostring(n,';'))
			rn[id]=listtostring(n,';')
	else:
		for id in rIDs:
			rnames.append(str(id))
		
	#exportCSV(rcoords, rn, "repeatmap.csv", species)
	#exportCSV(scoords, sn, "strainmap.csv", species)
	
	ax = mpl.subplot(111)
	 
	m = Basemap(projection='merc',llcrnrlat=-80,urcrnrlat=80,llcrnrlon=-180,urcrnrlon=180,lat_ts=20,resolution='i',ellps='WGS84')
	#m.drawcountries(linewidth=1)
	m.readshapefile("MapData/Admin_0", "countries", linewidth=2, ax=ax)
	m.drawcoastlines(linewidth=1)
	m.drawmapboundary(fill_color="#D3E9F0")
	m.fillcontinents(color="white", lake_color="#D3E9F0", zorder=0)
	 
	#plotBorders(m, ax, r"MapData\Admin_1")
	m.readshapefile("MapData/Admin_1", "provinces", linewidth=.5, ax=ax)
	
	if len(rnames)>0 and len(snames)>0:
		mpl.title ("Geographic Distribution of Strains and Repeats")
		mpl.figtext(.5,.005,'Dark grey borders correspond to genotypes while black borders correspond to repeats. Larger circles correspond to larger scope areas. \nFor instance, a circle representing strains in the U. S. A. would be larger than one corresponding to strains in Texas.',fontsize=10,ha='center')
	else:
		if len(snames)>0:
			mpl.title ("Geographic Distribution of Strains")
		if len(rnames)>0:
			mpl.title ("Geographic Distribution of Repeats")
						
	if sIDs!=[]:		
		sax = mpl.subplot(111)
		colors = cm.nipy_spectral(np.linspace(.05, .95, len(sIDs)))
		for i in range(len(snames)):
			m.scatter (0, 0, c=colors[i], marker="o", s=0, label=snames[i].decode('utf-8'))
			
		for coords in scoords:
			scope=len(coordnames[coords].split(','))
			x,y=m(coords[0],coords[1])
			#lx,ly=m(coords[0]+3/scope,coords[1])
			#mpl.text(lx,ly,coordnames[coords],fontsize=8,zorder=3)	#print coordnames
			cl=[]
			for id in scoords[coords]:
				cl.append(colors[sIDs.index(id)])
			draw_pie(sax,[1.0/len(cl)]*len(cl),x,y,(1200*sizemod)/scope, cl, '#303030')
			
	if rIDs!=[]:		
		rax = mpl.subplot(111)
		colors = cm.gist_rainbow(np.linspace(.05, 1, len(rIDs)))
		for i in range(len(rnames)):
			m.scatter (0, 0, c=colors[i], marker="o", s=0, label=rnames[i].decode('utf-8'))
			
		for coords in rcoords:
			scope=len(coordnames[coords].split(','))
			x,y=m(coords[0],coords[1])
			#lx,ly=m(coords[0]+3/scope,coords[1])
			#mpl.text(lx,ly,coordnames[coords],fontsize=8,zorder=3)	#print coordnames
			cl=[]
			for id in rcoords[coords]:
				cl.append(colors[rIDs.index(id)])
			draw_pie(rax,[1.0/len(cl)]*len(cl),x,y,(240*sizemod)/scope, cl,'#000000')
		

	mpl.rc('font', family='Arial')
	lgnd=mpl.legend(
		scatterpoints=1, 
		loc=legendmod, 
		fontsize=12, 
		ncol=((len(rIDs)+len(sIDs))/60)+1, 
		#bbox_to_anchor=(1.1, 1), 
		borderaxespad=0.0,
		handletextpad=-0.1,
		handlelength=1.5,
		labelspacing=0.12,
		borderpad=0.3,
		columnspacing=0.2)
	for h in lgnd.legendHandles:
		h._sizes=[50]
	mpl.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)
	mpl.show(block=False)	
	
#Pop up a plotGD plot
def plot(x,y,title,xlabel,ylabel):
	fig = mpl.figure()
	mpl.title(title)
	ax = fig.add_subplot(111)
	ax.plot(x,y,'bo',picker=5)
	ax.plot(x,y,'b-',picker=5)
	mpl.ylabel(ylabel)
	mpl.xlabel(xlabel)
	#eventually do labels if it's worth it
	mpl.xlim((0, 1)) 
	mpl.ylim((0, 1))

	ticks = [n/10.0 for n in range(0, 10)]
	mpl.yticks(ticks)
	mpl.xticks(ticks)
	def onpick(event):
		line=event.artist
		x=line.get_xdata()
		y=line.get_ydata()
		ind=event.ind
		#dostuff
	fig.canvas.mpl_connect('pick_event', onpick)
	mpl.show(block=False)
	

