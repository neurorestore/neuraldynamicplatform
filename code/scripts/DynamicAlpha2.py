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
	Conditions = ['Control','EES_A08','EES_A08_ProIncrease']



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

	eesFrequencies = range(0,101,100)
	nProc = 4
	seed = "1"

	nSim = len(eesFrequencies)
	count=0.
	percLastPrint=0.
	printPeriod = 0.05

	# run simulations
	for j,eesAmplitude in enumerate(Amplitudes):
		for i,eesFrequency in enumerate(eesFrequencies):
			for condition in Conditions:
				#name = "Tonic_FFS_"+inputFileName+"_freq_"+str(eesFrequency)
				inputFileName = condition
				inputFile = "generatedStructures/"+inputFileName+".txt"
				name = "Tonic_FFS_"+condition+"_freq_"+str(eesFrequency)
				resultFile = gt.find("*"+name+".p",pathToResults)
				if not resultFile:
					program = ['python','./scripts/runForSimMuscleSpindles_RORa.py',\
						str(eesFrequency),eesAmplitude,inputFile,name,"--simTime",str(totSimTime),"--seed",seed,"--noPlot"]

				if not resultFile: gt.run_subprocess(program)

				count+=1
				if count/nSim-percLastPrint>=printPeriod:
					percLastPrint=count/nSim
					print str(round(count/nSim*100))+"% of simulations performed..."





if __name__ == '__main__':
	main()
