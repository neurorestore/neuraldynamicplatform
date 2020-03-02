import argparse
import sys
sys.path.append('../code')
import time as time
from mpi4py import MPI
from neuron import h
from tools import general_tools  as gt
from tools import load_data_tools as ldt
from tools import seed_handler as sh

comm = MPI.COMM_WORLD
sizeComm = comm.Get_size()
rank = comm.Get_rank()

def main():
	""" This program launches a ForSimMuscleSpindles simulation with a NeuralNetwork structure,
	EES amplitude and EES frequency given by the user as argument. The NeuralNetwork
	need to conatain the structure of a muscle spindle sensorimotor circuitry for 2
	antagonist muscles, 'TA' and 'GM' for a rat model and 'TA' and 'GL' for a human model.
	Precomputed senosry information of the Ia and II fibers is used to drive the NN.
	The plots resulting from this simulation are saved in the results folder.

	This program can be executed both with and without MPI. In case MPI is used the cells
	of the NeuralNetwork are shared between the different hosts in order to speed up the
	simulation.

	"""
	parser = argparse.ArgumentParser(description="launch a cybex forward simulation")
	parser.add_argument("eesFrequency", help="ees frequency", type=float, choices=[gt.Range(0,1000)])
	parser.add_argument("eesAmplitude", help="ees amplitude (0-600] or %%Ia_II_Mn")
	parser.add_argument("species", help="simulated species", choices=["rat","human"])
	parser.add_argument("inputFile", help="neural network structure file")
	parser.add_argument("name", help="name to add at the output files")
	parser.add_argument("--simTime", help="simulation time", type=int, default=-1)
	parser.add_argument("--noPlot", help="no plot flag", action="store_true")
	parser.add_argument("--seed", help="positive seed used to initialize random number generators (default = time.time())", type=int, choices=[gt.Range(0,999999)])
	args = parser.parse_args()

	if args.seed is not None: sh.save_seed(args.seed)
	else: sh.save_seed(int(time.time()))

	# Import simulation specific modules
	from simulations import ForSimMuscleSpindlesCybex
	from NeuralNetwork import NeuralNetwork
	from EES import EES


	# Initialze variables...
	if args.eesAmplitude[0]=="%": eesAmplitude = [float(x) for x in args.eesAmplitude[1:].split("_")]
	else: eesAmplitude = float(args.eesAmplitude)
	name = "_"+args.species+"_"+args.name
	if args.species == "human": muscles = {"ext":"GL","flex":"TA"}
	elif args.species == "rat": muscles = {"ext":"GM","flex":"TA"}
	pc = h.ParallelContext()
	nn=NeuralNetwork(pc,args.inputFile)
	ees = EES(pc,nn,eesAmplitude,args.eesFrequency,pulsesNumber=100000,species=args.species)
	ees.get_amplitude(True)
	afferentsInput = ldt.load_afferent_input(args.species,muscles,"cybex")

	if rank==0:
		if args.species == 'human':
			motFile = "./generateForSimInputs/data/human/cybex/humanCybexAnkleControl.mot"
			ankleKinematic = ldt.readCsvGeneral(motFile,8,['time','kinematic'],['time','ankle_angle_r'])
		elif args.species == 'rat':
			motFile = "./generateForSimInputs/data/rat/cybex/ratCybexAnkleControl.mot"
			ankleKinematic = ldt.readCsvGeneral(motFile,8,['time','kinematic'],['time','ankle_flx'])
		ankleKinematic['dt'] = (ankleKinematic['time'][-1]-ankleKinematic['time'].min())/ankleKinematic['time'].size
	else: ankleKinematic = None

	# Run simulation, plot results and save them
	simulation = ForSimMuscleSpindlesCybex(pc,nn, afferentsInput, ees, args.simTime, ankleKinematic)
	simulation.run()
	if not args.noPlot: simulation.plot(name)
	comm.Barrier()
	simulation.save_results(name)



if __name__ == '__main__':
	main()
