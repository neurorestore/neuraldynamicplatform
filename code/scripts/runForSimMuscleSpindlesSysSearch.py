import sys
sys.path.append('../code')
import subprocess
from tools import structures_tools as tls
import numpy as np
from tools import general_tools as gt

def main():
	""" This program launches a parameters systematic search for a ForSimMuscleSpindles.
	The different parameters that are changed over time are directly defined in the main function.
	The program doesn't have to be executed by MPI.

	typical use: 	nohup python scripts/runForSimMuscleSpindlesSysSearch.py &
	"""
	nProc = 4
	pathToResults = "../../results/sysHuman29"
	seed = "1"

	species = "human"

	eesAmplitudes = [250,270]
	eesFrequencies = [20,60]
	delays = [2,16]

	weights_1 = 0.014*np.arange(1,2.01,0.25) #in templateFrwSimHuman.txt: Iaf->Mn
	weights_3 = 0.011*np.arange(1,2.01,0.25) #in templateFrwSimHuman.txt: IIf->ExcInt

	weights_2 = 0.011*np.arange(1,4.01,0.33) #in templateFrwSimHuman.txt: Iaf->IaInt
	weights_4 = 0.011*np.arange(1,4.01,0.33) #in templateFrwSimHuman.txt: IIf->IaInt

	totSimTime = 4000
	simLabel = "_sysHumanGod"

	if species == "human":
		templateFile = "templateFrwSimHumanSOL.txt"
	elif species == "rat":
		templateFile = "templateFrwSim.txt"
	else: raise(Exception("Unkown species"))
	nSim = len(eesAmplitudes)*len(eesFrequencies)*len(delays)*len(weights_1)*len(weights_2)*len(weights_4)
	count = 0.
	percLastPrint = 0.
	printPeriod = 0.005

	for delay in delays:
		for w1,w3 in zip(weights_1,weights_3):
			for w2 in weights_2:
				for w4 in weights_4:
					inputFile = "generatedStructures/ss_species"+species+"_d_"+str(delay)+"_w1_"+str(w1)+"_w2_"+str(w2)+"_w3_"+str(w3)+".txt"
					tls.modify_network_structure(templateFile,inputFile,delay,[w1,w2,w3,w4])
					for eesAmplitude in eesAmplitudes:
						for eesFrequency in eesFrequencies:
							name = "Tonic_w1_"+str(w1)+"_w2_"+str(w2)+"_w3_"+str(w3)+"_w4_"+str(w4)+"_"+str(eesAmplitude)+simLabel
							resultFile = gt.find("*"+str(eesFrequency)+"Hz_Delay_"+str(delay)+"ms*"+name+".p",pathToResults)
							if not resultFile:
								program = ['mpiexec','-np',str(nProc),'python','./scripts/runForSimMuscleSpindles.py',\
									str(eesFrequency),str(eesAmplitude),species,inputFile,name,"--simTime",str(totSimTime),"--seed",seed]
								gt.run_subprocess(program)
							count+=1
							if count/nSim-percLastPrint>=printPeriod:
								percLastPrint=count/nSim
								print str(round(count/nSim*100))+"% of simulations performed..."



if __name__ == '__main__':
	main()
