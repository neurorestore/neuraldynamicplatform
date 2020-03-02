import argparse
import sys
import pickle
sys.path.append('../code')
import time
from mpi4py import MPI
from neuron import h
from tools import general_tools  as gt
from tools import load_data_tools as ldt
from tools import seed_handler as sh

comm = MPI.COMM_WORLD
sizeComm = comm.Get_size()
rank = comm.Get_rank()

def main():
	""" This program launches a ForSimMuscleSpindles simulation with a predefined NeuralNetwork structure,
	EES amplitude and EES frequency given by the user as argument.
	The plots resulting from this simulation are saved in the results folder.

	This program can be executed both with and without MPI. In case MPI is used the cells
	of the NeuralNetwork are shared between the different hosts in order to speed up the
	simulation.
	"""

	parser = argparse.ArgumentParser(description="launch a ForSimMuscleSpindles simulation")
	parser.add_argument("eesFrequency", help="ees frequency", type=float, choices=[gt.Range(0,1000)])
	parser.add_argument("eesAmplitude", help="ees amplitude (0-600] or %%Ia_II_Mn")
	parser.add_argument("species", help="simulated species", choices=["rat","human"])
	parser.add_argument("modulation", help="type of stimulation modulation", choices=["kin","emg","kinemg","sensory","proportional","proportionalFloatData"])
	parser.add_argument("inputFile", help="neural network structure file")
	parser.add_argument("name", help="name to add at the output files")
	parser.add_argument("--simTime", help="simulation time", type=int, default=-1)
	parser.add_argument("--noPlot", help="no plots flag", action="store_true")
	parser.add_argument("--burstingEes", help="flag to use burst stimulation", action="store_true")
	parser.add_argument("--nPulsesPerBurst", help="number of pulses per burst", type=int, default=5)
	parser.add_argument("--burstsFrequency", help="stimulation frequency within bursts",type=float, default=600, choices=[gt.Range(0,1000)])
	parser.add_argument("--seed", help="positive seed used to initialize random number generators (default = time.time())", type=int, choices=[gt.Range(0,999999)])
	args = parser.parse_args()

	if args.seed is not None: sh.save_seed(args.seed)
	else: sh.save_seed(int(time.time()))

	# Import simulation specific modules
	from simulations import ForSimMuscleSpindles
	from NeuralNetwork import NeuralNetwork
	from EES import EES
	from BurstingEES import BurstingEES


	# Initialze variables...
	if args.eesAmplitude[0]=="%": eesAmplitude = [float(x) for x in args.eesAmplitude[1:].split("_")]
	else: eesAmplitude = float(args.eesAmplitude)
	name = "_"+args.species+"_"+args.name
	if args.species == "rat":
		muscles = {"ext":"GM","flex":"TA"}
		if args.modulation == "kin": fileStimMod = "generateForSimInputs/output/spatiotemporalStimulationRatKinBased.p"
		elif args.modulation == "emg": fileStimMod = "generateForSimInputs/output/spatiotemporalStimulationRatEmgBased.p"
		elif args.modulation == "kinemg": fileStimMod = "generateForSimInputs/output/spatiotemporalStimulationRatKinEmgBased.p"
		if 'fileStimMod' in locals():
			with open(fileStimMod, 'r') as pickle_file:
				eesModulation = pickle.load(pickle_file)
	elif args.species == "human":
		muscles = {"ext":"SOL","flex":"TA"}
		if args.modulation == "kin": fileStimMod = "generateForSimInputs/output/spatiotemporalStimulationHumanKinBased.p"
		elif args.modulation == "emg": fileStimMod = "generateForSimInputs/output/spatiotemporalStimulationHumanEmgBased.p"
		elif args.modulation == "kinemg": fileStimMod = "generateForSimInputs/output/spatiotemporalStimulationHumanKinEmgBased.p"
		elif args.modulation == "sensory": fileStimMod = "generateForSimInputs/output/spatiotemporalStimulationHumanSensoryBased.p"
		elif args.modulation == "proportional": fileStimMod = "generateForSimInputs/output/spatiotemporalProportionalStimulationHumanSensoryBased.p"
		elif args.modulation == "proportionalFloatData": fileStimMod = "generateForSimInputs/output/spatiotemporalProportionalStimulationHumanSensoryBased_fromFloatDataForHumData.p"
		if 'fileStimMod' in locals():
			with open(fileStimMod, 'r') as pickle_file:
				eesModulation = pickle.load(pickle_file)

	pc = h.ParallelContext()
	nn=NeuralNetwork(pc,args.inputFile)
	if not args.burstingEes: ees = EES(pc,nn,eesAmplitude,args.eesFrequency,pulsesNumber=100000,species=args.species)
	else: ees = BurstingEES(pc,nn,eesAmplitude,args.eesFrequency,args.burstsFrequency,args.nPulsesPerBurst,species=args.species)
	ees.get_amplitude(True)
	afferentsInput = ldt.load_afferent_input(args.species,muscles)

	# if 'fileStimMod' not in locals() and "afferents" in args.modulation:
	# 	afferents,dtUpdateAfferent = afferentsInput
	# 	stim = {}
	# 	for muscle in muscles:
	# 		stim[muscle] = afferents[muscle]['Iaf']
	#
	# 	eesModulation = {"modulation":stim, "dt":1000*dwnSamplFcrEmg*musclesActivation['dt']}
	# 	stim[muscle] = np.zeros(musclesActivation[muscle].size)

	simulation = ForSimMuscleSpindles(pc,nn, afferentsInput, ees, eesModulation, args.simTime)

	# Run simulation, plot results and save them
	simulation.run()
	if not args.noPlot: simulation.plot(muscles["flex"],muscles["ext"],name,False)
	comm.Barrier()
	simulation.save_results(muscles["flex"],muscles["ext"],name)


if __name__ == '__main__':
	main()
