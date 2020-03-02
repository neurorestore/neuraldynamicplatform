import argparse
import sys
sys.path.append('../code')
import time
from mpi4py import MPI
from neuron import h
import random as rnd
from tools import seed_handler as sh
from tools import general_tools  as gt

comm = MPI.COMM_WORLD
sizeComm = comm.Get_size()
rank = comm.Get_rank()


def main():
	""" This program launches a ForSimSpinalModulation simulation with a predefined NeuralNetwork structure.
	EES amplitude and EES frequency are given by the user as argument.
	The plots resulting from this simulation are saved in the results folder.

	This program doesn't support MPI!
	"""
	parser = argparse.ArgumentParser(description="Estimate the efferents modulation induced by EES and afferent input together")
	parser.add_argument("eesFrequency", help="ees frequency", type=float, choices=[gt.Range(0,1000)])
	parser.add_argument("eesAmplitude", help="ees amplitude (0-600] or %%Ia_II_Mn")
	parser.add_argument("species", help="simulated species", choices=["rat","human"])
	parser.add_argument("afferetntFiringRate", help="afferent firing rate", type=float, choices=[gt.Range(0,1000)])
	parser.add_argument("name", help="name to add at the output files")
	parser.add_argument("--mnReal", help="Real Mn flag, IntFire Mn otherwise",action="store_true")
	parser.add_argument("--simTime", help="simulation time", type=int, default=1000)
	parser.add_argument("--plot", help="(0 or 1 or 2 for raster plot)", choices=[0,1,2],type=int, default=1)
	parser.add_argument("--burstingEes", help="flag to use burst stimulation", action="store_true")
	parser.add_argument("--nPulsesPerBurst", help="number of pulses per burst", type=int, default=5)
	parser.add_argument("--burstsFrequency", help="stimulation frequency within bursts",type=float, default=600, choices=[gt.Range(0,1000)])
	parser.add_argument("--seed", help="positive seed used to initialize random number generators (default = time.time())", type=int, choices=[gt.Range(0,999999)])
	args = parser.parse_args()

	if args.seed is not None: sh.save_seed(args.seed)
	else: sh.save_seed(int(time.time()))

	# Import simulation specific modules
	from simulations import ForSimSpinalModulation
	from NeuralNetwork import NeuralNetwork
	from EES import EES
	from BurstingEES import BurstingEES

	# Initialze variables...
	if args.eesAmplitude[0]=="%": eesAmplitude = [float(x) for x in args.eesAmplitude[1:].split("_")]
	else: eesAmplitude = float(args.eesAmplitude)
	pc = h.ParallelContext()
	if args.mnReal: nnStructureFile = "fsMnMod.txt"
	else: nnStructureFile = "fsMnArtMod.txt"

	nn=NeuralNetwork(pc,nnStructureFile)
	if not args.burstingEes: ees = EES(pc,nn,eesAmplitude,args.eesFrequency,pulsesNumber=100000,species=args.species)
	else: ees = BurstingEES(pc,nn,eesAmplitude,args.eesFrequency,args.burstsFrequency,args.nPulsesPerBurst,species=args.species)
	ees.get_amplitude(True)
	afferentsInput = create_input(args.afferetntFiringRate,args.simTime)

	# Set last spike time at 500 to delay the start of the afferent fibers
	for muscle in nn.cells:
		for cellName in nn.cells[muscle]:
			if cellName in nn.get_afferents_names():
				for cell in nn.cells[muscle][cellName]:cell.initialise(rnd.normalvariate(500,10))

	if args.mnReal:
		cellsToRecord = {"MnReal":[mn.soma for mn in nn.cells['GM']['MnReal']]}
		modelTypes = {"MnReal":"real"}
		simulation = ForSimSpinalModulation(pc,nn,cellsToRecord,modelTypes, afferentsInput, ees, None, args.simTime)
		simulation.run()
		if args.plot == 1: simulation.plot('GM','MnReal',args.name)
		elif args.plot == 2: simulation.raster_plot(args.name)
		comm.Barrier()
	else:
		cellsToRecord = {"Mn":nn.cells['GM']['Mn']}
		modelTypes = {"Mn":"artificial"}
		simulation = ForSimSpinalModulation(pc,nn,cellsToRecord,modelTypes, afferentsInput, ees, None, args.simTime)
		simulation.run()
		if args.plot == 1: simulation.plot('GM','Mn',args.name)
		elif args.plot == 2: simulation.raster_plot(args.name)
		comm.Barrier()


def create_input(afferetntFiringRate,time):
	""" Load previously computed affarent inputs """
	afferents = {}
	afferents['GM'] = {}
	dtUpdateAfferent = 5.
	afferents['GM']['Iaf'] = [afferetntFiringRate]*(int(time/dtUpdateAfferent)+1)
	afferentsInput = [afferents,dtUpdateAfferent]

	return afferentsInput


if __name__ == '__main__':
	main()
