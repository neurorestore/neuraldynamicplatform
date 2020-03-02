import sys
sys.path.append('../code')
from mpi4py import MPI
from neuron import h
from cells import Motoneuron
from cells import IntFireMn
from simulations import CellsRecording
import numpy as np
import random as rnd
import time
import matplotlib.pyplot as plt
from tools import seed_handler as sh
randomSeed = 123
sh.save_seed(randomSeed)


def main():
	""" Simulates singel synapses on real/artificial motoneurons. """

	pc = h.ParallelContext()
	interval = 100
	start = 250
	number = 10000
	simTime = 400
	nCells = 10
	scale = 35

	""" RealMn excitatory """
	cellsNoDrug = []
	targetsNoDrug = []
	ncsNoDrug = []
	apsNoDrug = []

	cellsDrug = []
	targetsDrug = []
	ncsDrug = []
	apsDrug = []

	stim = h.NetStim()
	stim.interval = interval
	stim.start = start
	stim.number = number

	for i in range(nCells):
		cellsNoDrug.append(Motoneuron(drug=False))
		cellsDrug.append(Motoneuron(drug=True))
		targetsNoDrug.append(cellsNoDrug[-1].create_synapse("excitatory"))
		targetsDrug.append(cellsDrug[-1].create_synapse("excitatory"))

		ncsDrug.append(h.NetCon(stim,targetsDrug[-1]))
		ncsNoDrug.append(h.NetCon(stim,targetsNoDrug[-1]))
		ncsDrug[-1].weight[0] = 0.047*scale
		ncsNoDrug[-1].weight[0] = 0.047*scale

		ncsNoDrug.append(cellsNoDrug[-1].connect_to_target(None))
		apsNoDrug.append(h.Vector())
		ncsNoDrug[-1].record(apsNoDrug[-1])

		ncsDrug.append(cellsDrug[-1].connect_to_target(None))
		apsDrug.append(h.Vector())
		ncsDrug[-1].record(apsDrug[-1])

	somasDrug = [cellDrug.soma for cellDrug in cellsDrug]
	somasNoDrug = [cellNoDrug.soma for cellNoDrug in cellsNoDrug]

	somaDict = {"somaDrug":somasDrug,"somaNoDrug":somasNoDrug}
	modelType = {"somaDrug":"real","somaNoDrug":"real"}
	sim = CellsRecording(pc,somaDict,modelType,simTime)
	sim.run()

	totTime = simTime-start
	meanFrNoDrug = np.mean([apVector.size()*1000/totTime for apVector in apsNoDrug])
	meanFrDrug = np.mean([apVector.size()*1000/totTime for apVector in apsDrug])
	print "\n\nMn NoDrug mean firing rate is: "+str(meanFrNoDrug)+"Hz \n"
	print "\n\nMn Drug firing rate is: "+str(meanFrDrug)+"Hz \n"

	title = "Mn NoDrug mean firing rate is: "+str(meanFrNoDrug)+"Hz \n Mn Drug firing rate is: "+str(meanFrDrug)+"Hz"
	sim.plot("MnReal_excitatory",title)


	""" IntFireMn excitatory """
	# cell = IntFireMn()
	# target = cell.cell
	#
	# stim = h.NetStim()
	# stim.interval = interval
	# stim.start = start
	# stim.number = number
	#
	# nc = h.NetCon(stim,target)
	# nc.weight[0] = 0.014 #rnd.normalvariate(0.0339,0.0339*0.1)
	#
	# cellDict = {"cell":[cell]}
	# modelType = {"cell":"artificial"}
	# sim = CellsRecording(pc,cellDict,modelType,simTime)
	# sim.run()
	# sim.plot("IntFireMn_excitatory")



if __name__ == '__main__':
	main()
