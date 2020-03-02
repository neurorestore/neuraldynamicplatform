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
import numpy as np

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

	e.g: mpiexec -np 4 python scripts/InvestigateMembrane.py frwSimRatTest.txt test
	"""

	parser = argparse.ArgumentParser(description="Launch a forward simulation for the RORa network")
	parser.add_argument("inputFile", help="neural network structure file")
	parser.add_argument("name", help="name to add at the output files")
	parser.add_argument("--simTime", help="simulation time", type=int, default=-1)
	parser.add_argument("--noPlot", help="no plot flag", action="store_true")
	parser.add_argument("--seed", help="positive seed used to initialize random number generators (default = time.time())", type=int, choices=[gt.Range(0,999999)])
	args = parser.parse_args()

	if args.seed is not None: sh.save_seed(args.seed)
	else: sh.save_seed(int(time.time()))

	# Import simulation specific modules
	from simulations import ForSimSpinalModulation
	from NeuralNetwork import NeuralNetwork
	from EES import EES
	from BurstingEES import BurstingEES
	from BaselineActivity import BaselineActivity

	# Initialze variables...
	eesAmplitudes = [float(230)]
	eesFrequency = float(4)

	# Create a Neuron ParallelContext object to support parallel simulations
	simTime = 300 #250

	pc = h.ParallelContext()
	nn=NeuralNetwork(pc,args.inputFile)
	ees = EES(pc,nn,eesAmplitudes[0],eesFrequency,pulsesNumber=100000,species='rat')
	ees.get_amplitude(True)
	muscles = rp.get_muscles_dict()
	bs = BaselineActivity(pc,nn,rp.get_interneurons_baseline_fr())

	afferentsInput = None
	eesModulation = None

	cellsToRecord = {"MnGM":nn.cells['GM']['Mn'],\
					 "MnTA":nn.cells['TA']['Mn']}
	modelTypes = {"MnGM":"artificial","MnTA":"artificial"}
	simulation = ForSimSpinalModulation(pc,nn,cellsToRecord,modelTypes, afferentsInput, ees, eesModulation, simTime)
	membranePotentials = []
	taEmg = []
	taSpikes = []
	taStatTemp = []
	gmEmg = []
	gmSpikes = []
	gmStatTemp = []
	nSamplesToAnalyse = -100 # last 100 samples
	for eesAmplitude in eesAmplitudes:
		ees.set_amplitude(eesAmplitude)
		percFiberActEes = ees.get_amplitude(True)
		print percFiberActEes
		result_name = args.name + str(eesAmplitude)
		simulation.run(result_name)
		showFig = False
		PlotName = args.name + str(eesAmplitude)
		simulation.plot("TA","GM",PlotName,showFig)

		# Extract emg responses
		try: taEmg.append(simulation.get_estimated_emg("TA")[nSamplesToAnalyse:])
		except (ValueError, TypeError) as error: taEmg.append(np.zeros(abs(nSamplesToAnalyse)))
		try: gmEmg.append(simulation.get_estimated_emg("GM")[nSamplesToAnalyse:])
		except (ValueError, TypeError) as error: gmEmg.append(np.zeros(abs(nSamplesToAnalyse)))

		# Extract mn spikes
		try: taSpikes.append(simulation.get_mn_spikes_profile("TA")[nSamplesToAnalyse:])
		except (ValueError, TypeError) as error: taSpikes.append(np.zeros(abs(nSamplesToAnalyse)))
		try: gmSpikes.append(simulation.get_mn_spikes_profile("GM")[nSamplesToAnalyse:])
		except (ValueError, TypeError) as error: gmSpikes.append(np.zeros(abs(nSamplesToAnalyse)))

		# plot mn membrane potentials
		title = "%s_amp_%d_Ia_%f_II_%f_Mn_%f"%(args.name,percFiberActEes[0],percFiberActEes[1],percFiberActEes[2],percFiberActEes[3])
		fileName = "%s_amp_%d"%(args.name,eesAmplitude)
		simulation.plot_membrane_potatial(fileName,title)
		simulation.raster_plot(fileName+"_raster_plot")

		# Compute statistics
		taStatTemp.append(np.abs(taEmg[-1]).sum())
		gmStatTemp.append(np.abs(gmEmg[-1]).sum())

		comm.Barrier()


	if rank==0:
		resultsFolder = "../../results/"
		generalFileName = time.strftime("%Y_%m_%d_static_reflex_recording_min"+str(eesStartingAmplitude/args.motorThresholdAmp)+"_max"+str(eesMaxAmplitude/args.motorThresholdAmp)+args.name)

		taStat = np.array(taStatTemp).sum()
		gmStat = np.array(gmStatTemp).sum()
		if not args.noPlot:
			ax[0,2].bar(1, taStat, 0.2)
			ax[1,2].bar(1, gmStat, 0.2)
			ax[0,0].set_ylabel('Flexor')
			ax[0,0].set_title('Mn action potentials')
			ax[0,1].set_title('EMG response')
			ax[0,2].set_title('Statistic')
			ax[1,0].set_ylabel('Extensor')

			fileName = generalFileName+".pdf"
			pp = PdfPages(resultsFolder+fileName)
			pp.savefig(fig)
			pp.close()
			plt.show()

		fileName = generalFileName+".p"
		with open(resultsFolder+fileName, 'w') as pickle_file:
			pickle.dump(taSpikes, pickle_file)
			pickle.dump(taEmg, pickle_file)
			pickle.dump(taStat, pickle_file)
			pickle.dump(gmSpikes, pickle_file)
			pickle.dump(gmEmg, pickle_file)
			pickle.dump(gmStat, pickle_file)


	#comm.Barrier()

	#simulation.run(args.name)

	#memPotName = args.name + "membranePotential"
	#simulation.plot_membrane_potatial(memPotName,memPotName)
	#simulation.raster_plot(memPotName)
	#comm.Barrier()


if __name__ == '__main__':
	main()
