from mpi4py import MPI
from neuron import h
from Simulation import Simulation
from cells import AfferentFiber
import random as rnd
import time
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
import pickle
from scipy.optimize import fminbound
from tools import firings_tools as tlsf
from tools import seed_handler as sh
sh.set_seed()

comm = MPI.COMM_WORLD
sizeComm = comm.Get_size()
rank = comm.Get_rank()

class IsoModulationCurves(Simulation):
	""" Simulation to estimate the frequency/amplitude isomodulation curves
	"""

	def __init__(self,parallelContext,modulations,fiberDelay,toTime,firingRateProfile,dtAfferentProfile):
		""" Object initialization.

		Keyword arguments:
		parallelContext -- Neuron parallelContext object.
		modulations -- list of afferent modulations to test.
		fiberDelay -- afferent fiber delay.
		totTime -- simulation time.
		firingRateProfile -- profile of the afferent fibers firing rate during gait.
		dtAfferentProfile -- dt of the profile
		"""

		if rank==1:
			print "\nMPI execution: the fibers are splitted between the different processes"

		Simulation.__init__(self,parallelContext)

		for i in xrange(sizeComm):
			if i%sizeComm==rank: rnd.seed(time.time())

		# Variables initializations
		self._modulations = modulations
		self._fiberDelay = fiberDelay
		self._firingRateProfile = firingRateProfile
		self._meanFiringRateProfile = np.mean(self._firingRateProfile)
		self._dtUpdateAfferent = dtAfferentProfile
		self._percsIaf = np.arange(0.025,1.025,0.025)

		self._create_fibers()
		self._create_stim()
		self._connect_stim_to_fibers()

		self._totTime = toTime
		self._set_tstop(self._totTime)
		self._set_integration_step(AfferentFiber.get_update_period())
		self._set_print_period(toTime)

	"""
	Redefinition of inherited methods
	"""
	def run(self):
		""" Here we redifine the run method of the Simulation class.
			By running this method we will compute the isomodulation curve.
			For every stimulation amplitude we search the stimulation frequency
			necessary to modulate the affarent fiber of the given modulation.
			At every step a minimization problem is performed by running the
			Simulation.run method.
		"""

		self._requiredFreq = []
		self._percErasedAp = []
		self._meanFr = []
		maxError = 1
		nSim = len(self._modulations)*len(self._percsIaf)
		count = 0

		# Compute the mean firing rate profile without stimulation
		if rank==0:print "\t\t\t Control"
		self._activate_connections(0)
		if rank==0: self._stim.interval = 99999999.
		Simulation.run(self)
		self._meanFiringRateProfile = self._meanFibersFr
		if rank==0: print "The mean afferent firing rate withouth stimulation is: %f"%(self._meanFiringRateProfile)
		_firings = tlsf.exctract_firings(self._actionPotentials,self._get_tstop(),samplingRate=1000.)
		self._meanFr.append(tlsf.compute_mean_firing_rate(_firings,samplingRate=1000.))

		# Compute the isomodulation curves
		for modulation in self._modulations:
			if rank==0:print "\t\t\t Modulation: +"+str(modulation)+" Hz"
			self._requiredFreq.append([])
			self._percErasedAp.append([])
			self._meanFr.append([])
			for percIaf in self._percsIaf:
				self._activate_connections(percIaf)
				firstGuess = float(modulation)/percIaf
				stimFreq,error = self._minimize(firstGuess,maxError,modulation)
				self._requiredFreq[-1].append(stimFreq)
				self._percErasedAp[-1].append(self._meanPercErasedAp)
				_firings = tlsf.exctract_firings(self._actionPotentials,self._get_tstop(),samplingRate=1000.)
				self._meanFr[-1].append(tlsf.compute_mean_firing_rate(_firings,samplingRate=1000.))

				if rank==0:print "\t\t Amplitude: "+str(percIaf)+" %Iaf  --- Frequency: "+str(stimFreq)+" Hz --- Error: "+str(error)
				count += 1
			if rank==0: print "\t\t\t\t", str(count/nSim*100)," % of simulations performed."

		self._requiredFreq = np.array(self._requiredFreq)
		self._percErasedAp = np.array(self._percErasedAp)
		if rank==0:
			fileName = time.strftime("%Y_%m_%d_IsoModulationCurves_Delay_"+str(self._fiberDelay)+".p")
			with open(self._resultsFolder+fileName, 'w') as pickle_file:
				pickle.dump(self._requiredFreq, pickle_file)
				pickle.dump(self._percErasedAp, pickle_file)
				pickle.dump(self._percsIaf, pickle_file)
				pickle.dump(self._meanFr, pickle_file)


	def _initialize(self):
		Simulation._initialize(self)
		self._timeUpdateAfferentsFr = 0
		self._initialise_fibers()

	def _update(self):
		""" Update simulation parameters. """
		self._update_fibers()
		if h.t-self._timeUpdateAfferentsFr >= (self._dtUpdateAfferent-0.5*self._get_integration_step()):
			self._timeUpdateAfferentsFr = h.t
			for fiber in self._fibers:
				fiber.set_firing_rate(self._firingRateProfile[int(h.t/self._dtUpdateAfferent)])

	def _end_integration(self):
		""" Print the total simulation time and extract the results. """
		Simulation._end_integration(self)
		self._extract_results()

	def save_results(self,name=""):
		""" Save the Simulation results."""
		pass # we don't need to save the results of every single Simulation.run

	def plot(self):
		""" Plot the isomodulation curves.
		"""
		if rank == 0:
			fig, ax1 = plt.subplots(figsize=(16,9))
			ax2 = ax1.twinx()
			cmap = plt.get_cmap('winter')
			colors_f = cmap(np.linspace(0.1,0.9,len(self._modulations)))
			cmap = plt.get_cmap('autumn')
			colors_p = cmap(np.linspace(0.1,0.9,len(self._modulations)))

			for i,modulation in enumerate(self._modulations):
				ax1.plot(self._percsIaf,self._requiredFreq[i,:],color=colors_f[i],label="+{0:.0f} Hz".format(modulation))
				ax2.plot(self._percsIaf,self._percErasedAp[i,:],'-.',color=colors_p[i])

			ax1.legend(loc='upper right')
			ax2.set_ylim([0,100])
			ax1.set_ylim([0,1000])
			fileName = time.strftime("%Y_%m_%d_IsoModulationCurves_Delay_"+str(self._fiberDelay)+".pdf")
			plt.savefig(self._resultsFolder+fileName, format="pdf",transparent=True)
			plt.show(block=False)

	def plot_afferent_modulation(self,percIafList,fileName=None):
		if fileName:
			with open(self._resultsFolder+fileName, 'r') as pickle_file:
				self._requiredFreq = pickle.load(pickle_file)
				self._percErasedAp = pickle.load(pickle_file)
				self._percsIaf = pickle.load(pickle_file)
				self._meanFr = pickle.load(pickle_file)
		if rank == 0:
			fig, ax = plt.subplots(len(percIafList),2,figsize=(16,9))
			if len(percIafList)==1: ax = [ax]

			modulations = np.insert(self._modulations,0,0)
			cmap = plt.get_cmap('winter')
			colors = cmap(np.linspace(0.1,0.9,len(modulations)))

			for j,percIaf in enumerate(percIafList):
				ampInd = np.argmin(np.abs(self._percsIaf - percIaf))
				for i,modulation in enumerate(modulations):
					if i==0:
						ax[j][0].plot(self._meanFr[i],color='k',label="%d Hz"%(0))
						#compute th emodulation depth
						temp = np.array(self._meanFr[i])
						limit = temp.size/10
						modulationDepth = temp[limit:-limit].max()-temp[limit:-limit].min()
						ax[j][1].bar(modulation,modulationDepth,5,color='k',label="%d Hz"%(0))

					else:
						ax[j][0].plot(self._meanFr[i][ampInd],color=colors[i],label="%d Hz"%(self._requiredFreq[i-1][ampInd]))
						#compute th emodulation depth
						temp = np.array(self._meanFr[i][ampInd])
						limit = temp.size/10
						modulationDepth = temp[limit:-limit].max()-temp[limit:-limit].min()
						ax[j][1].bar(modulation,modulationDepth,5,color=colors[i],label="%d Hz"%(self._requiredFreq[i-1][ampInd]))

				ax[j][0].legend(loc='upper right')
				ax[j][1].legend(loc='upper right')
				ax[j][0].set_title('%d perc - recruited fibers'%(percIaf*100))
				ax[j][1].set_title('Modulation depth')

			fileName = time.strftime("%Y_%m_%d_IsoMod_Profiles_Delay_"+str(self._fiberDelay)+".pdf")
			plt.savefig(self._resultsFolder+fileName, format="pdf",transparent=True)
			plt.show(block=False)


	"""
	Specific Methods of this class
	"""
	def _create_fibers(self):
		""" Create the fibers and records the APs. """
		self._nFibers = 100
		self._fibers = []
		self._fibersNcList = []
		self._actionPotentials = []
		self.cellsId = []
		cellId = 0
		for i in xrange(self._nFibers):
			if i%sizeComm==rank:
				# Assign a cellId to the new cell
				self.cellsId.append(cellId)
				# Tell this host it has this cellId
				self._pc.set_gid2node(cellId, rank)
				# Create the cell
				self._fibers.append(AfferentFiber(self._fiberDelay))
				# Associate the cell with this host and id, the nc is also necessary to use this cell as a source for all other hosts
				self._fibersNcList.append(self._fibers[-1].connect_to_target(None))
				self._pc.cell(cellId, self._fibersNcList[-1])

				self._actionPotentials.append(h.Vector())
				self._fibersNcList[-1].record(self._actionPotentials[-1])
			cellId+=1

	def _create_stim(self):
		""" Create the NetStim object. """
		self._stimId = 100000
		if rank==0:
			self._stim = h.NetStim()
			self._pc.set_gid2node(self._stimId, rank)
			self._stim.interval = 1
			self._stim.number = 100000
			self._stim.start = 5
			self._stim.noise = 0
			# Associate the cell with this host and id
			# the nc is also necessary to use this cell as a source for all other hosts
			nc = h.NetCon(self._stim,None)
			self._pc.cell(self._stimId, nc)

	def _connect_stim_to_fibers(self):
		""" Connect fibers ojects to ees objects to make the stimulation activate these fibers. """
		self._netconList = []
		for targetId in self.cellsId:
			# check whether this id is associated with a cell in this host - useless..
			if not self._pc.gid_exists(targetId): continue
			target = self._pc.gid2cell(targetId)
			self._netconList.append(self._pc.gid_connect(self._stimId,target))
			self._netconList[-1].delay = rnd.randint(1,50) #Note that this delay is not functioal but only usefull for statistical reasons
			self._netconList[-1].weight[0] = AfferentFiber.get_ees_weight()
			self._netconList[-1].active(False)

	def _activate_connections(self,percIaf):
		for nc in self._netconList: nc.active(False)
		count = 0
		for i in xrange(int(percIaf*self._nFibers)):
			if i%sizeComm==rank:
				self._netconList[count].active(True)
				count += 1

	def _initialise_fibers(self):
		""" Initialise fiber state. """
		for fiber in self._fibers: fiber.initialise()

	def _update_fibers(self):
		""" Update the afferents fiber state. """
		for fiber in self._fibers: fiber.update(h.t)

	def _extract_results(self):
		""" Extract the simulation results.
			This function is called by Simulation.run
		"""
		fibersFr = [1000.*fiberAPs.size()/self._totTime for fiberAPs in self._actionPotentials]
		self._meanFibersFr = np.mean(fibersFr)
		self._meanFibersFr = comm.gather(self._meanFibersFr, root=0)
		if rank==0: self._meanFibersFr = np.mean(self._meanFibersFr)
		self._meanFibersFr = comm.bcast(self._meanFibersFr, root=0)
		percErasedAp = []
		for fiber in self._fibers:
			sent,arr,coll,perc=fiber.get_stats()
			percErasedAp.append(perc)
		self._meanPercErasedAp = np.mean(percErasedAp)
		self._meanPercErasedAp = comm.gather(self._meanPercErasedAp, root=0)
		if rank==0: self._meanPercErasedAp = np.mean(self._meanPercErasedAp)
		self._meanPercErasedAp = comm.bcast(self._meanPercErasedAp, root=0)

	def _minimize(self,startingFreq,maxError,targetModulation):
		error = 1000
		step = 0.02*startingFreq
		stimFreq = startingFreq -step*(error/abs(error))
		while abs(error)>maxError:
			stimFreq += step*(error/abs(error))
			if stimFreq>AfferentFiber.get_max_ees_frequency():
				error = None
				stimFreq = 1111
				self._meanPercErasedAp = None
				break
			error = self._estimate_modulation_error(stimFreq,targetModulation)
		return stimFreq,error

	def _estimate_modulation_error(self,stimFreq,targetModulation):
		if rank==0: self._stim.interval = 1000./stimFreq
		Simulation.run(self)
		error = self._compute_error(targetModulation)
		return error

	def _compute_error(self,targetModulation):
		""" Compute the error between the tartget modulation and the current modulation. """
		currentModulation = self._meanFibersFr-self._meanFiringRateProfile
		error = targetModulation-currentModulation
		return error
