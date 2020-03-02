from Cell import Cell
from neuron import h
import random as rnd
import time
import numpy as np
from mpi4py import MPI
from tools import seed_handler as sh
sh.set_seed()

comm = MPI.COMM_WORLD
sizeComm = comm.Get_size()
rank = comm.Get_rank()


class AfferentFiber2(Cell):
	""" Model of the afferent fiber.

	The model integrates the collision of natural spikes witht the ones
	induced by epidural electrical stimulation (EES) of the spinal cord.
	In particular the APs induced by the stimulation and the ones induced
	by the sensory organ are added to relative lists containg all APs
	positions in the fiber at the currant time. Every 0.1 ms (__updatePeriod)
	the position of the APs in the fiber has to be updated in order to
	simulate the progation of the APs and the collision of natural and EES
	induced spikes. A refracory period of mean 1.6 ms and std of 0.16 ms is modeled.
	Note that the __updatePeriod can be incresaed in order to speed up the
	simulations. However, by increasing this value we would also loose resolution
	of the refractory period.

	This model is the same model I used in Nest. In tha case is faster than the
	first model AfferentFiber. However, in neuron, this model is slower. Here
	we don't deal we population directly...
	"""

	__updatePeriod = 0.1 # Time period in ms between calls of the update fcn
	__eesWeight = -3 # Weight of a connection between an ees object and this cell
	__maxEesFrequency = 1001

	def __init__(self,delay):
		""" Object initialization.

		Keyword arguments:
		delay -- time delay in ms needed by a spike to travel the whole fiber
		"""

		Cell.__init__(self)
		self._debug = False

		#Initialise cell parameters
		self._set_delay(delay)

		self.maxFiringRate = 200 # This should be lower than the frequency allowed by the refractory period
		self._maxSensorySpikesXtime = int(float(self._delay)/1000.*float(self.maxFiringRate)+2)
		self._maxEesSpikesXtime = int(float(self._delay)/1000.*float(self.__class__.__maxEesFrequency)+2)
		#Mean refractory period of 1.6 ms - 625 Hz
		noisePerc = 0.1
		self._refractoryPeriod = rnd.normalvariate(1.6,1.6*noisePerc)
		if self._refractoryPeriod>1000./self.maxFiringRate:
			self._refractoryPeriod=1000./self.maxFiringRate
			print "Warning: refractory period bigger than period between 2 natural pulses"
		#Position along the fiber recruited by the stimulation
		self._stimPosition = self._delay-0.5

		self.initialise()
		#Create an ARTIFICIAL_CELL Neuron mechanism that will be the source of a netCon object.
		#This will be used to comunicate the APs to target cells
		self.cell = h.AfferentFiber()

		#Create a netcon to make the fiber fire
		self._fire = h.NetCon(None,self.cell)

		# Boolean flag to record a segment of the fiber over time
		self._record = False


	"""
	Specific Methods of this class
	"""
	def initialise(self,lastSpikeTime=0):
		""" Initialise the fiber. """

		#Initial firing rate of .1 Hz
		self._interval = 9999.
		self._oldFr = 0.
		self._lastNaturalSpikeTime = lastSpikeTime

		#Sometimes when working with nans you can get annoying warnings (e.g. [nan,3]<0)
		np.seterr(invalid='ignore')

		self._lastAntiSpikeTime = -9999.
		#Create array containing the natural sensory spikes
		self._naturalSpikes = np.nan*np.ones(self._maxSensorySpikesXtime)
		self._naturalSpikesArrivalTime = np.nan*np.ones(self._maxSensorySpikesXtime)
		#Create array containing the EES induced spikes
		self._stimAntidromicSpikesArrivalTime = np.nan*np.ones(self._maxSensorySpikesXtime)#new

		#Last spike in stim position
		self._lastStimPosSpikeTime = -9999.
		#Stats
		self._nCollisions = 0
		self._nNaturalSent = 0
		self._nNaturalArrived = 0
		#For debugging
		self._eesSent = 0
		self._eesArrived = 0


	# The delay correspond to the value naturalSpikes[] should have before being sent
	def _set_delay(self,delay):
		""" Set the delay.

		Keyword arguments:
		delay -- time delay in ms needed by a spike to travel the whole fiber
		"""

		minDelay = 1
		maxDelay = 100
		if delay>=minDelay and delay<=maxDelay:
			self._delay=delay
		else:
			raise Exception("Afferent fiber delay out of limits")

	def set_firing_rate(self,fr,noise=True):
		""" Set the afferent firing rate.

		Keyword arguments:
		fr -- firing rate in Hz
		"""

		if fr == self._oldFr: return
		if fr<=0:
			self._interval = 99999.
		elif fr>=self.maxFiringRate:
			self._interval = 1000.0/self.maxFiringRate
		elif fr<self.maxFiringRate and noise:
			mean = 1000.0/fr #ms
			sigma = mean*0.2
			self._interval = rnd.normalvariate(mean,sigma)
		else: self._interval = 1000.0/fr #ms
		self._oldFr = fr


	def update(self,time):
		""" Update function that hase to be called every __updatePeriod ms of simulation.

		The fucntions:
			1)  propagates the action pontentials (APs) induced by the stimulation along
				the fiber
			2)  checks whether a new pulse of stimulation occured and in this case sends an event
				to all the connected cells at the time = time
			3)  It checks whether a natural AP reached the end of the fiber and in this case
				it sends an event to the connected cells at time = time.
			4)  It propagates the natural action pontentials (APs) along the fibers
				taking in to account possible collision with EES induced AP.
		"""

		# Check whether an antidromic stim spike arrived at the fiber origin
		indexesSpikes  = np.nonzero(self._stimAntidromicSpikesArrivalTime-time <= self.__class__.__updatePeriod/2)
		if indexesSpikes[0].size:
			if self._debug: print "\t\t\tantidromic stim spike arrived at fiber origin at time: ",time
			self._lastAntiSpikeTime = time
			# Remove spike from pipeline
			self._stimAntidromicSpikesArrivalTime[indexesSpikes[0]] = np.nan

		# Check whether a sensory spike arrived at stimulation location
		indexSpike = np.where(self._naturalSpikesArrivalTime-time <= self.__class__.__updatePeriod/2)
		if indexSpike[0].size:
			if self._debug: print "\t\t\t\t\t\t\tsensory spike arrived at time: ",time+self._delay-self._stimPosition
			self._lastStimPosSpikeTime = time
			# Send a synaptic event to the attached neurons
			self._fire.event(time+self._delay-self._stimPosition,1)
			self._nNaturalArrived += 1
			# Remove spike from pipeline
			self._naturalSpikesArrivalTime[indexSpike[0]] = np.nan

		#Check whether a new pulse of stimulation occured
		if self.cell.EES==1:
			self.cell.EES=0
			if self._debug: print "\t\t Stimulation pulse occurred at time: %f" % (time)
			self._eesSent += 1
			#check whether the fiber isn't in refractory period
			if time - self._lastStimPosSpikeTime > self._refractoryPeriod:
				self._lastStimPosSpikeTime = time
				# Send a synaptic event to the attached neurons
				self._fire.event(time+self._delay-self._stimPosition,1)
				self._eesArrived+=1
				# Check for antidromic collisions
				if np.any(self._naturalSpikesArrivalTime-time >= self.__class__.__updatePeriod/2):
					if self._debug: print "\t\t  antidromic collision occured at time: %f" % (time)
					indCollision = np.nanargmin(self._naturalSpikesArrivalTime)
					self._naturalSpikesArrivalTime[indCollision] = np.nan
					self._nCollisions+=1
				# Add antidromic stim spike to pipeline
				else:
					indNan = np.nonzero(np.isnan(self._stimAntidromicSpikesArrivalTime))
					self._stimAntidromicSpikesArrivalTime[indNan[0][0]] = time+self._stimPosition

		#Check for new sensory spike
		if (time-self._lastNaturalSpikeTime)>=self._interval-(self.__class__.__updatePeriod/2.):
			self._nNaturalSent += 1
			self._lastNaturalSpikeTime = time
			if self._debug: print "\t\t\t\t\t\t sensory spike generated at time: %f" % (time)
			# Check fibers refractory period due to antidromic spike generated by the stimulation
			if time-self._lastAntiSpikeTime<=self._refractoryPeriod:
				if self._debug: print "\t\t\t\t\t\t fiber couldn't fire because of refractory period, time: %f" % (time)
				# Conside the fibers in refractory period as andtidromic collision
				self._nCollisions+=1
			else:
				# Check for antidromic collisions
				if np.any(self._stimAntidromicSpikesArrivalTime-time >= self.__class__.__updatePeriod/2):
					if self._debug: print "\t\t\t\t\t\t  antidromic collision occured at time: %f" % (time)
					indCollision = np.nanargmin(self._stimAntidromicSpikesArrivalTime)
					self._stimAntidromicSpikesArrivalTime[indCollision] = np.nan
					self._nCollisions+=1
				# Add new sensory spike to the pipeline
				else:
					indNan = np.nonzero(np.isnan(self._naturalSpikesArrivalTime))
					self._naturalSpikesArrivalTime[indNan[0][0]] = time+self._stimPosition


	def get_delay(self):
		""" Return the time delay in ms needed by a spike to travel the whole fiber. """
		return self._delay

	def get_stats(self):
		""" Return a touple containing statistics of the fiber after a simulation is performed. """
		if float(self._nNaturalArrived+self._nCollisions)==0: percErasedAp = 0
		else: percErasedAp = float(100*self._nCollisions)/float(self._nNaturalArrived+self._nCollisions)
		return self._nNaturalSent,self._nNaturalArrived,self._nCollisions,percErasedAp

	@classmethod
	def get_update_period(cls):
		""" Return the time period between calls of the update fcn. """
		return AfferentFiber.__updatePeriod

	@classmethod
	def get_ees_weight(cls):
		""" Return the weight of a connection between an ees object and this cell. """
		return AfferentFiber.__eesWeight

	@classmethod
	def get_max_ees_frequency(cls):
		""" Return the weight of a connection between an ees object and this cell. """
		return AfferentFiber.__maxEesFrequency
