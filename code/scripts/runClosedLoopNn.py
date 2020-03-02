import sys
sys.path.append('../code')
from tools import seed_handler as sh
import time as timeModule
sh.save_seed(timeModule.time())
from mpi4py import MPI
from neuron import h
from simulations import ClosedLoop
from NeuralNetwork import NeuralNetwork
from NetworkStimulation import NetworkStimulation
from EES import EES
import numpy as np
#TODO - within the HBP this part has compleatly chanched - there is another repo for the closedloop simulations

comm = MPI.COMM_WORLD
sizeComm = comm.Get_size()
rank = comm.Get_rank()

def main():
	""" This program runs the neural network for a closed loop simulation.
	MPI is supported.
	"""
	if len(sys.argv)<4:
		if rank==0:
			print "Error in arguments. Required arguments:"
			print "\t ees frequency [0-1000] "
			print "\t ees amplitude (0-600] or %Ia_II_Mn "
			print "\t neural network structure file .txt"
			print "Optional arguments:"
			print "Species (mouse, rat or human)"
			print "\t tot time of simulation (default = 999999)"
			print "\t perturbation parameters %muscleName/cellsName/percStimFiber/frequency/pulsesNumber/startTime or False (default = False)"
		sys.exit(-1)

	eesFrequency = float(sys.argv[1])

	if sys.argv[2][0]=="%": eesAmplitude = [float(x) for x in sys.argv[2][1:].split("_")]
	else: eesAmplitude = float(sys.argv[2])
	inputFile = sys.argv[3]
	if len(sys.argv)>=5: species = sys.argv[4]
	else: species = "human"
	if len(sys.argv)>=6: tStop = float(sys.argv[5])
	else: tStop = 999999
	if len(sys.argv)>=7 and sys.argv[6][0] == "%":
		perturbation = True
		pertParams = [x for x in sys.argv[6][1:].split("/")]
		pertParams[2:] = [float(x) for x in pertParams[2:]]
	else: perturbation = False


	# Create a Neuron ParallelContext object to support parallel simulations
	pc = h.ParallelContext()

	nn=NeuralNetwork(pc,inputFile)

	if perturbation: nnStim = NetworkStimulation(pc,nn,nn.cellsId[pertParams[0]][pertParams[1]],pertParams[1],pertParams[2],pertParams[3],pertParams[4],pertParams[5])

	dtCommunication = 20
	ees = EES(pc,nn,eesAmplitude,eesFrequency,pulsesNumber=100000,species=species)
	ees.get_amplitude(True)

	simulation = ClosedLoop(pc, nn, dtCommunication, species, ees, tStop)
	simulation.run()

if __name__ == '__main__':
	main()
