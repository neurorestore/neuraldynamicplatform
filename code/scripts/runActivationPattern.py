import argparse
import time
import sys
sys.path.append('../code')
from mpi4py import MPI
from neuron import h
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.backends.backend_pdf import PdfPages
import pickle
from tools import general_tools  as gt
from tools import seed_handler as sh
from tools import load_data_tools as ldt
from parameters import RatParameters as rp

comm = MPI.COMM_WORLD
sizeComm = comm.Get_size()
rank = comm.Get_rank()

def main():
	""" This program launches a ForwardSimulation simulation with a predefined NeuralNetwork structure,
	different stimulation amplitudes are tested to evealuate the muslce recruitment curve.
	The plots resulting from this simulation are saved in the results folder.

	This program can be executed both with and without MPI. In case MPI is used the cells
	of the NeuralNetwork are shared between the different hosts in order to speed up the
	simulation.
	"""

	# Import simulation specific modules
	from simulations import ForwardSimulationActivationPattern
	from NeuralNetwork import NeuralNetwork
	from EESActivationPattern import EES

	ActivationFile = "../ActivationPattern/heatMap_design_Medtronic_Elec_contact_1.txt"
	ActivationPattern = np.loadtxt(ActivationFile, delimiter=',')
	# Initialize parameters
	newPattern = ActivationPattern[1:]

	for idx_root,val_root in enumerate(newPattern):
		for
"""

	eesFrequency = 10
	simTime = 250 #250
	plotResults = True


	# Create a Neuron ParallelContext object to support parallel simulations

	pc = h.ParallelContext()
	nn=NeuralNetwork(pc,args.inputFile)
	eesAmplitude = args.eesAmplitude
	ees = EES(pc,nn,eesAmplitude,eesFrequency,pulsesNumber=100000,species='rat')
	ees.get_amplitude(True)
	muscles = rp.get_muscles_dict()
	bs = BaselineActivity(pc,nn,rp.get_interneurons_baseline_fr())
	afferentsInput = ldt.load_afferent_input('rat',muscles,"static")

	afferentsInput = None
	eesModulation = None

	if args.membranePotential:
		cellsToRecord = {"MnGM":nn.cells['GM']['Mn'],\
						 "MnTA":nn.cells['TA']['Mn']}
		modelTypes = {"MnGM":"artificial","MnTA":"artificial"}
		simulation = ForSimSpinalModulation(pc,nn,cellsToRecord,modelTypes, afferentsInput, ees, eesModulation, simTime)
		membranePotentials = []
	else: simulation = ForwardSimulation(pc,nn, afferentsInput, ees, eesModulation, simTime)

	taEmg = []
	taSpikes = []
	taStatTemp = []
	gmEmg = []
	gmSpikes = []
	gmStatTemp = []
	nSamplesToAnalyse = -250 # last 100 samples

	if not args.noPlot: fig, ax = plt.subplots(2, 3,figsize=(16,9),sharex='col',sharey='col')


	ees.set_amplitude(eesAmplitude)
	percFiberActEes = ees.get_amplitude(True)
	simulation.run()
	showFig = False
	PlotName = args.name + str(eesAmplitude)
	simulation.plot("TA","GM",PlotName,showFig)
	#simulation.plot("TA","Mn",PlotName)

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
	if args.membranePotential:
		title = "%s_amp_%d_Ia_%f_II_%f_Mn_%f"%(args.name,percFiberActEes[0],percFiberActEes[1],percFiberActEes[2],percFiberActEes[3])
		fileName = "%s_amp_%d"%(args.name,eesAmplitude)
		simulation.plot_membrane_potatial(fileName,title)

	# Compute statistics
	taStatTemp.append(np.abs(taEmg[-1]).sum())
	gmStatTemp.append(np.abs(gmEmg[-1]).sum())

	if rank==0 and not args.noPlot:
		ax[0,1].plot(taEmg[-1])
		ax[0,0].plot(taSpikes[-1])
		ax[1,1].plot(gmEmg[-1])
		ax[1,0].plot(gmSpikes[-1])
	comm.Barrier()

	if rank==0:
		resultsFolder = "../../results/"
		generalFileName = time.strftime("%Y_%m_%d_static_reflex_recording_"+str(eesAmplitude)+args.name)
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

	comm.Barrier()
"""

if __name__ == '__main__':
	main()
