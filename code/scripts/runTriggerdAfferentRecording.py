import argparse
import sys
sys.path.append('../code')
import time as time
from mpi4py import MPI
from neuron import h
from tools import general_tools  as gt
from tools import seed_handler as sh

def main():
	""" To simulate an SEP/antidromic collision experiment
	"""
	parser = argparse.ArgumentParser(description="simulate an SEP/antidromic collision experiment")
	parser.add_argument("eesFrequency", help="ees frequency",type=float,choices=[gt.Range(1,1000)])
	parser.add_argument("delay", help="delay of the fiber in ms",type=int,choices=[gt.Range(1,30)])
	parser.add_argument("pnsFrequency", help="peripheral nerve stimulation frequency",type=float,choices=[gt.Range(1,1000)])
	parser.add_argument("segmentToRecord", help="segment to record [0-delay]",type=int,choices=[gt.Range(1,30)])
	parser.add_argument("tstop", help="simulation max time",type=int,choices=[gt.Range(1,999999)])
	parser.add_argument("--seed", help="positive seed used to initialize random number generators (default = time.time())", type=int, choices=[gt.Range(0,999999)])
	args = parser.parse_args()

	if args.seed is not None: sh.save_seed(args.seed)
	else: sh.save_seed(int(time.time()))

	# Import simulation specific modules
	from simulations import CollisionEesNatural

	# Create a Neuron ParallelContext object to support parallel simulations
	pc = h.ParallelContext()
	eesFrequencies = [float(sys.argv[1])]
	fiberDelays = [float(sys.argv[2])]
	fiberFiringRates = [float(sys.argv[3])]
	tstop = int(sys.argv[5])
	simulation = CollisionEesNatural(pc,[args.eesFrequency],[args.delay],[args.pnsFrequency],args.segmentToRecord,args.tstop)
	simulation.run()

	simulation.plot_recorded_segment()

if __name__ == '__main__':
	main()
