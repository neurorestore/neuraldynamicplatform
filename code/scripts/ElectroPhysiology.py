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
from tools import post_processing_tools as ppt
from parameters import HumanParameters as hp
from parameters import RatParameters as rp

pathToResults = "../../results"

def main():
	""" This program launches a ForSimMuscleSpindles for different stimulation freqeuncies.
	The results are then plotted in order to see the effect of the stimulation
	frequency on the afferent firings.
	The program doesn't have to be executed by MPI.
	"""
	#Necessary Parameters for Simulation
	eesAmplitude = "230"
	eesAmplitudeName = "230"
	delay = "2"
	toAddname = ""
	species = "rat"
	#Paramters initialization
	totSimTime = rp.get_tot_sim_time()
	gaitCyclesFileName = rp.get_gait_cycles_file()
	muscles = rp.get_muscles()
	templateFile = "templateFrwSimRORa_2.txt"
	w1 = 0.011
	w2 = -0.005

	templateFile = "A08.txt"
	inputFileName = "A08"
	inputFile = "generatedStructures/"+inputFileName+".txt"
	tls.modify_network_structure(templateFile,templateFile,delay,[w1,w2])

	eesFrequencies = range(0,41,40)
	nProc = 4
	seed = "1"

	nSim = len(eesFrequencies)
	count=0.
	percLastPrint=0.
	printPeriod = 0.05

	# run simulations
	for i,eesFrequency in enumerate(eesFrequencies):
		name = "Tonic_FFS_"+inputFileName+"_freq_"+str(eesFrequency)
		resultFile = gt.find("*"+name+".p",pathToResults)
		if not resultFile:
			program = ['python','./scripts/runForSimMuscleSpindles_RORa.py',\
				str(eesFrequency),eesAmplitude,inputFile,name,"--simTime",str(totSimTime),"--seed",seed,"--noPlot"]

		if not resultFile: gt.run_subprocess(program)

		count+=1
		if count/nSim-percLastPrint>=printPeriod:
			percLastPrint=count/nSim
			print str(round(count/nSim*100))+"% of simulations performed..."



	""" create plots """
	errParams = dict(lw=0.5, capsize=1, capthick=0.5)
	with open(gaitCyclesFileName, 'r') as pickle_file:
		heelStrikes = pickle.load(pickle_file)
		footOffs = pickle.load(pickle_file)


	# Figure 5 plot all gait cycles- afferent and efferents
	#if not phasicStim:
	figName = time.strftime("/%Y_%m_%d_Tonic_FFS_species_"+toAddname+inputFileName+species+"_muscles_"+"".join(muscles)+"_delay_"+str(delay)+"_amp_"+str(eesAmplitudeName)+"_firingRates.pdf")
	#else: figName = time.strftime("/%Y_%m_%d_Phasic_FFS_species_"+toAddname+inputFileName+species+"_muscles_"+"".join(muscles)+"_delay_"+str(delay)+"_amp_"+str(eesAmplitudeName)+"_firingRates.pdf")
	fig, ax = plt.subplots(2, 4,figsize=(16,9))
	cmap = plt.get_cmap('winter')
	colors = cmap(np.linspace(0.1,0.9,len(eesFrequencies)))

	for i,eesFrequency in enumerate(eesFrequencies):
		#if not phasicStim:
		name = "FS_EES_230uA_"+str(eesFrequency)+"Hz_Delay_2ms_Tonic_FFS_Control_freq_"+str(eesFrequency)
		#name = "Tonic_FFS_species_"+toAddname+inputFileName+species+"_muscles_"+"".join(muscles)+"_delay_"+str(delay)+"_amp_"+str(eesAmplitudeName)+"_freq_"+str(eesFrequency)
		#else: name = "Phasic_"+emgVsKinMod+"_FFS_species_"+toAddname+inputFileName+species+"_muscles_"+"".join(muscles)+"_delay_"+str(delay)+"_amp_"+str(eesAmplitudeName)+"_freq_"+str(eesFrequency)
		if species == "human":name += hp.get_dataset()

		# get data
		print name
		resultFile = gt.find("*"+name+".p",pathToResults)
		print resultFile
		if len(resultFile)>1: print "Warning: multiple result files found!!!"
		with open(resultFile[0], 'r') as pickle_file:
			estimatedEmg = pickle.load(pickle_file)
			meanFr = pickle.load(pickle_file)

		# get gait cycles
		if not 'heelStrikeSamples' in locals():
			nSamples = len(meanFr[muscles[0]]["Mn"])
			dtMeanFr = float(totSimTime)/nSamples
			heelStrikeSamples = [int(x) for x in heelStrikes*1000./dtMeanFr]
			footOffSamples = [int(x) for x in footOffs*1000./dtMeanFr]
			samples = range(nSamples)
			stance = np.zeros(nSamples).astype(bool)
			for strike,off in zip(heelStrikeSamples,footOffSamples):
				if strike>nSamples: break
				stance[strike:off]=True

		for j,muscle in enumerate(muscles):
			ax[j,0].plot(meanFr[muscle]['Iaf'],color=colors[i])
			ax[j,0].fill_between(samples, 0, 200, where=stance, facecolor='#b0abab', alpha=0.25)
			ax[j,1].plot(meanFr[muscle]['IaInt'],color=colors[i])
			ax[j,1].fill_between(samples, 0, 200, where=stance, facecolor='#b0abab', alpha=0.25)
			ax[j,2].plot(meanFr[muscle]['Mn'],color=colors[i])
			ax[j,2].fill_between(samples, 0, 200, where=stance, facecolor='#b0abab', alpha=0.25)
			ax[j,3].plot(estimatedEmg[muscle]['Mn'],color=colors[i])
			ax[j,3].fill_between(samples, 0, 200, where=stance, facecolor='#b0abab', alpha=0.25)


	for j,muscle in enumerate(muscles):
		ax[j,0].set_ylim([0,200])
		ax[j,0].set_title("Ia fibers firing rate - "+muscle)
		ax[j,0].set_xlabel("Time (ms)")
		ax[j,0].set_ylabel("Firing rate (Imp/s)")
		ax[j,1].set_ylim([0,200])
		ax[j,1].set_title("IaInt firing rate - "+muscle)
		ax[j,1].set_xlabel("Time (ms)")
		ax[j,1].set_ylabel("Firing rate (Imp/s)")
		ax[j,2].set_ylim([0,200])
		ax[j,2].set_title("Mn firing rate - "+muscle)
		ax[j,2].set_xlabel("Time (ms)")
		ax[j,2].set_ylabel("Firing rate (Imp/s)")
		ax[j,3].set_ylim([0,200])
		ax[j,3].set_title("EMG - "+muscle)
		ax[j,3].set_xlabel("Time (ms)")
		ax[j,3].set_ylabel("Emg amplitude (a.u.)")
	plt.savefig(pathToResults+figName, format="pdf",transparent=True)


# FIgure 5 plot 2 single gait cycles- afferent and efferents + mn phasicity score
	if species == "rat":
		startGaitCycleN = 3
		nCycles = 1
	elif species == "human":
		startGaitCycleN = 3
		nCycles = 1

	figName = time.strftime("/%Y_%m_%d_Tonic_FFS_species_"+toAddname+inputFileName+species+"_muscles_"+"".join(muscles)+"_delay_"+str(delay)+"_amp_"+str(eesAmplitudeName)+"_single_firingRates.pdf")
	#else: figName = time.strftime("/%Y_%m_%d_Phasic_FFS_species_"+toAddname+inputFileName+species+"_muscles_"+"".join(muscles)+"_delay_"+str(delay)+"_amp_"+str(eesAmplitudeName)+"_single_firingRates.pdf")
	fig, ax = plt.subplots(2, 6,figsize=(16,9))
	cmap = plt.get_cmap('winter')
	colors = cmap(np.linspace(0.1,0.9,len(eesFrequencies)))
	bar_width = 5

	for i,eesFrequency in enumerate(eesFrequencies):
		#if not phasicStim:

		name = "FS_EES_230uA_"+str(eesFrequency)+"Hz_Delay_2ms_Tonic_FFS_Control_freq_"+str(eesFrequency)		#else: name = "Phasic_"+emgVsKinMod+"_FFS_species_"+toAddname+inputFileName+species+"_muscles_"+"".join(muscles)+"_delay_"+str(delay)+"_amp_"+str(eesAmplitudeName)+"_freq_"+str(eesFrequency)
		if species == "human":name += hp.get_dataset()

		# get data
		resultFile = gt.find("*"+name+".p",pathToResults)
		if len(resultFile)>1: print "Warning: multiple result files found!!!"
		with open(resultFile[0], 'r') as pickle_file:
			estimatedEmg = pickle.load(pickle_file)
			meanFr = pickle.load(pickle_file)

		# compute stats
		iaIntModDepth = {}
		activeMnFr={}
		for muscle in muscles:
			iaIntModDepth[muscle]=[]
			activeMnFr[muscle]=[]
		for j in xrange(len(heelStrikeSamples)-1):
			if heelStrikeSamples[j+1]>nSamples-50: break
			if heelStrikeSamples[j]<50:continue # to skip artefacts
			for muscle in muscles:
				iaIntModDepth[muscle].append(\
					meanFr[muscle]['IaInt'][heelStrikeSamples[j]:heelStrikeSamples[j+1]].max()-meanFr[muscle]['IaInt'][heelStrikeSamples[j]:heelStrikeSamples[j+1]].min())
				mnActivityDuringCycle = meanFr[muscle]['Mn'][heelStrikeSamples[j]:heelStrikeSamples[j+1]]
				activeMnFr[muscle].append(\
					mnActivityDuringCycle[mnActivityDuringCycle>=0.8*mnActivityDuringCycle.max()].mean())
					# mnActivityDuringCycle[mnActivityDuringCycle>=1.5*mnActivityDuringCycle.std()].mean())
					# mnActivityDuringCycle[mnActivityDuringCycle>=np.percentile(mnActivityDuringCycle,90)].mean())
		iaIntModDepthStats = {}
		activeMnFrStats = {}
		for muscle in muscles:
			iaIntModDepthStats[muscle] = {"mean":np.mean(iaIntModDepth[muscle]),
				"sem":np.std(iaIntModDepth[muscle])/(np.sqrt(len(iaIntModDepth[muscle])-1))}
			activeMnFrStats[muscle] = {"mean":np.mean(activeMnFr[muscle]),
				"sem":np.std(activeMnFr[muscle])/(np.sqrt(len(activeMnFr[muscle])-1))}

		# get gait cycles to plot
		if not 'startPlot' in locals():
			startPlot = heelStrikeSamples[startGaitCycleN-1]
			stopPlot = heelStrikeSamples[startGaitCycleN+nCycles-1]
			if stopPlot>nSamples: stopPlot=nSamples
			reducedSamples = range(stopPlot-startPlot)
			reducedStance = stance[startPlot:stopPlot]

		for j,muscle in enumerate(muscles):
			ax[j,0].plot(meanFr[muscle]['Iaf'][startPlot:stopPlot],color=colors[i])
			ax[j,0].fill_between(reducedSamples, 0, 200, where=reducedStance, facecolor='#b0abab', alpha=0.25)
			ax[j,1].plot(meanFr[muscle]['IaInt'][startPlot:stopPlot],color=colors[i])
			ax[j,1].fill_between(reducedSamples, 0, 250, where=reducedStance, facecolor='#b0abab', alpha=0.25)
			ax[j,2].bar(eesFrequency,iaIntModDepthStats[muscle]["mean"],bar_width,yerr=iaIntModDepthStats[muscle]["sem"],\
				color=colors[i],error_kw=errParams)
			xValsScatter = np.linspace(0,bar_width*0.9,len(iaIntModDepth[muscle]))+eesFrequency-bar_width*0.45
			ax[j,2].scatter(xValsScatter,iaIntModDepth[muscle], marker='o',edgecolor='black', linewidth='0.1', color="#dddde3", s=7, zorder=3, alpha=0.7)

			ax[j,3].plot(meanFr[muscle]['Mn'][startPlot:stopPlot],color=colors[i])
			ax[j,3].fill_between(reducedSamples, 0, 40, where=reducedStance, facecolor='#b0abab', alpha=0.25)
			ax[j,4].bar(eesFrequency,activeMnFrStats[muscle]["mean"],bar_width,yerr=activeMnFrStats[muscle]["sem"],\
				color=colors[i],error_kw=errParams)
			ax[j,4].scatter(xValsScatter,activeMnFr[muscle], marker='o',edgecolor='black', linewidth='0.1', color="#dddde3", s=7, zorder=3, alpha=0.7)
			ax[j,5].plot(estimatedEmg[muscle]['Mn'][startPlot:stopPlot],color=colors[i])
			ax[j,5].fill_between(reducedSamples, -50, 50, where=reducedStance, facecolor='#b0abab', alpha=0.25)

	for j,muscle in enumerate(muscles):
		ax[j,0].set_ylim([0,200])
		ax[j,0].set_title("Ia fibers firing rate - "+muscle)
		ax[j,0].set_xlabel("Time (ms)")
		ax[j,0].set_ylabel("Firing rate (Imp/s)")
		ax[j,1].set_ylim([0,250])
		ax[j,1].set_title("IaInt firing rate - "+muscle)
		ax[j,1].set_xlabel("Time (ms)")
		ax[j,1].set_ylabel("Firing rate (Imp/s)")
		ax[j,2].set_ylim([0,250])
		ax[j,2].set_title("Mean IaInr Fr while active")
		ax[j,2].set_xlabel("Stimulation amplitude (uA)")
		ax[j,2].set_ylabel("Firing rate (Imp/s)")
		ax[j,3].set_ylim([0,40])
		ax[j,3].set_title("Mn firing rate - "+muscle)
		ax[j,3].set_xlabel("Time (ms)")
		ax[j,3].set_ylabel("Firing rate (Imp/s)")
		ax[j,4].set_ylim([0,40])
		ax[j,4].set_title("Mean Mn Fr while active")
		ax[j,4].set_xlabel("Stimulation amplitude (uA)")
		ax[j,4].set_ylabel("Firing rate (Imp/s)")
		ax[j,5].set_ylim([-50,50])
		ax[j,5].set_title("EMG - "+muscle)
		ax[j,5].set_xlabel("Time (ms)")
		ax[j,5].set_ylabel("Emg amplitude (a.u.)")
	plt.savefig(pathToResults+figName, format="pdf",transparent=True)





	# FIgure 2-7 plot
	if species == "rat":
		startGaitCycleN = 3
		nCycles = 1
	elif species == "human":
		startGaitCycleN = 3
		nCycles = 1

	#if not phasicStim:
	figName = time.strftime("/%Y_%m_%d_Tonic_FFS_species_"+toAddname+inputFileName+species+"_muscles_"+"".join(muscles)+"_delay_"+str(delay)+"_amp_"+str(eesAmplitudeName)+"_afferentStats.pdf")
	#else: figName = time.strftime("/%Y_%m_%d_Phasic_FFS_species_"+toAddname+inputFileName+species+"_muscles_"+"".join(muscles)+"_delay_"+str(delay)+"_amp_"+str(eesAmplitudeName)+"_afferentStats.pdf")
	fig, ax = plt.subplots(2, 4,figsize=(16,9))
	cmap = plt.get_cmap('winter')
	colors = cmap(np.linspace(0.1,0.9,len(eesFrequencies)))
	bar_width = 5

	meanPerEraserApIaf = []
	offsetMeanFr = 0
	offsetMeanModDepth = 0

	for i,eesFrequency in enumerate(eesFrequencies):
		#if not phasicStim:
		name = "FS_EES_230uA_"+str(eesFrequency)+"Hz_Delay_2ms_Tonic_FFS_Control_freq_"+str(eesFrequency)
		#name = "Tonic_FFS_species_"+toAddname+inputFileName+species+"_muscles_"+"".join(muscles)+"_delay_"+str(delay)+"_amp_"+str(eesAmplitudeName)+"_freq_"+str(eesFrequency)
		#else: name = "Phasic_"+emgVsKinMod+"_FFS_species_"+toAddname+inputFileName+species+"_muscles_"+"".join(muscles)+"_delay_"+str(delay)+"_amp_"+str(eesAmplitudeName)+"_freq_"+str(eesFrequency)
		if species == "human":name += hp.get_dataset()

		resultFile = gt.find("*"+name+".p",pathToResults)
		if len(resultFile)>1: print "Warning: multiple result files found!!!"
		with open(resultFile[0], 'r') as pickle_file:
			estimatedEmg = pickle.load(pickle_file)
			meanFr = pickle.load(pickle_file)
			meanPerEraserApIaf.append(pickle.load(pickle_file))

		# compute stats
		iaModDepth = {}
		iaMeanFr={}
		for muscle in muscles:
			iaModDepth[muscle]=[]
			iaMeanFr[muscle]=[]
		for j in xrange(len(heelStrikeSamples)-1):
			if heelStrikeSamples[j+1]>nSamples-50: break
			if heelStrikeSamples[j]<50:continue # to skip artefacts
			for muscle in muscles:
				iaModDepth[muscle].append(\
					meanFr[muscle]['Iaf'][heelStrikeSamples[j]:heelStrikeSamples[j+1]].max()-meanFr[muscle]['Iaf'][heelStrikeSamples[j]:heelStrikeSamples[j+1]].min())
				iaMeanFr[muscle].append(\
					meanFr[muscle]['Iaf'][heelStrikeSamples[j]:heelStrikeSamples[j+1]].mean())
		iaModDepthStats = {}
		iaMeanFrStats = {}
		for muscle in muscles:
			iaModDepthStats[muscle] = {"mean":np.mean(iaModDepth[muscle]),
				"sem":np.std(iaModDepth[muscle])/(np.sqrt(len(iaModDepth[muscle])-1))}
			iaMeanFrStats[muscle] = {"mean":np.mean(iaMeanFr[muscle]),
				"sem":np.std(iaMeanFr[muscle])/(np.sqrt(len(iaMeanFr[muscle])-1))}

		# get gait cycles to plot
		if not 'startPlot' in locals():
			startPlot = heelStrikeSamples[startGaitCycleN-1]
			stopPlot = heelStrikeSamples[startGaitCycleN+nCycles-1]
			if stopPlot>nSamples: stopPlot=nSamples
			reducedSamples = range(stopPlot-startPlot)
			reducedStance = stance[startPlot:stopPlot]

		for j,muscle in enumerate(muscles):

			ax[j,0].plot(meanFr[muscle]['Iaf'][startPlot:stopPlot],color=colors[i])
			ax[j,0].fill_between(reducedSamples, 0, 125, where=reducedStance, facecolor='#b0abab', alpha=0.25)
			ax[j,1].bar(eesFrequency,iaMeanFrStats[muscle]["mean"],bar_width,yerr=iaMeanFrStats[muscle]["sem"],\
				color=colors[i],error_kw=errParams)
			xValsScatter = np.linspace(0,bar_width*0.9,len(iaMeanFr[muscle]))+eesFrequency-bar_width*0.45
			ax[j,1].scatter(xValsScatter,iaMeanFr[muscle], marker='o',edgecolor='black', linewidth='0.1', color="#dddde3", s=7, zorder=3, alpha=0.7)

			ax[j,2].bar(eesFrequency,iaModDepthStats[muscle]["mean"],bar_width,yerr=iaModDepthStats[muscle]["sem"],\
				color=colors[i],error_kw=errParams)
			ax[j,2].scatter(xValsScatter,iaModDepth[muscle], marker='o',edgecolor='black', linewidth='0.1', color="#dddde3", s=7, zorder=3, alpha=0.7)
			ax[j,3].bar(eesFrequency,meanPerEraserApIaf[-1],5,color=colors[i])

			ax[j,0].set_ylim([0,125])
			ax[j,0].set_title("Ia fibers firing rate - "+muscle)
			ax[j,0].set_xlabel("Time (ms)")
			ax[j,0].set_ylabel("Firing rate (Imp/s)")
			ax[j,1].set_ylim([0,125])
			ax[j,1].set_title("Mean Ia firing rate ")
			ax[j,1].set_xlabel("Stimulation amplitude (uA)")
			ax[j,1].set_ylabel("(imp/s)")
			ax[j,2].set_ylim([0,80])
			ax[j,2].set_title("modulation depth")
			ax[j,2].set_xlabel("Stimulation amplitude (uA)")
			ax[j,2].set_ylabel("(imp/s)")
			ax[j,3].set_ylim([0,100])
			ax[j,3].set_title("Percentage erased APs")
			ax[j,3].set_xlabel("Stimulation frequency (Hz)")
			ax[j,3].set_ylabel("Percentage")
	plt.savefig(pathToResults+figName, format="pdf",transparent=True)




if __name__ == '__main__':
	main()
