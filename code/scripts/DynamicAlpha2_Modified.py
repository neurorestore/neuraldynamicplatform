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
	templateFile = "templateFrwSimRORaReal.txt"
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
		name = "FS_EES_230uA_"+str(eesFrequency)+"Hz_Delay_2ms_Tonic_FFS_"+inputFileName+"_freq_"+str(eesFrequency)
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
	figName2 = time.strftime("/%Y_%m_%d_Tonic_FFS_species_"+toAddname+inputFileName+species+"_muscles_"+"".join(muscles)+"_delay_"+str(delay)+"_amp_"+str(eesAmplitudeName)+"_single_firingRates_ModDepth.pdf")
	#else: figName = time.strftime("/%Y_%m_%d_Phasic_FFS_species_"+toAddname+inputFileName+species+"_muscles_"+"".join(muscles)+"_delay_"+str(delay)+"_amp_"+str(eesAmplitudeName)+"_single_firingRates.pdf")
	# fig, ax for firing rate
	fig, ax = plt.subplots(2, 12,figsize=(36,9))
	cmap = plt.get_cmap('winter')
	colors = cmap(np.linspace(0.1,0.9,len(eesFrequencies)))
	bar_width = 5
	cell_List = ['Iaf','IaInt','II_RAf_foot','II_RAf','II_SAIf_foot','II_SAIf','IIExInt','RORa','RORaInt','IIf']
	for i,eesFrequency in enumerate(eesFrequencies):
		#if not phasicStim:

		name = "FS_EES_230uA_"+str(eesFrequency)+"Hz_Delay_2ms_Tonic_FFS_"+inputFileName+"_freq_"+str(eesFrequency)		#else: name = "Phasic_"+emgVsKinMod+"_FFS_species_"+toAddname+inputFileName+species+"_muscles_"+"".join(muscles)+"_delay_"+str(delay)+"_amp_"+str(eesAmplitudeName)+"_freq_"+str(eesFrequency)
		if species == "human":name += hp.get_dataset()

		# get data
		resultFile = gt.find("*"+name+".p",pathToResults)
		if len(resultFile)>1: print "Warning: multiple result files found!!!"
		with open(resultFile[0], 'r') as pickle_file:
			estimatedEmg = pickle.load(pickle_file)
			meanFr = pickle.load(pickle_file)

		# compute stats
		iaIntModDepth = {}
		cellModDepth = {}
		activeMnFr={}
		for muscle in muscles:
			iaIntModDepth[muscle]=[]
			cellModDepth[muscle]={}
			activeMnFr[muscle]=[]
			for cell_type in cell_List:
				cellModDepth[muscle][cell_type] = []
		for j in xrange(len(heelStrikeSamples)-1):
			if heelStrikeSamples[j+1]>nSamples-50: break
			if heelStrikeSamples[j]<50:continue # to skip artefacts
			for muscle in muscles:
				for cell_type in cell_List:
					cellModDepth[muscle][cell_type].append(\
						meanFr[muscle][cell_type][heelStrikeSamples[j]:heelStrikeSamples[j+1]].max()-meanFr[muscle][cell_type][heelStrikeSamples[j]:heelStrikeSamples[j+1]].min())
				iaIntModDepth[muscle].append(\
					meanFr[muscle]['IaInt'][heelStrikeSamples[j]:heelStrikeSamples[j+1]].max()-meanFr[muscle]['IaInt'][heelStrikeSamples[j]:heelStrikeSamples[j+1]].min())
				mnActivityDuringCycle = meanFr[muscle]['Mn'][heelStrikeSamples[j]:heelStrikeSamples[j+1]]
				activeMnFr[muscle].append(\
					mnActivityDuringCycle[mnActivityDuringCycle>=0.8*mnActivityDuringCycle.max()].mean())
					# mnActivityDuringCycle[mnActivityDuringCycle>=1.5*mnActivityDuringCycle.std()].mean())
					# mnActivityDuringCycle[mnActivityDuringCycle>=np.percentile(mnActivityDuringCycle,90)].mean())
		iaIntModDepthStats = {}
		cellModDepthStats = {}
		activeMnFrStats = {}
		for muscle in muscles:
			cellModDepthStats[muscle] = {}
			for cell_type in cell_List:
				cellModDepthStats[muscle][cell_type] = {"mean":np.mean(cellModDepth[muscle][cell_type]),
					"sem":np.std(cellModDepth[muscle][cell_type])/(np.sqrt(len(cellModDepth[muscle][cell_type])-1))}
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
			ax[j,2].plot(meanFr[muscle]['II_RAf_foot'][startPlot:stopPlot],color=colors[i])
			ax[j,2].fill_between(reducedSamples, 0, 200, where=reducedStance, facecolor='#b0abab', alpha=0.25)
			ax[j,3].plot(meanFr[muscle]['II_RAf'][startPlot:stopPlot],color=colors[i])
			ax[j,3].fill_between(reducedSamples, 0, 200, where=reducedStance, facecolor='#b0abab', alpha=0.25)
			ax[j,4].plot(meanFr[muscle]['II_SAIf_foot'][startPlot:stopPlot],color=colors[i])
			ax[j,4].fill_between(reducedSamples, 0, 200, where=reducedStance, facecolor='#b0abab', alpha=0.25)
			ax[j,5].plot(meanFr[muscle]['II_SAIf'][startPlot:stopPlot],color=colors[i])
			ax[j,5].fill_between(reducedSamples, 0, 200, where=reducedStance, facecolor='#b0abab', alpha=0.25)
			ax[j,6].plot(meanFr[muscle]['IIExInt'][startPlot:stopPlot],color=colors[i])
			ax[j,6].fill_between(reducedSamples, 0, 200, where=reducedStance, facecolor='#b0abab', alpha=0.25)
			ax[j,7].plot(meanFr[muscle]['RORa'][startPlot:stopPlot],color=colors[i])
			ax[j,7].fill_between(reducedSamples, 0, 600, where=reducedStance, facecolor='#b0abab', alpha=0.25)
			ax[j,8].plot(meanFr[muscle]['RORaInt'][startPlot:stopPlot],color=colors[i])
			ax[j,8].fill_between(reducedSamples, 0, 600, where=reducedStance, facecolor='#b0abab', alpha=0.25)
			ax[j,9].plot(meanFr[muscle]['IIf'][startPlot:stopPlot],color=colors[i])
			ax[j,9].fill_between(reducedSamples, 0, 200, where=reducedStance, facecolor='#b0abab', alpha=0.25)
			ax[j,10].plot(meanFr[muscle]['Mn'][startPlot:stopPlot],color=colors[i])
			ax[j,10].fill_between(reducedSamples, 0, 60, where=reducedStance, facecolor='#b0abab', alpha=0.25)
			ax[j,11].plot(estimatedEmg[muscle]['Mn'][startPlot:stopPlot],color=colors[i])
			ax[j,11].fill_between(reducedSamples, -150, 150, where=reducedStance, facecolor='#b0abab', alpha=0.25)



	for j,muscle in enumerate(muscles):
		ax[j,0].set_ylim([0,120])
		ax[j,0].set_title("Ia fibers firing rate - "+muscle)
		ax[j,0].set_xlabel("Time (ms)")
		ax[j,0].set_ylabel("Firing rate (Imp/s)")
		ax[j,1].set_ylim([0,200])
		ax[j,1].set_title("IaInt firing rate - "+muscle)
		ax[j,1].set_xlabel("Time (ms)")
		ax[j,1].set_ylabel("Firing rate (Imp/s)")
		ax[j,2].set_ylim([0,100])
		ax[j,2].set_title("II_RAf_foot firing rate - "+muscle)
		ax[j,2].set_xlabel("Time (ms)")
		ax[j,2].set_ylabel("Firing rate (Imp/s)")
		ax[j,3].set_ylim([0,100])
		ax[j,3].set_title("II_RAf firing rate - "+muscle)
		ax[j,3].set_xlabel("Time (ms)")
		ax[j,3].set_ylabel("Firing rate (Imp/s)")
		ax[j,4].set_ylim([0,200])
		ax[j,4].set_title("II_SAIf_foot firing rate - "+muscle)
		ax[j,4].set_xlabel("Time (ms)")
		ax[j,4].set_ylabel("Firing rate (Imp/s)")
		ax[j,5].set_ylim([0,200])
		ax[j,5].set_title("II_SAIf firing rate - "+muscle)
		ax[j,5].set_xlabel("Time (ms)")
		ax[j,5].set_ylabel("Firing rate (Imp/s)")
		ax[j,6].set_ylim([0,100])
		ax[j,6].set_title("IIExInt firing rate - "+muscle)
		ax[j,6].set_xlabel("Time (ms)")
		ax[j,6].set_ylabel("Firing rate (Imp/s)")
		ax[j,7].set_ylim([0,200])
		ax[j,7].set_title("RORa firing rate - "+muscle)
		ax[j,7].set_xlabel("Time (ms)")
		ax[j,7].set_ylabel("Firing rate (Imp/s)")
		ax[j,8].set_ylim([0,500])
		ax[j,8].set_title("RORaInt firing rate - "+muscle)
		ax[j,8].set_xlabel("Time (ms)")
		ax[j,8].set_ylabel("Firing rate (Imp/s)")
		ax[j,9].set_ylim([0,140])
		ax[j,9].set_title("II fibers firing rate - "+muscle)
		ax[j,9].set_xlabel("Time (ms)")
		ax[j,9].set_ylabel("Firing rate (Imp/s)")
		ax[j,10].set_ylim([0,50])
		ax[j,10].set_title("Mn firing rate - "+muscle)
		ax[j,10].set_xlabel("Time (ms)")
		ax[j,10].set_ylabel("Firing rate (Imp/s)")
		ax[j,11].set_ylim([-80,80])
		ax[j,11].set_title("EMG - "+muscle)
		ax[j,11].set_xlabel("Time (ms)")
		ax[j,11].set_ylabel("Emg amplitude (a.u.)")
	plt.savefig(pathToResults+figName, format="pdf",transparent=True)
	# fig2, ax2 for modulation depth
	fig2, ax2 = plt.subplots(2, 12,figsize=(36,9))
	for i,eesFrequency in enumerate(eesFrequencies):
		for j,muscle in enumerate(muscles):
			for cell_idx, cell_val in enumerate(cell_List):
				ax2[j,cell_idx].bar(eesFrequency,cellModDepthStats[muscle][cell_val]["mean"],bar_width,yerr=cellModDepthStats[muscle][cell_val]["sem"],\
					color=colors[i],error_kw=errParams)
				xValsScatter = np.linspace(0,bar_width*0.9,len(cellModDepth[muscle][cell_val]))+eesFrequency-bar_width*0.45
				ax2[j,cell_idx].scatter(xValsScatter,cellModDepth[muscle][cell_val], marker='o',edgecolor='black', linewidth='0.1', color="#dddde3", s=7, zorder=3, alpha=0.7)
			ax2[j,len(cell_List)].bar(eesFrequency,activeMnFrStats[muscle]["mean"],bar_width,yerr=activeMnFrStats[muscle]["sem"],\
				color=colors[i],error_kw=errParams)
			ax2[j,len(cell_List)].scatter(xValsScatter,activeMnFr[muscle], marker='o',edgecolor='black', linewidth='0.1', color="#dddde3", s=7, zorder=3, alpha=0.7)

	for j,muscle in enumerate(muscles):
		ax2[j,0].set_ylim([0,120])
		ax2[j,0].set_title("Ia fibers firing rate - "+muscle)
		ax2[j,0].set_xlabel("Time (ms)")
		ax2[j,0].set_ylabel("Firing rate (Imp/s)")
		ax2[j,1].set_ylim([0,200])
		ax2[j,1].set_title("IaInt firing rate - "+muscle)
		ax2[j,1].set_xlabel("Time (ms)")
		ax2[j,1].set_ylabel("Firing rate (Imp/s)")
		ax2[j,2].set_ylim([0,100])
		ax2[j,2].set_title("II_RAf_foot firing rate - "+muscle)
		ax2[j,2].set_xlabel("Time (ms)")
		ax2[j,2].set_ylabel("Firing rate (Imp/s)")
		ax2[j,3].set_ylim([0,100])
		ax2[j,3].set_title("II_RAf firing rate - "+muscle)
		ax2[j,3].set_xlabel("Time (ms)")
		ax2[j,3].set_ylabel("Firing rate (Imp/s)")
		ax2[j,4].set_ylim([0,200])
		ax2[j,4].set_title("II_SAIf_foot firing rate - "+muscle)
		ax2[j,4].set_xlabel("Time (ms)")
		ax2[j,4].set_ylabel("Firing rate (Imp/s)")
		ax2[j,5].set_ylim([0,200])
		ax2[j,5].set_title("II_SAIf firing rate - "+muscle)
		ax2[j,5].set_xlabel("Time (ms)")
		ax2[j,5].set_ylabel("Firing rate (Imp/s)")
		ax2[j,6].set_ylim([0,100])
		ax2[j,6].set_title("IIExInt firing rate - "+muscle)
		ax2[j,6].set_xlabel("Time (ms)")
		ax2[j,6].set_ylabel("Firing rate (Imp/s)")
		ax2[j,7].set_ylim([0,200])
		ax2[j,7].set_title("RORa firing rate - "+muscle)
		ax2[j,7].set_xlabel("Time (ms)")
		ax2[j,7].set_ylabel("Firing rate (Imp/s)")
		ax2[j,8].set_ylim([0,500])
		ax2[j,8].set_title("RORaInt firing rate - "+muscle)
		ax2[j,8].set_xlabel("Time (ms)")
		ax2[j,8].set_ylabel("Firing rate (Imp/s)")
		ax2[j,9].set_ylim([0,140])
		ax2[j,9].set_title("II fibers firing rate - "+muscle)
		ax2[j,9].set_xlabel("Time (ms)")
		ax2[j,9].set_ylabel("Firing rate (Imp/s)")
		ax2[j,10].set_ylim([0,50])
		ax2[j,10].set_title("Mn firing rate - "+muscle)
		ax2[j,10].set_xlabel("Time (ms)")
		ax2[j,10].set_ylabel("Firing rate (Imp/s)")
		ax2[j,11].set_ylim([-80,80])
		ax2[j,11].set_title("EMG - "+muscle)
		ax2[j,11].set_xlabel("Time (ms)")
		ax2[j,11].set_ylabel("Emg amplitude (a.u.)")
	plt.savefig(pathToResults+figName2, format="pdf",transparent=True)



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
		name = "FS_EES_230uA_"+str(eesFrequency)+"Hz_Delay_2ms_Tonic_FFS_"+inputFileName+"_freq_"+str(eesFrequency)
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
