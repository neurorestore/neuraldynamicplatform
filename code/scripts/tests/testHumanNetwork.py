import argparse
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
from tools import structures_tools as tls
import warnings

pathToResults = "../../results/testHuman"

def main():



	eesAmplitudes = [235,250,270]
	eesFrequencies = [40,60,80]
	eesLowAmplitudes = ["%0.2_0_0"]
	eesHighFrequencies = [600,700,800]
	delays = [2,16]
	templateFile = "templateFrwSimHuman.txt"
	# 1
	# w1 = 0.0225
	# w2 = 0.0357
	# w3 = 0.0165
	# 2 - best
	w1 = 0.0225
	w2 = 0.0385
	w3 = 0.0165
	# 3
	# w1 = 0.0225
	# w2 = 0.0385
	# w3 = 0.0137
	# 4
	# w1 = 0.0225
	# w2 = 0.041
	# w3 = 0.0165

	simLabel = "_testHuman"
	nProc = 4
	totSimTime = 6000
	seed = "1"
	species = "human"
	extMuscle = "GL"
	flexMuscle = "TA"

	nSim = (len(eesFrequencies)*len(eesAmplitudes)+len(eesLowAmplitudes)*len(eesHighFrequencies))*len(delays)
	count=0.
	percLastPrint=0.
	printPeriod = 0.05

	for eesFrequency in eesFrequencies:
		for eesAmplitude in eesAmplitudes:
			for delay in delays:
				inputFile = "generatedStructures/testHuman_d_"+str(delay)+"_w1_"+str(w1)+"_w2_"+str(w2)+"_w3_"+str(w3)+".txt"
				tls.modify_network_structure(templateFile,inputFile,delay,[w1,w2,w3])
				name = "Tonic_w1_"+str(w1)+"_w2_"+str(w2)+"_w3_"+str(w3)+"_"+str(eesAmplitude)+simLabel

				resultFile = gt.find("*"+str(eesFrequency)+"Hz_Delay_"+str(delay)+"ms*"+name+".p",pathToResults)
				if not resultFile:
					program = ['mpiexec','-np',str(nProc),'python','./scripts/runForSimMuscleSpindles.py',\
						str(eesFrequency),str(eesAmplitude),species,inputFile,name,"--simTime",str(totSimTime),"--seed",seed]
					gt.run_subprocess(program)
				count+=1
				if count/nSim-percLastPrint>=printPeriod:
					percLastPrint=count/nSim
					print str(round(count/nSim*100))+"% of simulations performed..."

	for eesHighFrequency in eesHighFrequencies:
		for eesLowAmplitude in eesLowAmplitudes:
			eesLowAmpName = eesLowAmplitude[1:]
			for delay in delays:
				inputFile = "generatedStructures/testHuman_d_"+str(delay)+"_w1_"+str(w1)+"_w2_"+str(w2)+"_w3_"+str(w3)+".txt"
				name = "HFLA_"+eesLowAmpName+"_w1_"+str(w1)+"_w2_"+str(w2)+"_w3_"+str(w3)+"_"+simLabel

				resultFile = gt.find("*"+str(eesHighFrequency)+"Hz_Delay_"+str(delay)+"*"+name+".p",pathToResults)
				if not resultFile:
					program = ['mpiexec','-np',str(nProc),'python','./scripts/runForSimMuscleSpindles.py',\
						str(eesHighFrequency),eesLowAmplitude,species,inputFile,name,"--simTime",str(totSimTime),"--seed",seed]
					gt.run_subprocess(program)
				count+=1
				if count/nSim-percLastPrint>=printPeriod:
					percLastPrint=count/nSim
					print str(round(count/nSim*100))+"% of simulations performed..."

	#Plotting
	size = 0.8
	for eesFrequency in eesFrequencies:
		fig,ax = plt.subplots(len(eesAmplitudes),2,figsize=(16*size,9*size))
		fig.suptitle("frequency = %d w1:%f w2:%f w3:%f"%(eesFrequency,w1,w2,w3),fontsize=14)
		for i,delay in enumerate(delays):
			for j,eesAmplitude in enumerate(eesAmplitudes):
				patternTonic = "*"+str(eesFrequency)+"Hz_Delay_"+str(delay)+\
					"ms_human_Tonic_w1_"+str(w1)+"_w2_"+str(w2)+"_w3_"+str(w3)+"_"+str(eesAmplitude)+simLabel+".p"
				meanFr = load_results(patternTonic,"../../results/")
				ax[j,i].set_ylabel("amplitude: %d"%(eesAmplitude))
				if meanFr:
					ax[j,i].plot(meanFr[extMuscle]['Mn'],'r')
					ax[j,i].plot(meanFr[extMuscle]['IaInt'],'-.r')
					ax[j,i].plot(meanFr[flexMuscle]['Mn'],'b')
					ax[j,i].plot(meanFr[flexMuscle]['IaInt'],'-.b')

	for eesLowAmplitude in eesLowAmplitudes:
		eesLowAmpName = eesLowAmplitude[1:]
		fig,ax = plt.subplots(len(eesHighFrequencies),2,figsize=(16*size,9*size))
		fig.suptitle("amplitude %s w1:%f w2:%f w3:%f"%(eesLowAmpName,w1,w2,w3),fontsize=14)
		for i,delay in enumerate(delays):
			for j,eesHighFrequency in enumerate(eesHighFrequencies):
				patternHFLA = "*"+str(eesHighFrequency)+"Hz_Delay_"+str(delay)+\
					"ms_human_HFLA_"+eesLowAmpName+"_w1_"+str(w1)+"_w2_"+str(w2)+"_w3_"+str(w3)+"_"+simLabel+".p"
				meanFr = load_results(patternHFLA,"../../results/")
				ax[j,i].set_ylabel("ees high frequency: %d"%(eesHighFrequency))
				if meanFr:
					ax[j,i].plot(meanFr[extMuscle]['Mn'],'r')
					ax[j,i].plot(meanFr[extMuscle]['IaInt'],'-.r')
					ax[j,i].plot(meanFr[flexMuscle]['Mn'],'b')
					ax[j,i].plot(meanFr[flexMuscle]['IaInt'],'-.b')

	plt.show()












def load_results(pattern,resultsFolder):
	fileToLoad = gt.find(pattern, resultsFolder)
	if not fileToLoad:
		warnings.warn('\tfile with pattern: '+pattern+' not found')
		return None
	else:
		print "\tloading file: "+fileToLoad[0]
		with open(fileToLoad[0], 'r') as pickle_file:
			_ = pickle.load(pickle_file)
			meanFr = pickle.load(pickle_file)
		return meanFr

if __name__ == '__main__':
	main()
