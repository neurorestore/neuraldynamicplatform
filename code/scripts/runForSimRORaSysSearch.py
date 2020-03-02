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

			# Forward simulatiom membrane potential
			#resultFile = gt.find("*"+resultName+"_fs_real"+"*.pdf",pathToResults)
			#if not resultFile:
			#	inputFile = "generatedStructures/ForSimRoRa_w1_"+str(w1)+"_w2_"+str(w2)+"_w3_"+str(w3)+".txt"
			#	tls.modify_network_structure("templateFrwSimRORaReal.txt",inputFile,delay,[w1,w2,w3])
			#	gt.run_subprocess(['mpiexec','-np',str(nProc),'python','./scripts/runForSimRORa_MemPot.py',\
			#		eesFrequency,eesAmplitude,inputFile,resultName+"_fs_real","--simTime",str(simTime),"--seed",seed])

			# Static reflex recordings simulatiom Control
			resultFile = gt.find("*"+resultName+"_sr_Control"+"*.p",pathToResults)
			if not resultFile:
				inputFile = "generatedStructures/ForSimRoRa_w1_"+str(w1)+"_w2_"+str(w2)+".txt"
				tls.modify_network_structure("Control.txt",inputFile,delay,[w1,w2])
				program = ['python','./scripts/runBatchOfStaticReflexRecordings.py',\
					initAmplitude,maxAmplitude,nStimSteps,nRepetitions,inputFile,resultName+"_sr_Control"]
				print " ".join(program)
				gt.run_subprocess(program)

			# Static reflex recordings simulatiom Control
			resultFile = gt.find("*"+resultName+"_sr_Control_No_Inhib"+"*.p",pathToResults)
			if not resultFile:
				inputFile = "generatedStructures/ForSimRoRa_w1_"+str(w1)+"_w2_"+str(w2)+".txt"
				tls.modify_network_structure("Control_NoInhib.txt",inputFile,delay,[w1,w2])
				program = ['python','./scripts/runBatchOfStaticReflexRecordings.py',\
					initAmplitude,maxAmplitude,nStimSteps,nRepetitions,inputFile,resultName+"_sr_Control_No_Inhib"]
				print " ".join(program)
				gt.run_subprocess(program)

			# Static reflex recordings simulatiom A08
			resultFile = gt.find("*"+resultName+"_sr_A08"+"*.p",pathToResults)
			if not resultFile:
				inputFile = "generatedStructures/ForSimRoRa_w1_"+str(w1)+"_w2_"+str(w2)+".txt"
				tls.modify_network_structure("A08.txt",inputFile,delay,[w1,w2])
				program = ['python','./scripts/runBatchOfStaticReflexRecordings.py',\
					initAmplitude,maxAmplitude,nStimSteps,nRepetitions,inputFile,resultName+"_sr_A08"]
				print " ".join(program)
				gt.run_subprocess(program)

			# Static reflex recordings simulatiom A08
			resultFile = gt.find("*"+resultName+"_sr_2aAgo"+"*.p",pathToResults)
			if not resultFile:
				inputFile = "generatedStructures/ForSimRoRa_w1_"+str(w1)+"_w2_"+str(w2)+".txt"
				tls.modify_network_structure("Ago.txt",inputFile,delay,[w1,w2])
				program = ['python','./scripts/runBatchOfStaticReflexRecordings.py',\
					initAmplitude,maxAmplitude,nStimSteps,nRepetitions,inputFile,resultName+"_sr_2aAgo"]
				print " ".join(program)
				gt.run_subprocess(program)

			# Static reflex recordings simulatiom A08
			resultFile = gt.find("*"+resultName+"_sr_2aAgo_NoInhib"+"*.p",pathToResults)
			if not resultFile:
				inputFile = "generatedStructures/ForSimRoRa_w1_"+str(w1)+"_w2_"+str(w2)+".txt"
				tls.modify_network_structure("Ago_NoInhib.txt",inputFile,delay,[w1,w2])
				program = ['python','./scripts/runBatchOfStaticReflexRecordings.py',\
				initAmplitude,maxAmplitude,nStimSteps,nRepetitions,inputFile,resultName+"_sr_2aAgo_NoInhib"]
				print " ".join(program)
				gt.run_subprocess(program)

			#a2aName = name+"_a2a_w1_"+str(w1)+"_w2_"+str(w2)+"_w3_"+str(w3)
			# Static reflex recordings simulatiom a2aAgo
			#resultFilea2a = gt.find("*"+a2aName+"_sr_real"+"*.p",pathToResults)
			#if not resultFilea2a:
			#	inputFile = "generatedStructures/ForSima2aAgo_w1_"+str(w1)+"_w2_"+str(w2)+"_w3_"+str(w3)+".txt"
			#	tls.modify_network_structure("templateFrwSima2aAgo.txt",inputFile,delay,[w1,w2,w3])
			#	program = ['python','./scripts/runBatchOfStaticReflexRecordings.py',\
			#		initAmplitude,maxAmplitude,nStimSteps,nRepetitions,inputFile,a2aName+"_sr_real"]
			#	gt.run_subprocess(program)

			# Forward simulatiom no 5ht


			#resultFilea2a = gt.find("*"+a2aName+"_sr_real"+"*.p",pathToResults)
			#if not resultFilea2a:
			#	inputFile = "generatedStructures/ForSimRoRa2aAgo_w1_"+str(w1)+"_w2_"+str(w2)+"_w3_"+str(w3)+".txt"
			#	tls.modify_network_structure("templateFrwSima2aAgo.txt",inputFile,delay,[w1,w2,w3])
			#	gt.run_subprocess(['mpiexec','-np',str(nProc),'python','./scripts/runForSimRORa_MemPot.py',\
			#		eesFrequency,eesAmplitude,inputFile,resultFilea2a+"_fs_real","--simTime",str(simTime),"--seed",seed])


			# Forward simulatiom 5ht
			#resultFile = gt.find("*"+resultName+"_fs_artificial_5HT"+"*.p",pathToResults)
			#if not resultFile:
			#	inputFile = "generatedStructures/ForSimRoRa_5HT_w1_"+str(w1)+"_w2_"+str(w2_1)+"_w3_"+str(w3)+"_w4_"+str(w2_2)+".txt"
			#	tls.modify_network_structure("templateFrwSimRORaReal_5HT.txt",inputFile,delay,[w1,w2_1,w3,w2_2])
			#	gt.run_subprocess(['mpiexec','-np',str(nProc),'python','./scripts/runForSimRORa.py',\
			#		eesFrequency,eesAmplitude,inputFile,resultName+"_fs_real_5HT","--simTime",str(simTime),"--seed",seed])

			# Static reflex recordings simulatiom 5ht
			#resultFile = gt.find("*"+resultName+"_sr_real_5HT"+"*.p",pathToResults)
			#if not resultFile:
			#	inputFile = "generatedStructures/ForSimRoRa_5HT_w1_"+str(w1)+"_w2_"+str(w2_1)+"_w3_"+str(w3)+"_w4_"+str(w2_2)+".txt"
			#	tls.modify_network_structure("templateFrwSimRORaReal_5HT.txt",inputFile,delay,[w1,w2_1,w3,w2_2])
			#	gt.run_subprocess(['python','./scripts/runBatchOfStaticReflexRecordings.py',\
			#		initAmplitude,maxAmplitude,nStimSteps,nRepetitions,inputFile,resultName+"_sr_real_5HT"])

			count+=1
			if count/nSim-percLastPrint>=printPeriod:
				percLastPrint=count/nSim
				print str(round(count/nSim*100))+"% of simulations performed..."


if __name__ == '__main__':
	main()
