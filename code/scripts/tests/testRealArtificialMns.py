import argparse
import sys
sys.path.append('../code')
from mpi4py import MPI
from neuron import h
from cells import Motoneuron
from cells import IntFireMn
from cells import IntFire
from simulations import CellsRecording
import numpy as np
import random as rnd
import time

def main():
	""" Simulates singel synapses on real/artificial motoneurons. """
	parser = argparse.ArgumentParser(description="Test different Mn models and synapses")
	parser.add_argument("--realInh", help="real inhibitory flag", action="store_true")
	parser.add_argument("--artInh", help="intFireMn inhibitory flag", action="store_true")
	parser.add_argument("--realExc", help="real excitatory flag", action="store_true")
	parser.add_argument("--artExc", help="intFireMn excitatory flag", action="store_true")
	parser.add_argument("--intInh", help="intFire inhibitory flag", action="store_true")
	parser.add_argument("--intExc", help="intFire excitatory flag", action="store_true")
	args = parser.parse_args()

	rnd.seed(time.time())
	pc = h.ParallelContext()
	interval = 1000
	start = 100
	number = 10000
	simTime = 250
	mult=1#60*0.05
	nCells = 50

	""" RealMn inhibitory """
	if args.realInh:
		cells = [Motoneuron() for i in range(nCells)]
		targets = [cell.create_synapse("inhibitory") for cell in cells]

		stim = h.NetStim()
		stim.interval = interval
		stim.start = start
		stim.number = number

		ncs = [h.NetCon(stim,target) for target in targets]
		for nc in ncs: nc.weight[0] = 0.0023*232


		somaDict = {"soma":[cell.soma for cell in cells]}
		modelType = {"soma":"real"}
		sim = CellsRecording(pc,somaDict,modelType,simTime)
		h.finitialize(-69.3)
		sim.run()
		sim.plot("MnReal_inhib")

	""" IntFireMn inhibitory """
	if args.artInh:
		cells = [IntFireMn() for i in range(nCells)]
		targets = [cell.cell for cell in cells]

		stim = h.NetStim()
		stim.interval = interval
		stim.start = start
		stim.number = number

		ncs = [h.NetCon(stim,target) for target in targets]
		for nc in ncs: nc.weight[0] = -0.002*232

		cellDict = {"cell":cells}
		modelType = {"cell":"artificial"}
		sim = CellsRecording(pc,cellDict,modelType,simTime)
		sim.run()
		sim.plot("IntFireMn_inhib")

	""" RealMn excitatory """
	if args.realExc:
		cells = [Motoneuron() for i in range(nCells)]
		targets = [cell.create_synapse("excitatory") for cell in cells]


		stim = h.NetStim()
		stim.interval = interval
		stim.start = start
		stim.number = number

		ncs = [h.NetCon(stim,target) for target in targets]
		for nc in ncs: nc.weight[0] = mult*0.047 #0.0445 #0.048

		somaDict = {"soma":[cell.soma for cell in cells]}
		modelType = {"soma":"real"}
		sim = CellsRecording(pc,somaDict,modelType,simTime)
		sim.run()
		sim.plot("MnReal_excitatory")

	""" IntFireMn excitatory """
	if args.artExc:
		cells = [IntFireMn() for i in range(nCells)]
		targets = [cell.cell for cell in cells]

		stim = h.NetStim()
		stim.interval = interval
		stim.start = start
		stim.number = number

		ncs = [h.NetCon(stim,target) for target in targets]
		w1 = 0.0210
		for nc in ncs: nc.weight[0] = mult*w1

		cellDict = {"cell":cells}
		modelType = {"cell":"artificial"}
		sim = CellsRecording(pc,cellDict,modelType,simTime)
		sim.run()
		sim.plot("IntFireMn_excitatory")

	""" IntFire excitatory """
	if args.intExc:
		cell = IntFire()
		target = cell.cell

		stim = h.NetStim()
		stim.interval = interval
		stim.start = start
		stim.number = number

		nc = h.NetCon(stim,target)
		nc.weight[0] = 0.9 #rnd.normalvariate(0.0339,0.0339*0.1)

		cellDict = {"cell":[cell]}
		modelType = {"cell":"artificial"}
		sim = CellsRecording(pc,cellDict,modelType,simTime)
		sim.run()
		sim.plot("IntFire_excitatory")

	""" IntFire inhibitory """
	if args.intInh:
		cell = IntFire()
		target = cell.cell

		stim = h.NetStim()
		stim.interval = interval
		stim.start = start
		stim.number = number

		nc = h.NetCon(stim,target)
		nc.weight[0] = -0.9 #rnd.normalvariate(0.0339,0.0339*0.1)

		cellDict = {"cell":[cell]}
		modelType = {"cell":"artificial"}
		sim = CellsRecording(pc,cellDict,modelType,simTime)
		sim.run()
		sim.plot("IntFire_inhibitory")

if __name__ == '__main__':
	main()
