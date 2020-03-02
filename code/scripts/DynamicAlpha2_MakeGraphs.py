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
	Amplitudes = ['230','260','290']
	Conditions = ['No EES','EES','EES+A08','EES+A08+ProIncrease']

	#eesAmplitude = "230"
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

	tls.modify_network_structure(templateFile,templateFile,delay,[w1,w2])

	eesFrequencies = range(0,41,40)
	nProc = 4
	seed = "1"

	nSim = len(eesFrequencies)
	count=0.
	percLastPrint=0.
	printPeriod = 0.05


	""" create plots """
	errParams = dict(lw=0.5, capsize=1, capthick=0.5)
	with open(gaitCyclesFileName, 'r') as pickle_file:
		heelStrikes = pickle.load(pickle_file)
		footOffs = pickle.load(pickle_file)


	# Figure 5 plot all gait cycles- afferent and efferents
	#if not phasicStim:
	figName = "Complete_Plot.pdf"
	#else: figName = time.strftime("/%Y_%m_%d_Phasic_FFS_species_"+toAddname+inputFileName+species+"_muscles_"+"".join(muscles)+"_delay_"+str(delay)+"_amp_"+str(eesAmplitudeName)+"_firingRates.pdf")
	fig, ax = plt.subplots(2, 4,figsize=(16,9))
	cmap = plt.get_cmap('winter')
	colors = cmap(np.linspace(0.1,0.9,len(eesFrequencies)))

	Conditions = ['2019_07_22_FS_EES_230uA_0Hz_Delay_2ms_Tonic_FFS_Control_freq_0.p','2019_07_22_FS_EES_230uA_100Hz_Delay_2ms_Tonic_FFS_Control_freq_100.p','2019_07_22_FS_EES_230uA_100Hz_Delay_2ms_Tonic_FFS_EES_A08_freq_100.p','2019_07_22_FS_EES_230uA_100Hz_Delay_2ms_Tonic_FFS_EES_A08_ProIncrease_freq_100.p']
	CondNames = ['No EES','EES','EES A08','EES A08 Pro Increase']

	#Conditions = ['2019_07_22_FS_EES_230uA_40Hz_Delay_2ms_Tonic_FFS_EES_A08_freq_40.p','2019_07_22_FS_EES_230uA_40Hz_Delay_2ms_Tonic_FFS_EES_A08_ProIncrease_freq_40.p']

# FIgure 5 plot 2 single gait cycles- afferent and efferents + mn phasicity score
	if species == "rat":
		startGaitCycleN = 3
		nCycles = 1
	elif species == "human":
		startGaitCycleN = 3
		nCycles = 1

	fig, ax = plt.subplots(2, 12,figsize=(36,9))
	cmap = plt.get_cmap('winter')
	colors = cmap(np.linspace(0.1,0.9,len(Conditions)))
	bar_width = 5
	cell_List = ['Iaf','IaInt','II_RAf_foot','II_RAf','II_SAIf_foot','II_SAIf','IIExInt','RORa','RORaInt','IIf']
	for i,condition in enumerate(Conditions):
		#if not phasicStim:

		name = condition
		resultFile = gt.find(name,pathToResults)
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
		ax[0,11].legend(CondNames)


	for j,muscle in enumerate(muscles):
		ax[j,0].set_ylim([0,120])
		ax[j,0].set_title("Ia fibers firing rate - "+muscle)
		ax[j,0].set_xlabel("Time (ms)")
		ax[j,0].set_ylabel("Firing rate (Imp/s)")
		ax[j,1].set_ylim([0,220])
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




if __name__ == '__main__':
	main()
