from mpi4py import MPI
from neuron import h
from ForSimMuscleSpindles import ForSimMuscleSpindles
from cells import AfferentFiber
import random as rnd
import time as timeMod
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from tools import firings_tools as tlsf
from tools import general_tools as gt
import pickle
from tools import seed_handler as sh
sh.set_seed()

comm = MPI.COMM_WORLD
sizeComm = comm.Get_size()
rank = comm.Get_rank()

class ForSimMuscleSpindlesCybex(ForSimMuscleSpindles):
	""" Integration of a NeuralNetwork object of two antagonist muscles over time given an input.
		EMG and afferent firing rates are the results extracted at the end of simulation.
	"""

	def __init__(self, parallelContext, neuralNetwork, afferentInput, eesObject, tStop, ankleKinematic):
		""" Object initialization. """
		eesModulation = None
		ForSimMuscleSpindles.__init__(self,parallelContext,neuralNetwork,afferentInput,eesObject,eesModulation,tStop)
		self._samplingRate = 1000.
		if rank == 0:
			self._ankleKinematic = ankleKinematic
			ratio = (1000./self._samplingRate/(1000*self._ankleKinematic['dt']))
			gt.resample(self._ankleKinematic,['time','kinematic'],ratio)
			self._ankleKinematic['dt'] = 1./self._samplingRate
			self.nBins = 10
		self._samplingRate = comm.bcast(self._samplingRate,root=0)


	def _extract_results(self):
		ForSimMuscleSpindles._extract_results(self,self._samplingRate)
		if rank == 0:
			self.mnActivity = {}
			for muscle in self._firings:
				self.mnActivity[muscle] = np.sum(self._firings[muscle]['Mn'],axis=0)
			stimPulsesTime,stimPulses = self._ees.get_pulses(self._get_tstop(),self._samplingRate)
			self._stimPulsesIndexes = np.where(stimPulses)[0]
			self._extract_muscle_responses()
			self._compute_muscle_responses()

	def save_results(self,name=""):
		""" Save the resulting muscle responses.

		Keyword arguments:
		name -- string to add at predefined file name of the saved pdf (default = "").
		"""

		if rank == 0:
			stimInfo = "%dHz_%duA"%(self._ees.get_frequency(),self._ees.get_amplitude()[0])
			fileName = timeMod.strftime("%Y_%m_%d_CybexMuscleResponses_"+stimInfo+name+".p")
			with open(self._resultsFolder+fileName, 'w') as pickle_file:
				pickle.dump(self.muscleResponsesStimPulse, pickle_file)
				pickle.dump(self.kinBins, pickle_file)

	def plot(self,name="",showFig=False):
		""" Plot and save the simulation results."""
		if rank==0:
			nMuscles = len(self._nn.cells.keys())
			index = np.arange(self.nBins)
			bar_width = 0.35
			opacity = 1
			kinColors = ["#2C3E50","#E74C3C"]*int(round(self.nBins/2.))
			error_config = {'ecolor': '0.3'}
			figSize = 0.7
			fig, ax = plt.subplots(nMuscles+1,1, figsize=(16*figSize,9*figSize),facecolor='#ECF0F1')
			fig.suptitle("Muscle responses")

			dataToPlot = self.muscleResponsesStimPulse
			for j,muscle in enumerate(self._nn.cells):
				ax[j].bar(index, dataToPlot[muscle]["mean"], bar_width,
								 alpha=opacity,
								 color='#2C3E50',
								 yerr=dataToPlot[muscle]["std"],
								 error_kw=error_config,
								 ecolor = '#E74C3C',
								 align='center')

				for dataBin in index:
					ax[j].scatter([dataBin]*len(dataToPlot[muscle]["values"][dataBin])\
						,dataToPlot[muscle]["values"][dataBin]\
						,zorder=10, color='#2980B9',s=3,edgecolor='none')

				ax[j].set_facecolor('#ECF0F1')
				ax[j].xaxis.set_ticks([])
				ax[j].yaxis.set_ticks([])
				if j==0: ax[j].set_title("f: %d Hz\na: %d perc Ia %d perc II"\
					%(self._ees.get_frequency(),100*self._ees.get_amplitude()[1],100*self._ees.get_amplitude()[2]))
				ax[j].set_ylabel(muscle)

			# Plot kinematics
			offset = 0
			for k in xrange(self.nBins):
				for z,kinData in enumerate(self.kinBins[k]):
					time = range(offset,offset+len(kinData))
					ax[-1].plot(time,kinData,color=kinColors[k])
				ax[-1].set_facecolor('#ECF0F1')
				ax[-1].xaxis.set_ticks([])
				ax[-1].yaxis.set_ticks([])
				offset += len(self.kinBins[k][0])
			ax[-1].set_ylabel("Kinematics")

			stimInfo = "%dHz_%duA"%(self._ees.get_frequency(),self._ees.get_amplitude()[0])
			fileName = timeMod.strftime("%Y_%m_%d_CybexMuscleResponses_"+stimInfo+name+".pdf")
			plt.savefig(self._resultsFolder+fileName, format="pdf",transparent=True)
			plt.show(block=showFig)

	def plot_overall_activity(self,flexorMuscle,extensorMuscle,name="",showFig=True):
		ForSimMuscleSpindles.plot(self,flexorMuscle,extensorMuscle,name,showFig)

	def _extract_muscle_responses(self):
		if rank == 0:
			timeAfterPulse = 4
			timeBeforePulse = 1
			dt = 1
			samplesAfterPulse = int(timeAfterPulse/dt) #ms
			samplesBeforePulse = int(timeBeforePulse/dt) #ms

			#Extract cycles start time
			startCycleIndexesTemp = np.where(self._ankleKinematic['kinematic']>self._ankleKinematic['kinematic'].mean()+self._ankleKinematic['kinematic'].std())
			startCycleTemp = np.zeros(self._ankleKinematic['kinematic'].size)
			startCycleTemp[startCycleIndexesTemp] = 1
			startCycleIndexes = np.where(np.diff(startCycleTemp)>0.5)
			startCycleIndexes = startCycleIndexes[0]
			startCycleTime = startCycleIndexes*self._ankleKinematic['dt']

			# plt.plot(self._ankleKinematic['time'],self._ankleKinematic['kinematic'])
			# plt.plot(startCycleTime,np.ones(startCycleIndexes.size),'x')
			# plt.show()

			#Create kin bins
			self.kinBins = [[] for i in xrange(self.nBins)]
			for i in xrange(startCycleIndexes.size-1):
				kinCycle = self._ankleKinematic['kinematic'][startCycleIndexes[i]:startCycleIndexes[i+1]]
				for k,kinBin in enumerate(np.array_split(kinCycle,self.nBins)):
					self.kinBins[k].append(kinBin)
			# check boundary conditions
			if self._stimPulsesIndexes[0]<samplesBeforePulse:
				self._stimPulsesIndexes[0]=samplesBeforePulse
			if self._stimPulsesIndexes[-1]>self._ankleKinematic['kinematic'].size-samplesAfterPulse:
				self._stimPulsesIndexes[-1]=self._ankleKinematic['kinematic'].size-samplesAfterPulse
			# Extract mn activity
			self.dataBinsStimPulse = {}
			for muscle in self._nn.cells:
				self.dataBinsStimPulse[muscle] = [[] for i in xrange(self.nBins)]
				# data bin extraction
				for i in xrange(startCycleIndexes.size-1):
					indexesCycle = np.arange(startCycleIndexes[i],startCycleIndexes[i+1])
					for k,indexesBin in enumerate(np.array_split(indexesCycle,self.nBins)):
						# Find the stim pulses inside the bin
						stimPulsesBin = self._stimPulsesIndexes[np.in1d(self._stimPulsesIndexes,indexesBin)]
						for stimPulseBin in stimPulsesBin:
							self.dataBinsStimPulse[muscle][k].append(\
								sum(self.mnActivity[muscle][stimPulseBin-samplesBeforePulse:stimPulseBin+samplesAfterPulse]))

	def _compute_muscle_responses(self):
		self.muscleResponsesStimPulse = {}
		for muscle in self._nn.cells:
			self.muscleResponsesStimPulse[muscle] = {
				"mean":[],
				"std":[],
				"values":[]}
			for dataBin in self.dataBinsStimPulse[muscle]:
				self.muscleResponsesStimPulse[muscle]["mean"].append(np.mean(dataBin))
				self.muscleResponsesStimPulse[muscle]["std"].append(np.std(dataBin))
				self.muscleResponsesStimPulse[muscle]["values"].append(dataBin)

	def get_muscle_responses(self):
		return self.muscleResponsesStimPulse
