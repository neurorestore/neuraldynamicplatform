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

pathToResults = "../../results"

def main():
	""" This program launches several static reflex recordings with different random seeds """

	parser = argparse.ArgumentParser(description="launch several static reflex recordings with different random seeds")
	parser.add_argument("eesStartingAmplitude", help="ees starting amplitude (times motor thresold 0-3)")
	parser.add_argument("eesMaxAmplitude", help="ees max amplitude (times motor thresold 0-3)")
	parser.add_argument("eesSteps", help="number of stimulatin steps")
	parser.add_argument("nSim", help="number of simulations to run", type=int)
	parser.add_argument("inputFile", help="neural network structure file")
	parser.add_argument("outFileName", help="name to add at the output files")
	args = parser.parse_args()

	nProc = 4
	count=0.
	percLastPrint=0.
	printPeriod = 0.05

	for n in xrange(args.nSim):
		name = "batchSRR_seedn_"+str(n)+"_"+args.outFileName

		resultName = "_static_reflex_recording_min"+args.eesStartingAmplitude+"_max"+str(float(args.eesMaxAmplitude))+name
		resultFile = gt.find("*"+resultName+".p",pathToResults)
		if not resultFile:
			program = ['python','./scripts/runStaticReflexRecordings.py',\
					args.eesStartingAmplitude,args.eesMaxAmplitude,args.eesSteps,args.inputFile,name,"--noPlot","--seed",str(n),"--membranePotential"]#,"--seed",str(1) 'mpiexec','-np',str(nProc),
			gt.run_subprocess(program)

		count+=1
		if count/args.nSim-percLastPrint>=printPeriod:
			percLastPrint=count/args.nSim
			print str(round(count/args.nSim*100))+"% of simulations performed..."

	figName = time.strftime("/%Y_%m_%d_Batch_SRR_nSim_"+str(args.nSim)+"_min"+args.eesStartingAmplitude+"_max"+args.eesMaxAmplitude+"_"+args.outFileName+".pdf")
	plot_afferents(args.nSim,args.eesStartingAmplitude,args.eesMaxAmplitude,figName,args.outFileName)

def plot_afferents(nSimulations,eesStartingAmplitude,eesMaxAmplitude,figName,outFileName,showPlot=False):
	""" Plots the averaged afferents firing rates. """

	taStat = []
	gmStat = []
	for n in xrange(nSimulations):
		name = "batchSRR_seedn_"+str(n)+"_"+outFileName
		#name = "_static_reflex_recording_min"+eesStartingAmplitude+"_max"+str(float(eesMaxAmplitude))+"batchSRR_seedn_"+str(n)+"_"+outFileName
		resultFile = gt.find("*"+name+".p",pathToResults)
		print resultFile
		if len(resultFile)>1: print "Warning: multiple result files found!!!"
		with open(resultFile[0], 'r') as pickle_file:
			taSpikes = pickle.load(pickle_file)
			taEmg = pickle.load(pickle_file)
			taStatVal = pickle.load(pickle_file)
			gmSpikes = pickle.load(pickle_file)
			gmEmg = pickle.load(pickle_file)
			gmStatVal = pickle.load(pickle_file)
		taStat.append(taStatVal)
		gmStat.append(gmStatVal)

	fig, ax = plt.subplots(2, 3,figsize=(16,9),sharex='col',sharey='col')
	for flexOneSeed,extOneSeed in zip(taEmg,gmEmg):
		ax[0,1].plot(flexOneSeed)
		ax[1,1].plot(extOneSeed)
	for flexOneSeed,extOneSeed in zip(taSpikes,gmSpikes):
		ax[0,0].plot(flexOneSeed)
		ax[1,0].plot(extOneSeed)
	ax[0,2].bar(0.4, np.array(taStat).mean(), 0.2, yerr=np.array(taStat).std())
	ax[1,2].bar(0.4, np.array(gmStat).mean(), 0.2, yerr=np.array(gmStat).std())
	ax[0,0].set_ylabel('Flexor')
	ax[0,0].set_title('Mn action potentials')
	ax[0,1].set_title('EMG response')
	ax[0,2].set_title('Statistic')
	ax[0,2].set_xlim([0,1])
	ax[1,0].set_ylabel('Extensor')
	plt.savefig(pathToResults+figName, format="pdf",transparent=True)
	if showPlot: plt.show()

if __name__ == '__main__':
	main()
