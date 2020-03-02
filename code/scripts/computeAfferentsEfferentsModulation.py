import argparse
import sys
sys.path.append('../code')
import time
import random as rnd
from mpi4py import MPI
from neuron import h
from tools import seed_handler as sh
from tools import general_tools  as gt

comm = MPI.COMM_WORLD
sizeComm = comm.Get_size()
rank = comm.Get_rank()

def main():
	""" This program launches a ForSimSpinalModulation simulation with a given NeuralNetwork structure.
	Raster plots of Iaf and Mns are plotted.
	EES amplitude and EES frequency are given by the user as argument.
	The plots resulting from this simulation are saved in the results folder.

	This program doesn't support MPI!
	"""
	parser = argparse.ArgumentParser(description="Estimate the efferents modulation induced by EES and afferent input together")
	parser.add_argument("eesFrequency", help="ees frequency", type=float, choices=[gt.Range(0,1000)])
	parser.add_argument("eesAmplitude", help="ees amplitude (0-600] or %%Ia_II_Mn")
	parser.add_argument("species", help="simulated species", choices=["rat","human"])
	parser.add_argument("inputFile", help="neural network structure file (e.g. fsSFrFfMnArtModHuman.txt)")
	parser.add_argument("name", help="name to add at the output files")
	parser.add_argument("--mnReal", help="Real Mn flag, IntFire Mn otherwise",action="store_true")
	parser.add_argument("--simTime", help="simulation time", type=int, default=1000)
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
	from NetworkStimulation import NetworkStimulation

	# Initialze variables...
	if args.eesAmplitude[0]=="%": eesAmplitude = [float(x) for x in args.eesAmplitude[1:].split("_")]
	else: eesAmplitude = float(args.eesAmplitude)
	name = args.name+"_amp_"+args.eesAmplitude+"_freq_"+str(args.eesFrequency)
	pc = h.ParallelContext()
	nn=NeuralNetwork(pc,args.inputFile)
	if not args.burstingEes: ees = EES(pc,nn,eesAmplitude,args.eesFrequency,pulsesNumber=100000,species=args.species)
	else: ees = BurstingEES(pc,nn,eesAmplitude,args.eesFrequency,args.burstsFrequency,args.nPulsesPerBurst,species=args.species)
	ees.get_amplitude(True)
	print "The stimulation frequency is: ",args.eesFrequency," Hz"
	afferentsInput = None

	cellsToRecord = {}
	cellsToRecord['Iaf'] = nn.cells['SOL']['Iaf']
	cellsToRecord['MnS']=nn.cells['SOL']['MnS']
	# cellsToRecord['MnFf']=nn.cells['SOL']['MnFf']
	# cellsToRecord['MnFr']=nn.cells['SOL']['MnFr']
	# modelTypes = {"MnS":"artificial","MnFr":"artificial","MnFf":"artificial","Iaf":"artificial"}
	modelTypes = {"MnS":"artificial","Iaf":"artificial"}
	simulation = ForSimSpinalModulation(pc,nn,cellsToRecord,modelTypes, afferentsInput, None, None, args.simTime)
	simulation.set_results_folder("../../results/AffEffModSweap/")
	simulation.run()
	simulation.raster_plot(name,False)
	comm.Barrier()

	simulation.save_results(name)

if __name__ == '__main__':
	main()
