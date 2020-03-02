import sys
sys.path.append('../code')
import subprocess
import matplotlib.pyplot as plt
import numpy as np
import os
import fnmatch
import time
import pickle
from tools import general_tools as gt

pathToResults = "../../results"

def main():

	# eesAmplitudes = np.linspace(220,300,5)
	eesAmplitudes = [235,250]
	eesFrequencies = [5,10,20,40,60]
	nProc = 4
	seed = "1"
	species = "human"
	totTime = "10000"

	if species == "rat": nnStructureFile = "frwSimRat.txt"
	elif species == "human": nnStructureFile = "frwSimHuman.txt"
	muscleResponses = []
	kinBins = []
	labels = []
	count=0.
	percLastPrint=0.
	printPeriod = 0.05
	nSim = len(eesAmplitudes)*len(eesFrequencies)

	for i,eesAmplitude in enumerate(eesAmplitudes):
		for j,eesFrequency in enumerate(eesFrequencies):
			labels.append("%duA\n%dHz"%(eesAmplitude,eesFrequency))
			name = "_exp"
			resultName = "CybexMuscleResponses_%dHz_%duA"%(eesFrequency,eesAmplitude)+"_"+species+"_"+name
			resultFile = gt.find("*"+resultName+".p",pathToResults)
			if not resultFile:
				program = ['mpiexec','-np',str(nProc),'python','./scripts/runCybexForSimMuscleSpindles.py',\
						str(eesFrequency),str(eesAmplitude),species,nnStructureFile,name,"--simTime",totTime,"--seed",seed]
				gt.run_subprocess(program)
				resultFile = gt.find("*"+resultName+".p",pathToResults)
			with open(resultFile[0], 'r') as pickle_file:
				muscleResponses.append(pickle.load(pickle_file))
				kinBins.append(pickle.load(pickle_file))

			count+=1
			if count/nSim-percLastPrint>=printPeriod:
				percLastPrint=count/nSim
				print str(round(count/nSim*100))+"% of simulations performed..."


	figName = time.strftime("%Y_%m_%d_CybexExperimentMuscleResponses_"+species+".pdf")
	plot_muscle_responses(muscleResponses,kinBins,labels,figName)


def plot_muscle_responses(muscleResponses,kinBins,labels,figName,showPlot=True):

	nMuscles = len(muscleResponses[0].keys())
	nTrials = len(muscleResponses)
	nCells = 169.
	nBins = 10
	index = np.arange(nBins)
	bar_width = 0.35
	opacity = 1
	kinColors = ["#2C3E50","#E74C3C"]*int(round(nBins/2.))
	error_config = {'ecolor': '0.3'}
	figSize = 0.7
	fig, ax = plt.subplots(nMuscles+1,nTrials, figsize=(16*figSize,9*figSize),facecolor='#ECF0F1',sharey='row')

	fig.suptitle("Muscle responses")

	for i in xrange(nTrials):
		for j,muscle in enumerate(muscleResponses[0]):
			if nTrials == 1: currAx = ax[j+i]
			else: currAx = ax[j,i]
			currAx.bar(index, np.array(muscleResponses[i][muscle]["mean"])/nCells, bar_width,
							 alpha=opacity,
							 color='#2C3E50',
							 yerr=np.array(muscleResponses[i][muscle]["std"])/nCells,
							 error_kw=error_config,
							 ecolor = '#E74C3C',
							 align='center')

			for dataBin in index:
				currAx.scatter([dataBin]*len(muscleResponses[i][muscle]["values"][dataBin])\
					,np.array(muscleResponses[i][muscle]["values"][dataBin])/nCells\
					,zorder=10, color='#2980B9',s=3,edgecolor='none')

			currAx.set_facecolor('#ECF0F1')
			currAx.xaxis.set_ticks([])
			if j==0: currAx.set_title(labels[i])
			if i==0: currAx.set_ylabel(muscle)

		# Plot kinematics
		offset = 0
		if nTrials == 1: currAx = ax[-1]
		else: currAx = ax[-1,i]
		for k in xrange(nBins):
			for z,kinData in enumerate(kinBins[i][k]):
				time = range(offset,offset+len(kinData))
				currAx.plot(time,kinData,color=kinColors[k])
			currAx.set_facecolor('#ECF0F1')
			currAx.xaxis.set_ticks([])
			currAx.yaxis.set_ticks([])
			offset += len(kinBins[i][k][0])
		if i==0: currAx.set_ylabel("Kinematics")

	plt.savefig(pathToResults+"/"+figName, format="pdf",transparent=True)
	plt.show(block=showPlot)

if __name__ == '__main__':
	main()
