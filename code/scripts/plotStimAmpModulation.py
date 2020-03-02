import sys
sys.path.append('../code')

import matplotlib.pyplot as plt
import numpy as np
import pickle
from neuron import h

from tools import structures_tools as tls
from NeuralNetwork import NeuralNetwork
from EES import EES

def main():
	templateFile = "templateFrwSimHumanSOL.txt"
	w1 = 0.0210
	w2 = 0.0364
	w3 = 0.0165
	w4 = 0.0219
	delay = 16
	inputFileName = "ffs_d_"+str(delay)+"_w1_"+str(w1)+"_w2_"+str(w2)+"_w3_"+str(w3)+"_w4_"+str(w4)
	inputFile = "generatedStructures/"+inputFileName+".txt"
	tls.modify_network_structure(templateFile,inputFile,delay,[w1,w2,w3,w4])

	eesAmplitudes = ["235","242","250","259","270","282"]
	fileStimMod = "generateForSimInputs/output/spatiotemporalProportionalStimulationHumanSensoryBased_fromFloatDataForHumData.p"
	with open(fileStimMod, 'r') as pickle_file:
		eesModulation = pickle.load(pickle_file)
	pc = h.ParallelContext()
	nn=NeuralNetwork(pc,inputFile)
	ees = EES(pc,nn,1,1,pulsesNumber=100000,species="human")


	fig, ax = plt.subplots(2,2,figsize=(16,9))
	cmap = plt.get_cmap('autumn')
	colors = cmap(np.linspace(0.1,0.9,len(eesAmplitudes)))


	for i,eesAmplitude in enumerate(eesAmplitudes):

		ees.set_amplitude(int(eesAmplitude))
		current, percIf, percIIf, percMn = ees.get_amplitude()
		tonicStim = percIf*np.ones(eesModulation["modulation"]["SOL"].shape)
		spatioStimExt = percIf*eesModulation["modulation"]["SOL"]
		spatioStimFlex = percIf*eesModulation["modulation"]["TA"]

		ax[0,0].plot(spatioStimFlex,color=colors[i])
		ax[1,0].plot(spatioStimExt,color=colors[i])
		ax[0,1].plot(tonicStim,color=colors[i])
		ax[1,1].plot(tonicStim,color=colors[i])

	plt.show()

if __name__ == '__main__':
	main()
