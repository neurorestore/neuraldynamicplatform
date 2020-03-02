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
	eesAmplitude = "200" #235
	eesFrequency = "40" #40
	delay = 2
	initAmplitude = "0.1" #0.8
	maxAmplitude = "2.0" #1.6
	nStimSteps = "20" #5
	nRepetitions = "1" #5

	count=0.
	percLastPrint=0.
	printPeriod = 0.01

	resultName = "AutoMonoInh"

	# Static reflex Monosynapic Excitatory
	inputFile = "AutoDiInh.txt"
	program = ['python','./scripts/runBatchOfStaticReflexRecordings.py',\
		initAmplitude,maxAmplitude,nStimSteps,nRepetitions,inputFile,resultName]
	print " ".join(program)
	gt.run_subprocess(program)



if __name__ == '__main__':
	main()
