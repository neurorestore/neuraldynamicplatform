import argparse
import sys
sys.path.append('../code')
import time
from mpi4py import MPI
from neuron import h
from tools import seed_handler as sh
from tools import general_tools  as gt
from tools import structures_tools as tls
from tools import load_data_tools as ldt
from parameters import RatParameters as rp

comm = MPI.COMM_WORLD
sizeComm = comm.Get_size()
rank = comm.Get_rank()

def main():
	""" This program launches a ForSimRORa simulation with a NeuralNetwork structure,
	EES amplitude and EES frequency given by the user as argument. The NeuralNetwork
	need to conatain the structure of a muscle spindle sensorimotor + RORa cutaneous
	circuitry for 2	antagonist muscles, namely the 'TA' and 'GM'.
	Precomputed senosry information of the Ia, II, SAI and RA fibers is used to drive the NN.
	The plots resulting from this simulation are saved in the results folder.

	This program can be executed both with and without MPI. In case MPI is used the cells
	of the NeuralNetwork are shared between the different hosts in order to speed up the
	simulation.

	e.g: mpiexec -np 4 python scripts/runForSimRORa.py 40 240 1 frwSimRat_testActivity.txt test
	"""

	parser = argparse.ArgumentParser(description="Launch a forward simulation for the RORa network")
	parser.add_argument("eesFrequency", help="ees frequency", type=float, choices=[gt.Range(0,1000)])
	parser.add_argument("eesAmplitude", help="ees amplitude (0-600] or %%Ia_II_Mn")
	parser.add_argument("inputFile", help="neural network structure file")
	parser.add_argument("name", help="name to add at the output files")
	parser.add_argument("--simTime", help="simulation time", type=int, default=-1)
	parser.add_argument("--noPlot", help="no plot flag", action="store_true")
	parser.add_argument("--seed", help="positive seed used to initialize random number generators (default = time.time())", type=int, choices=[gt.Range(0,999999)])
	args = parser.parse_args()

	if args.seed is not None: sh.save_seed(args.seed)
	else: sh.save_seed(int(time.time()))

	# Import simulation specific modules
	from simulations import ForSimRORa
	from simulations import ForSimSpinalModulation
	from NeuralNetwork import NeuralNetwork
	from EES import EES
	from BurstingEES import BurstingEES
	from BaselineActivity import BaselineActivity

	# Initialze variables...
	if args.eesAmplitude[0]=="%": eesAmplitude = [float(x) for x in args.eesAmplitude[1:].split("_")]
	else: eesAmplitude = float(args.eesAmplitude)


	# Create a Neuron ParallelContext object to support parallel simulations
	pc = h.ParallelContext()
	nn=NeuralNetwork(pc,args.inputFile)
	#ees = EES(pc,nn,eesAmplitude,args.eesFrequency,pulsesNumber=100000,species='rat')
	#ees.get_amplitude(True)
	#muscles = rp.get_muscles_dict()
	#afferentsInput = ldt.load_afferent_input('rat',muscles,"static")
	#bs = BaselineActivity(pc,nn,rp.get_interneurons_baseline_fr())

	ees = EES(pc,nn,eesAmplitude,args.eesFrequency)
	ees.get_amplitude(True)
	afferentsInput = create_input()

	simulation = ForSimRORa(pc,nn, afferentsInput, ees, None, args.simTime)
	simulation.run("test")

	showFig = False
	if not args.noPlot: simulation.plot("TA","GM",args.name,showFig)
	comm.Barrier()
	simulation.save_results("TA","GM",args.name)


def create_input(norm=1):
	""" Load previously computed affarent inputs """
	afferents = {}
	afferents['TA'] = {}
	afferents['GM'] = {}
	afferents['TA']['Iaf'] = list(gt.load_txt_mpi('../afferentsFirings/meanFr_Ia_TA_rat.txt')*norm)
	afferents['TA']['IIf'] = list(gt.load_txt_mpi('../afferentsFirings/meanFr_II_TA_rat.txt')*norm)
	afferents['TA']['II_SAIf_foot'] = list(gt.load_txt_mpi('../afferentsFirings/meanFr_SAI_rat.txt')*norm)
	afferents['TA']['II_RAf_foot']  = list(gt.load_txt_mpi('../afferentsFirings/meanFr_RA_rat.txt')*norm)
	afferents['TA']['II_SAIf'] = list(gt.load_txt_mpi('../afferentsFirings/meanFr_SAI_rat.txt')*0)
	afferents['TA']['II_RAf']  = list(gt.load_txt_mpi('../afferentsFirings/meanFr_RA_rat.txt')*0)

	afferents['GM']['Iaf'] = list(gt.load_txt_mpi('../afferentsFirings/meanFr_Ia_GM_rat.txt')*norm)
	afferents['GM']['IIf'] = list(gt.load_txt_mpi('../afferentsFirings/meanFr_II_GM_rat.txt')*norm)
	afferents['GM']['II_SAIf_foot'] = list(gt.load_txt_mpi('../afferentsFirings/meanFr_SAI_rat.txt')*norm)
	afferents['GM']['II_RAf_foot']  = list(gt.load_txt_mpi('../afferentsFirings/meanFr_RA_rat.txt')*norm)
	afferents['GM']['II_SAIf'] = list(gt.load_txt_mpi('../afferentsFirings/meanFr_SAI_rat.txt')*0)
	afferents['GM']['II_RAf']  = list(gt.load_txt_mpi('../afferentsFirings/meanFr_RA_rat.txt')*0)
	dtUpdateAfferent = 5
	afferentsInput = [afferents,dtUpdateAfferent]
	return afferentsInput


if __name__ == '__main__':
	main()
