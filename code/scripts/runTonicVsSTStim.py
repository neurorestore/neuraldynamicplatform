import sys
sys.path.append('../code')
import subprocess
import numpy as np
from tools import general_tools as gt
import time
import pickle

def main():
	""" Run two forward simulations (standard tonic and spatiotemparl modulation)
	and eventualy makes a video of the emg signals.
	"""

	eesFrequency = "60"
	eesAmplitude = "270"
	species = "human"
	inputFile = "frwSimHuman.txt"
	simTime = "6000"
	plotResults = "True"
	nProc = 4
	pathToResults = "../../results"
	seed = "1"

	# Run tonic simulation
	name = eesAmplitude+eesFrequency+species+"tonicStimulationHuman"
	resultFile = gt.find("*"+name+"*.p",pathToResults)
	if not resultFile:
		program = ['mpiexec','-np',str(nProc),'python','./scripts/runForSimMuscleSpindles.py',\
			eesFrequency,eesAmplitude,species,inputFile,name,"--simTime",simTime,"--seed",seed]
		gt.run_subprocess(program)
		resultFile = gt.find("*"+name+"*.p",pathToResults)

	# Make video
	with open(resultFile[0], 'r') as pickle_file:
		emg = pickle.load(pickle_file)
	dt = 1
	if species =="human": data = {"Flexor":emg["TA"]['Mn'],"Extensor":emg["GL"]['Mn']}
	elif species =="rat": data = {"Flexor":emg["TA"]['Mn'],"Extensor":emg["GM"]['Mn']}

	name = time.strftime("%Y_%m_%d_"+name)
	fileName = pathToResults+"/"+name
	windowLength = 1500
	gt.make_video(data,dt,fileName,windowLength)

	# Run spatiotemporal simulation
	emgVsKinMod = "kinemg"
	name = eesAmplitude+eesFrequency+species+"SpatioTemporal%sModStimulationHuman"%(emgVsKinMod)
	resultFile = gt.find("*"+name+"*.p",pathToResults)
	if not resultFile:
		program = ['mpiexec','-np',str(nProc),'python','./scripts/runForSimMuscleSpindlesStimModulation.py',\
			eesFrequency,eesAmplitude,species,emgVsKinMod,inputFile,name,"--simTime",simTime,"--seed",seed]
		gt.run_subprocess(program)
		resultFile = gt.find("*"+name+"*.p",pathToResults)

	# Make video
	with open(resultFile[0], 'r') as pickle_file:
		emg = pickle.load(pickle_file)
	dt = 1
	if species =="human": data = {"Flexor":emg["TA"]['Mn'],"Extensor":emg["GL"]['Mn']}
	elif species =="rat": data = {"Flexor":emg["TA"]['Mn'],"Extensor":emg["GM"]['Mn']}

	name = time.strftime("%Y_%m_%d_"+name)
	fileName = pathToResults+"/"+name
	windowLength = 1500
	gt.make_video(data,dt,fileName,windowLength)


if __name__ == '__main__':
	main()
