import argparse
import sys
sys.path.append('../code')
from tools import seed_handler as sh
import time as timeModule
from mpi4py import MPI
from neuron import h
import numpy as np
from tools import general_tools as gt

def main():
	""" This program launches a CollisionEesNatural simulation with predefined input parameters.
	The plots resulting from this simulation are saved in the Results folder.

	This program can be executed both with and without MPI. In case MPI is used the different processes
	are used to run simulations with different initial condition and the results report the mean of
	all simulations.
	"""

	parser = argparse.ArgumentParser(description="Compute the probability of antidromic collisions - to be run with mpi 40 proc")
	parser.add_argument("--seed", help="positive seed used to initialize random number generators (default = time.time())", type=int, choices=[gt.Range(0,999999)])
	args = parser.parse_args()

	sh.save_seed(timeModule.time())
	from simulations import CollisionEesNatural

	# Create a Neuron ParallelContext object to support parallel simulations
	pc = h.ParallelContext()
	eesFrequencies = np.linspace(5,100,20)
	fiberDelays = [2,10,20]
	fiberFiringRates = np.linspace(5,200,20)
	simulation = CollisionEesNatural(pc,eesFrequencies,fiberDelays,fiberFiringRates)
	simulation.run()
	for i in range(len(fiberDelays)):
		simulation.plot(i,10,"_40p_del"+str(fiberDelays[i])) # to be run with 40 processes
	simulation.plot_isoinformation_surface()

if __name__ == '__main__':
	main()
