import argparse
import sys
sys.path.append('../code')
from tools import seed_handler as sh
import time
from mpi4py import MPI
from neuron import h
import numpy as np
from tools import general_tools  as gt

def main():
	""" Computes isomodulation curves given a certain fiber delay.
	MPI is supported.
	"""
	parser = argparse.ArgumentParser(description="Compute the isomodulation curves given a certain fiber delay")
	parser.add_argument("minMod", help="min afferent modulation", type=float)
	parser.add_argument("maxMod", help="max afferent modulation", type=float)
	parser.add_argument("nSteps", help="number of steps", type=int)
	parser.add_argument("delay", help="delay of the fiber in ms",type=int,choices=[gt.Range(1,30)])
	parser.add_argument("species", help="simulated species", choices=["rat","human"])
	parser.add_argument("totTime", help="simulation max time",type=float,choices=[gt.Range(1,999999)])
	parser.add_argument("--seed", help="positive seed used to initialize random number generators (default = time.time())", type=int, choices=[gt.Range(0,999999)])
	args = parser.parse_args()

	if args.seed is not None: sh.save_seed(args.seed)
	else: sh.save_seed(int(time.time()))

	# Import simulation specific modules
	from simulations import IsoModulationCurves

	modulations = np.linspace(args.minMod,args.maxMod,args.nSteps)

	if args.species == 'rat':
		firingRateProfile = list(gt.load_txt_mpi('../afferentsFirings/meanFr_Ia_TA_rat.txt'))
	elif args.species == 'human':
		firingRateProfile = list(gt.load_txt_mpi('../afferentsFirings/meanFr_Ia_TA_human.txt'))
	dtUpdateAfferent = 5
	pc = h.ParallelContext()

	simulation = IsoModulationCurves(pc,modulations,args.delay,args.totTime,firingRateProfile,dtUpdateAfferent)
	simulation.run()
	simulation.plot()
	simulation.plot_afferent_modulation([0.1,0.6],fileName='2017_06_20_IsoModulationCurves_Delay_16.0.p')

if __name__ == '__main__':
	main()
