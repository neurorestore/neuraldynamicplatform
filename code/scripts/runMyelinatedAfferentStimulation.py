import sys
sys.path.append('../code')
from tools import seed_handler as sh
import time as timeModule
from mpi4py import MPI
from neuron import h

def main():
	""" This program launch a MyelinatedAfferentStimulation simulation with predefined input parameters.
	The plot resulting from this simulation are saved in the Results folder.

	This program can be executed both with and without MPI. However MPI is not supported and the different
	hosts will run the same code.
	"""


	sh.save_seed(timeModule.time())
	# Import simulation specific modules
	from simulations import MyelinatedAfferentStimulation

	# Create a Neuron ParallelContext object to support parallel simulations
	pc = h.ParallelContext()
	simulation = MyelinatedAfferentStimulation(pc,tstop=20,fiberType="richardson")

	# Select the first and last segments
	segment_1 = simulation.fiber.node[-1]
	segment_2 = simulation.fiber.node[0]

	# Attach a netStim object to the selected segments
	simulation.attach_netstim(segment_1,1000)
	simulation.attach_netstim(segment_2,1000)

	simulation.run()
	simulation.plot()

if __name__ == '__main__':
	main()
