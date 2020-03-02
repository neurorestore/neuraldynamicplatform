from mpi4py import MPI
from neuron import h
from Simulation import Simulation
from cells import AfferentFiber
import random as rnd
import time
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from tools import firings_tools as tlsf
import pickle
from tools import seed_handler as sh
sh.set_seed()

comm = MPI.COMM_WORLD
sizeComm = comm.Get_size()
rank = comm.Get_rank()

class ForwardSimulation(Simulation):
	""" Integration of a NeuralNetwork object over time given an input (ees or afferent input or both). """

	def __init__(self, parallelContext, neuralNetwork, afferentInput=None, eesObject=None, eesModulation=None, tStop = 100):
		""" Object initialization.

		Keyword arguments:
		parallelContext -- Neuron parallelContext object.
		neuralNetwork -- NeuralNetwork object.
		afferentInput -- Dictionary of lists for each type of fiber containing the
			fibers firing rate over time and the dt at wich the firing rate is updated.
			If no afferent input is desired use None (default = None).
		eesObject -- EES object connected to the NeuralNetwork, usefull for some plotting
			info and mandatory for eesModulation (Default = None).
		eesModulation -- possible dictionary with the following strucuture: {'modulation':
			dictionary containing a	signal of 0 and 1s used to activate/inactivate
			the stimulation for every muscle that we want to modulate (the dictionary
			keys have to be the muscle names used in the neural network structure), 'dt':
			modulation dt}. If no modulation of the EES is intended use None (default = None).
		tStop -- Time in ms at wich the simulation will stop (default = 100). In case
			the time is set to -1 the neuralNetwork will be integrated for all the duration
			of the afferentInput.
		"""

		Simulation.__init__(self,parallelContext)
		if rank==1:
			print "\nMPI execution: the cells are divided in the different hosts\n"
		self._nn = neuralNetwork
		self._Iaf = self._nn.get_primary_afferents_names()[0] if self._nn.get_primary_afferents_names() else []
		self._IIf = self._nn.get_secondary_afferents_names()[0] if self._nn.get_secondary_afferents_names() else []
		self._Mn = self._nn.get_motoneurons_names() if self._nn.get_motoneurons_names() else []

		self._set_integration_step(AfferentFiber.get_update_period())

		# Initialization of the afferent modulation
		if afferentInput == None:
			self._afferentModulation = False
			self._afferentInput = None
			if tStop>0: self._set_tstop(tStop)
			else : raise(Exception("If no afferents input are provided tStop has to be greater than 0."))
		else:
			self._afferentModulation = True
			self._afferentInput = afferentInput[0]
			self._dtUpdateAfferent = afferentInput[1]
			self._init_afferents_fr()
			key=[]
			key.append(self._afferentInput.keys()[0])
			key.append(self._afferentInput[key[0]].keys()[0])
			self._inputDuration = len(self._afferentInput[key[0]][key[1]])*self._dtUpdateAfferent
			if tStop == -1 or tStop>= self._inputDuration: self._set_tstop(self._inputDuration-self._dtUpdateAfferent)
			else : self._set_tstop(tStop)

		self._ees = eesObject
		# Initialization of the binary stim modulation
		if eesModulation == None or eesObject == None:
			self._eesBinaryModulation = False
			self._eesProportionalModulation = False
			self._eesParam = {'state':None, 'amp':None, 'modulation':None, 'dt':None}
		elif eesModulation['type']=="binary":
			self._eesBinaryModulation = True
			self._eesProportionalModulation = False
			current, percIf, percIIf, percMn = self._ees.get_amplitude()
			self._eesParam = {'state':{}, 'modulation':eesModulation['modulation'], 'dt':eesModulation['dt']}
			self._eesParam['amp'] = [percIf, percIIf, percMn]
			for muscle in eesModulation['modulation']:
				self._eesParam['state'][muscle] = 1
		elif eesModulation['type']=="proportional":
			self._eesBinaryModulation = False
			self._eesProportionalModulation = True
			self._eesParam = {'modulation':eesModulation['modulation'], 'dt':eesModulation['dt']}
			current, percIf, percIIf, percMn = self._ees.get_amplitude()
			self._eesParam['maxAmp'] = np.array([percIf, percIIf, percMn])

		#Initialization of the result dictionaries
		self._meanFr = None
		self._estimatedEMG = None
		self._nSpikes = None
		self._nActiveCells = None

	"""
	Redefinition of inherited methods
	"""
	def _initialize(self):
		Simulation._initialize(self)
		self._init_aff_fibers()
		self._timeUpdateAfferentsFr = 0
		self._timeUpdateEES = 0

	def _update(self):
		""" Update simulation parameters. """
		comm.Barrier()
		self._nn.update_afferents_ap(h.t)
		if self._afferentModulation:
			if h.t-self._timeUpdateAfferentsFr>= (self._dtUpdateAfferent-0.5*self._get_integration_step()):
				self._timeUpdateAfferentsFr = h.t
				self._set_afferents_fr(int(h.t/self._dtUpdateAfferent))
				self._nn.set_afferents_fr(self._afferentFr)

		if self._eesBinaryModulation:
			if h.t-self._timeUpdateEES>= (self._eesParam['dt']-0.5*self._get_integration_step()):
				ind = int(h.t/self._eesParam['dt'])
				for muscle in self._eesParam['modulation']:
					if self._eesParam['state'][muscle] != self._eesParam['modulation'][muscle][ind]:
						if self._eesParam['state'][muscle] == 0: self._ees.set_amplitude(self._eesParam['amp'],[muscle])
						else: self._ees.set_amplitude([0,0,0],[muscle])
						self._eesParam['state'][muscle] = self._eesParam['modulation'][muscle][ind]

		if self._eesProportionalModulation:
			if h.t-self._timeUpdateEES>= (self._eesParam['dt']-0.5*self._get_integration_step()):
				ind = int(h.t/self._eesParam['dt'])
				for muscle in self._eesParam['modulation']:
					amp = list(self._eesParam['maxAmp']*self._eesParam['modulation'][muscle][ind])
					self._ees.set_amplitude(amp,[muscle])

	def _end_integration(self,result_name):
		""" Print the total simulation time and extract the results. """
		Simulation._end_integration(self)
		self._extract_results(result_name)
		print "It is called"

	"""
	Specific Methods of this class
	"""
	def _init_aff_fibers(self):
		""" Return the percentage of afferent action potentials erased by the stimulation. """
		for muscleName in self._nn.cells:
			for cellName in self._nn.cells[muscleName]:
				if cellName in self._nn.get_afferents_names():
					for fiber in self._nn.cells[muscleName][cellName]:
						fiber.initialise()


	def _init_afferents_fr(self):
		""" Initialize the dictionary necessary to update the afferent fibers. """
		self._afferentFr = {}
		for muscle in self._afferentInput:
			self._afferentFr[muscle]={}
			for cellType in self._afferentInput[muscle]:
				if cellType in self._nn.get_afferents_names():
					self._afferentFr[muscle][cellType]= 0.
				else: raise(Exception("Wrong afferent input structure!"))

	def _set_afferents_fr(self,i):
		""" Set the desired firing rate in the _afferentFr dictionary. """
		for muscle in self._afferentInput:
			for cellType in self._afferentInput[muscle]:
				self._afferentFr[muscle][cellType] = self._afferentInput[muscle][cellType][i]

	def _extract_results(self,result_name,samplingRate = 1000.):
		""" Extract the simulation results. """
		if rank==0: print "Extracting the results... ",
		self._firings = {}
		self._meanFr = {}
		self._estimatedEMG = {}
		self._nSpikes = {}
		self._nActiveCells = {}
		for muscle in self._nn.actionPotentials:
			self._firings[muscle]={}
			self._meanFr[muscle]={}
			self._estimatedEMG[muscle]={}
			self._nSpikes[muscle]={}
			self._nActiveCells[muscle]={}
			for cell in self._nn.actionPotentials[muscle]:
				self._firings[muscle][cell] = tlsf.exctract_firings(self._nn.actionPotentials[muscle][cell],self._get_tstop(),samplingRate)
				if rank==0: self._nActiveCells[muscle][cell] = np.count_nonzero(np.sum(self._firings[muscle][cell],axis=1))
				self._nSpikes[muscle][cell] = np.sum(self._firings[muscle][cell])
				self._meanFr[muscle][cell] = tlsf.compute_mean_firing_rate(self._firings[muscle][cell],samplingRate)
				if cell in self._nn.get_motoneurons_names():
					self._estimatedEMG[muscle][cell] = tlsf.synth_rat_emg(self._firings[muscle][cell],samplingRate)
		if rank==0:
			resultsFolder = "../../results/"
			with open(resultsFolder+result_name + ".p", 'w') as pickle_file:
				pickle.dump(self._firings, pickle_file)
				pickle.dump(self._meanFr, pickle_file)
				pickle.dump(self._estimatedEMG, pickle_file)
				pickle.dump(self._nSpikes, pickle_file)
				pickle.dump(self._nActiveCells, pickle_file)

			fig, ax = plt.subplots(3, 2,figsize=(24,10),sharex='col',sharey='col')

			extMuscle = "GM"
			flexMuscle = "TA"
			ax[0,0].plot(self._meanFr[extMuscle]['Mn'],color='b')
			ax[0,0].set_title('Extensor MN')
			ax[0,1].plot(self._meanFr[flexMuscle]['Mn'],color='b')
			ax[0,1].set_title('Flexor MN')
			ax[1,0].plot(self._meanFr[extMuscle]['IaInt'],color='b')
			ax[1,0].set_title('Extensor IaInt')
			ax[1,1].plot(self._meanFr[flexMuscle]['IaInt'],color='b')
			ax[1,1].set_title('Flexor IaInt')
			ax[2,0].plot(self._meanFr[extMuscle]['RORa'],color='b')
			ax[2,0].set_title('Extensor RORa')
			ax[2,1].plot(self._meanFr[flexMuscle]['RORa'],color='b')
			ax[2,1].set_title('Flexor RORa')

			fileName = time.strftime(result_name+".pdf")
			pp = PdfPages(self._resultsFolder+fileName)
			pp.savefig(fig)
			pp.close()

			print "...completed."

	def get_estimated_emg(self,muscleName):
		emg = [self._estimatedEMG[muscleName][mnName] for mnName in self._Mn]
		emg = np.sum(emg,axis=0)
		return emg

	def get_mn_spikes_profile(self,muscleName):
		spikesProfile = [self._firings[muscleName][mnName] for mnName in self._Mn]
		spikesProfile = np.sum(spikesProfile,axis=0)
		spikesProfile = np.sum(spikesProfile,axis=0)
		return spikesProfile

	def _get_perc_aff_ap_erased(self,muscleName,cellName):
		""" Return the percentage of afferent action potentials erased by the stimulation. """
		if cellName in self._nn.get_afferents_names():
			percErasedAp = []
			meanPercErasedAp = None
			for fiber in self._nn.cells[muscleName][cellName]:
				sent,arrived,collisions,perc = fiber.get_stats()
				percErasedAp.append(perc)
			percErasedAp = comm.gather(percErasedAp,root=0)

			if rank==0:
				percErasedAp = sum(percErasedAp,[])
				meanPercErasedAp = np.array(percErasedAp).mean()

			meanPercErasedAp = comm.bcast(meanPercErasedAp,root=0)
			percErasedAp = comm.bcast(percErasedAp,root=0)
			return meanPercErasedAp,percErasedAp
		else: raise(Exception("The selected cell is not and afferent fiber!"))

	def plot(self,flexorMuscle,extensorMuscle,name="",showFig=True):
		""" Plot and save the simulation results.

		Keyword arguments:
		flexorMuscle -- flexor muscle to plot
		extensorMuscle -- extensor muscle to plot
		name -- string to add at predefined file name of the saved pdf.
		"""
		meanPercErasedApFlexIaf,percErasedApFlexIaf = self._get_perc_aff_ap_erased(flexorMuscle,self._Iaf)
		meanPercErasedApExtIaf,percErasedApExtIaf = self._get_perc_aff_ap_erased(extensorMuscle,self._Iaf)
		meanPercErasedApFlexIIf,percErasedApFlexIIf = self._get_perc_aff_ap_erased(flexorMuscle,self._IIf)
		meanPercErasedApExtIIf,percErasedApExtIIf = self._get_perc_aff_ap_erased(extensorMuscle,self._IIf)
		meanPerEraserApIaf = np.mean([meanPercErasedApFlexIaf,meanPercErasedApExtIaf])
		meanPerEraserApIIf = np.mean([meanPercErasedApFlexIIf,meanPercErasedApExtIIf])

		#should be on rank 0?
		if not self._ees == None:
			percFiberActEes = self._ees.get_amplitude()
			title = 'EES _ {0:.0f}uA _ {1:.0f}Hz _ Delay _ {2:.0f}ms '.format(percFiberActEes[0],self._ees.get_frequency(),\
				self._nn.cells[flexorMuscle][self._Iaf][0].get_delay())
			plt.suptitle(title+"\n Iaf = {0:.0f}%, IIf = {1:.0f}%, Mn = {2:.0f}%, PercErasedApIaf = {3:.0f}%, prasedApIIf = {4:.0f}% ".format(\
				100*percFiberActEes[1],100*percFiberActEes[2],100*percFiberActEes[3],meanPerEraserApIaf,meanPerEraserApIIf))
		else:
			title = ' No EES _ Delay _ {2:.0f} ms '.format(self._nn.cells[flexorMuscle][self._Iaf][0].get_delay())
			plt.suptitle(title+"\n PercErasedApIaf = {3:.0f}%, prasedApIIf = {4:.0f}% ".format(meanPerEraserApIaf,meanPerEraserApIIf))


		if rank == 0:
			if not self._nn.recordMotoneurons and not self._nn.recordMotoneurons:
				raise(Exception("To plot the results it is necessary to have the NeuralNetwork recordMotoneurons and recordAfferents flags set to True"))

			flexIaAfferentModel = self._meanFr[flexorMuscle][self._Iaf]
			flexIIAfferentModel = self._meanFr[flexorMuscle]['IIf']
			flexRAf_footAfferentModel = self._meanFr[flexorMuscle]['II_RAf_foot']
			flexSAIf_footAfferentModel = self._meanFr[flexorMuscle]['II_SAIf_foot']
			flexRAfAfferentModel = self._meanFr[flexorMuscle]['II_RAf']
			flexSAIfAfferentModel = self._meanFr[flexorMuscle]['II_SAIf']

			extIaAfferntModel = self._meanFr[extensorMuscle][self._Iaf]
			extIIAfferntModel = self._meanFr[extensorMuscle]['IIf']
			extRAf_footAfferntModel = self._meanFr[extensorMuscle]['II_RAf_foot']
			extSAIf_footAfferntModel = self._meanFr[extensorMuscle]['II_SAIf_foot']
			extRAfAfferntModel = self._meanFr[extensorMuscle]['II_RAf']
			extSAIfAfferntModel = self._meanFr[extensorMuscle]['II_SAIf']

			flexMnAll = [self._meanFr[flexorMuscle][mnName] for mnName in self._Mn]
			extMnAll = [self._meanFr[extensorMuscle][mnName] for mnName in self._Mn]
			flexMn = np.mean(flexMnAll,axis=0)
			extMn = np.mean(extMnAll,axis=0)

			if self._afferentModulation:
				flexIaAfferentInput = self._afferentInput[flexorMuscle][self._Iaf]
				flexIIAfferentInput = self._afferentInput[flexorMuscle]['IIf']
				flexRAf_footAfferentInput = self._afferentInput[flexorMuscle]['II_RAf_foot']
				flexSAIf_footAfferentInput = self._afferentInput[flexorMuscle]['II_SAIf_foot']
				flexRAfAfferentInput = self._afferentInput[flexorMuscle]['II_RAf']
				flexSAIfAfferentInput = self._afferentInput[flexorMuscle]['II_SAIf']

				extIaAfferentInput = self._afferentInput[extensorMuscle][self._Iaf]
				extIIAfferentInput = self._afferentInput[extensorMuscle]['IIf']
				extRAf_footAfferentInput = self._afferentInput[extensorMuscle]['II_RAf_foot']
				extSAIf_footAfferentInput = self._afferentInput[extensorMuscle]['II_SAIf_foot']
				extRAfAfferentInput = self._afferentInput[extensorMuscle]['II_RAf']
				extSAIfAfferentInput = self._afferentInput[extensorMuscle]['II_SAIf']

			tStop = self._get_tstop()
			info,temp = self._nn.get_mn_info()
			strInfo = []
			for line in info: strInfo.append(" ".join(line))

			fig1, ax1 = plt.subplots(2, 4,figsize=(24,10),sharex='col',sharey='col')
			""" Ia afferents fr subplots """
			ax1[0,0].plot(flexIaAfferentModel,color='b',label='model')
			if self._afferentModulation:
				ax1[0,0].plot(np.arange(0,tStop,self._dtUpdateAfferent),flexIaAfferentInput[:np.ceil(float(tStop)/self._dtUpdateAfferent).astype(int)],color='r',label='input')
			ax1[0,0].set_title('Ia afferents mean firing rate')
			ax1[0,0].legend(loc='upper right')
			ax1[0,0].set_ylabel("Ia firing rate (Hz) - flex")
			ax1[1,0].plot(extIaAfferntModel,color='b',label='model')
			if self._afferentModulation:
				ax1[1,0].plot(np.arange(0,tStop,self._dtUpdateAfferent),extIaAfferentInput[:np.ceil(float(tStop)/self._dtUpdateAfferent).astype(int)],color='r',label='input')
			ax1[1,0].legend(loc='upper right')
			ax1[1,0].set_ylabel("Ia firing rate (Hz) - ext")
			ax1[1,0].set_xlabel("time (ms)")

			""" afferents percAperased subplots """
			ax1[0,1].hist(percErasedApFlexIaf, bins=range(0,101,2), facecolor='green', alpha=0.75)
			ax1[0,1].set_title("Histogram of the Ap perc erased in Iaf")
			ax1[0,1].set_ylabel("Frquency - flex")
			ax1[0,1].axis([0, 100, 0, 60])
			ax1[1,1].hist(percErasedApExtIaf, bins=range(0,101,2), facecolor='green', alpha=0.75)
			ax1[1,1].set_ylabel("Frquency - ext")
			ax1[1,1].set_xlabel("Percentage %")
			ax1[1,1].axis([0, 100, 0, 60])

			""" Motoneurons subplots """
			ax1[0,2].plot(flexMn)
			ax1[0,2].set_title('Motoneurons mean firing rate')
			ax1[0,2].set_ylabel("Mn firing rate (Hz) - flex")
			ax1[1,2].plot(extMn)
			ax1[1,2].set_ylabel("Mn firing rate (Hz) - ext")
			ax1[1,2].set_xlabel("time (ms)")

			""" EMG plot """
			ax1[0,3].plot(self.get_estimated_emg(flexorMuscle),color='b',label='model')
			ax1[0,3].set_ylabel("amplutide (a.u.) - flex")
			ax1[0,3].set_xlabel("time (ms)")
			ax1[0,3].set_title('Estimated EMG')
			ax1[1,3].plot(self.get_estimated_emg(extensorMuscle),color='b',label='model')
			ax1[1,3].set_ylabel("amplutide (a.u.) - ext")
			ax1[1,3].set_xlabel("time (ms)")

			title = title.replace(" ","")
			if showFig:	plt.show()

			fig2, ax2 = plt.subplots(2, 5,figsize=(24,10),sharex='col',sharey='col')
			""" II afferents fr subplots """
			ax2[0,0].plot(flexIIAfferentModel,color='b',label='model')
			if self._afferentModulation:
				ax2[0,0].plot(np.arange(0,tStop,self._dtUpdateAfferent),flexIIAfferentInput[:np.ceil(float(tStop)/self._dtUpdateAfferent).astype(int)],color='r',label='input')
			ax2[0,0].set_title('II afferents mean firing rate')
			ax2[0,0].legend(loc='upper right')
			ax2[0,0].set_ylabel("II firing rate (Hz) - flex")
			ax2[1,0].plot(extIIAfferntModel,color='b',label='model')
			if self._afferentModulation:
				ax2[1,0].plot(np.arange(0,tStop,self._dtUpdateAfferent),extIIAfferentInput[:np.ceil(float(tStop)/self._dtUpdateAfferent).astype(int)],color='r',label='input')
			ax2[1,0].legend(loc='upper right')
			ax2[1,0].set_ylabel("II firing rate (Hz) - ext")
			ax2[1,0].set_xlabel("time (ms)")

			""" Cutaneous RA afferents fr subplots """
			#ax2[0,1].plot(flexRAfAfferentModel,color='b',label='model')
			#if self._afferentModulation:
			#	ax2[0,1].plot(np.arange(0,tStop,self._dtUpdateAfferent),flexRAfAfferentInput[:np.ceil(float(tStop)/self._dtUpdateAfferent).astype(int)],color='r',label='input')
			#ax2[0,1].set_title('RA afferents mean firing rate')
			#ax2[0,1].legend(loc='upper right')
			#ax2[0,1].set_ylabel("RA firing rate (Hz) - flex")
			#ax2[1,1].plot(extRAfAfferntModel,color='b',label='model')
			#if self._afferentModulation:
			#	ax2[1,1].plot(np.arange(0,tStop,self._dtUpdateAfferent),extRAfAfferentInput[:np.ceil(float(tStop)/self._dtUpdateAfferent).astype(int)],color='r',label='input')
			#ax2[1,1].legend(loc='upper right')
			#ax2[1,1].set_ylabel("RA firing rate (Hz) - ext")
			#ax2[1,1].set_xlabel("time (ms)")

			ax2[0,1].plot(flexRAfAfferentModel,color='b',label='model')
			if self._afferentModulation:
				ax2[0,1].plot(np.arange(0,tStop,self._dtUpdateAfferent),flexRAfAfferentInput[:np.ceil(float(tStop)/self._dtUpdateAfferent).astype(int)],color='r',label='input')
			ax2[0,1].set_title('RA afferents mean firing rate')
			ax2[0,1].legend(loc='upper right')
			ax2[0,1].set_ylabel("RA firing rate (Hz) - flex")
			ax2[1,1].plot(extRAfAfferntModel,color='b',label='model')
			if self._afferentModulation:
				ax2[1,1].plot(np.arange(0,tStop,self._dtUpdateAfferent),extRAfAfferentInput[:np.ceil(float(tStop)/self._dtUpdateAfferent).astype(int)],color='r',label='input')
			ax2[1,1].legend(loc='upper right')
			ax2[1,1].set_ylabel("RA firing rate (Hz) - ext")
			ax2[1,1].set_xlabel("time (ms)")

			""" Cutaneous RA foot afferents fr subplots """
			ax2[0,2].plot(flexRAf_footAfferentModel,color='b',label='model')
			if self._afferentModulation:
				ax2[0,2].plot(np.arange(0,tStop,self._dtUpdateAfferent),flexRAf_footAfferentInput[:np.ceil(float(tStop)/self._dtUpdateAfferent).astype(int)],color='r',label='input')
			ax2[0,2].set_title('RA foot afferents mean firing rate')
			ax2[0,2].legend(loc='upper right')
			ax2[0,2].set_ylabel("RA foot firing rate (Hz) - flex")
			ax2[1,2].plot(extRAf_footAfferntModel,color='b',label='model')
			if self._afferentModulation:
				ax2[1,2].plot(np.arange(0,tStop,self._dtUpdateAfferent),extRAf_footAfferentInput[:np.ceil(float(tStop)/self._dtUpdateAfferent).astype(int)],color='r',label='input')
			ax2[1,2].legend(loc='upper right')
			ax2[1,2].set_ylabel("RA foot firing rate (Hz) - ext")
			ax2[1,2].set_xlabel("time (ms)")

			""" Cutaneous SAI afferents fr subplots """
			ax2[0,3].plot(flexSAIfAfferentModel,color='b',label='model')
			if self._afferentModulation:
				ax2[0,3].plot(np.arange(0,tStop,self._dtUpdateAfferent),flexSAIfAfferentInput[:np.ceil(float(tStop)/self._dtUpdateAfferent).astype(int)],color='r',label='input')
			ax2[0,3].set_title('SAI afferents mean firing rate')
			ax2[0,3].legend(loc='upper right')
			ax2[0,3].set_ylabel("SAI firing rate (Hz) - flex")
			ax2[1,3].plot(extSAIfAfferntModel,color='b',label='model')
			if self._afferentModulation:
				ax2[1,3].plot(np.arange(0,tStop,self._dtUpdateAfferent),extSAIfAfferentInput[:np.ceil(float(tStop)/self._dtUpdateAfferent).astype(int)],color='r',label='input')
			ax2[1,3].legend(loc='upper right')
			ax2[1,3].set_ylabel("SAI firing rate (Hz) - ext")
			ax2[1,3].set_xlabel("time (ms)")

			""" Cutaneous SAI foot afferents fr subplots """
			ax2[0,4].plot(flexSAIf_footAfferentModel,color='b',label='model')
			if self._afferentModulation:
				ax2[0,4].plot(np.arange(0,tStop,self._dtUpdateAfferent),flexSAIf_footAfferentInput[:np.ceil(float(tStop)/self._dtUpdateAfferent).astype(int)],color='r',label='input')
			ax2[0,4].set_title('SAI foot afferents mean firing rate')
			ax2[0,4].legend(loc='upper right')
			ax2[0,4].set_ylabel("SAI foot firing rate (Hz) - flex")
			ax2[1,4].plot(extSAIf_footAfferntModel,color='b',label='model')
			if self._afferentModulation:
				ax2[1,4].plot(np.arange(0,tStop,self._dtUpdateAfferent),extSAIf_footAfferentInput[:np.ceil(float(tStop)/self._dtUpdateAfferent).astype(int)],color='r',label='input')
			ax2[1,4].legend(loc='upper right')
			ax2[1,4].set_ylabel("SAI foot firing rate (Hz) - ext")
			ax2[1,4].set_xlabel("time (ms)")

			fig3 = plt.figure()
			ax3 = fig3.add_subplot(111)
			ax3.text(0.5, 0.5,"\n".join(strInfo), horizontalalignment='center',verticalalignment='center',transform=ax3.transAxes)
			ax3.xaxis.set_visible(False)
			ax3.yaxis.set_visible(False)





			fileName = time.strftime("%Y_%m_%d_FS_"+title+name+".pdf")
			pp = PdfPages(self._resultsFolder+fileName)
			pp.savefig(fig1)
			pp.savefig(fig2)
			pp.savefig(fig3)
			pp.close()
