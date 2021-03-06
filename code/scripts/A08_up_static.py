import sys
sys.path.append('../code')
import subprocess
from tools import structures_tools as tls
from tools import general_tools as gt
import numpy as np

pathToResults = "../../results"

def main():
	""" This program launches a parameters systematic search for a ForSimRORa.
	The different parameters that are changed over time are directly defined in the main function.
	The program doesn't have to be executed by MPI.
	"""
	nProc = 4
	seed = "1"
	name = "_SS_RORa_"
	simTime = 500
	eesAmplitude = "235" #235
	eesFrequency = "40" #40
	delay = 2
	initAmplitude = "0.8" #0.8
	maxAmplitude = "1.6" #1.6
	nStimSteps = "5" #5
	nRepetitions = "1" #5

	weights_1 = np.round(np.linspace(0.011,0.011,1),3)
	weights_2 = np.round(np.linspace(0.005,0.005,1),3)

	nSim = len(weights_1)*len(weights_2)
	count=0.
	percLastPrint=0.
	printPeriod = 0.01

	for w1 in weights_1:
		for w2 in weights_2:
			resultName = name+"w1_"+str(w1)+"_w2_"+str(w2)

			# Static reflex recordings simulatiom Control
			resultFile = gt.find("*"+resultName+"_sr_A08"+"*.p",pathToResults)
			if not resultFile:
				inputFile = "generatedStructures/ForSimRoRa_w1_"+str(w1)+"_w2_"+str(w2)+".txt"
				tls.modify_network_structure("A08_2.txt",inputFile,delay,[w1,w2])
				program = ['python','./scripts/runBatchOfStaticReflexRecordings.py',\
					initAmplitude,maxAmplitude,nStimSteps,nRepetitions,inputFile,resultName+"_sr_A08_up"]
				print " ".join(program)
				gt.run_subprocess(program)

			count+=1
			if count/nSim-percLastPrint>=printPeriod:
				percLastPrint=count/nSim
				print str(round(count/nSim*100))+"% of simulations performed..."


if __name__ == '__main__':
	main()
