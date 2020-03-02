from mpi4py import MPI
from neuron import h
import numpy as np
from scipy import interpolate
from cells import Motoneuron
from cells import IntFireMn
from cells import AfferentFiber
import random as rnd
import time
from tools import seed_handler as sh
sh.set_seed()

comm = MPI.COMM_WORLD
sizeComm = comm.Get_size()
rank = comm.Get_rank()

class NetworkStimulation():
	""" Network stimulation.

	Useful to asses the response of the network to perturbations.
	"""

	def __init__(self,parallelContext,neuralNetwork,targetsId,cellName,percStimFiber,frequency,pulsesNumber,startTime):
		""" Object initialization.

		Keyword arguments:
		parallelContext -- Neuron parallelContext object.
		neuralNetwork -- NeuralNetwork object to connect to this object.
		targetsId -- Id of the cells to stimulate.
		cellName -- Name of the cells to stimulate.
		percStimFiber -- Percentage of stimulated fibers.
		frequency -- Stimulation frequency in Hz; it has to be lower than the
		maximum stimulation frequency imposed by the AfferentFiber model.
		pulsesNumber -- number of pulses to send.
		startTime -- time to start the stimulation.
		"""

		self._pc = parallelContext
		self._nn = neuralNetwork
		# Lets assign an Id to the stim object (high value to be sure is not already take from some cell)
		self._stimId = 2000000


		self._maxFrequency = AfferentFiber.get_max_ees_frequency()
		self._percStimFiber = percStimFiber

		# Create the netStim Object in the first process
		if rank==0:
			# Tell this host it has this cellId
			self._pc.set_gid2node(self._stimId, rank)

			# Create the stim objetc
			self._stim = h.NetStim()
			self._stim.number = pulsesNumber
			self._stim.start = startTime
			self._stim.noise = 0

			self._pulses = h.Vector()
			# Associate the cell with this host and id
			# the nc is also necessary to use this cell as a source for all other hosts
			nc = h.NetCon(self._stim,None)
			self._pc.cell(self._stimId, nc)
			# Record the stimulation pulses
			nc.record(self._pulses)

		# Connect the stimulation to the cells
		self._connections = []
		self._connect(targetsId,cellName,self._connections)

		# Set stimulation parameters
		self._activate_connections(self._connections,self._percStimFiber)
		self.set_frequency(frequency)

	def __del__(self):
		self._pc.gid_clear() # It removes also the gid of the network...

	def _connect(self,targetsId,cellName,netconList):
		""" Connect this object to target cells.

		Keyword arguments:
		targetsId -- List with the id of the target cells.
		cellName -- String defining the cell name.
		netconList -- List in which we append the created netCon Neuron objects.
		"""

		delay=1 # delay of the connection
		if cellName in self._nn.get_afferents_names(): weight = AfferentFiber.get_ees_weight()
		elif cellName in self._nn.get_real_motoneurons_names(): weight = Motoneuron.get_ees_weight()
		elif cellName in self._nn.get_intf_motoneurons_names(): weight = IntFireMn.get_ees_weight()
		else: raise Exception("undefined celltype for EES...")

		for targetId in targetsId:
			# check whether this id is associated with a cell in this host.
			if not self._pc.gid_exists(targetId): continue

			if cellName in self._nn.get_real_motoneurons_names():
				cell = self._pc.gid2cell(targetId)
				target = cell.create_synapse('ees')
			else: target = self._pc.gid2cell(targetId)

			# create the connections
			nc = self._pc.gid_connect(self._stimId,target)
			nc.weight[0] = weight
			nc.delay = delay
			nc.active(False)
			netconList.append(nc)

	def _activate_connections(self,netcons,percentage):
		""" Modify which connections are active. """
		for nc in netcons: nc.active(False)
		nCon = comm.gather(len(netcons),root=0)
		nOn = None
		if rank==0:
			nCon = sum(nCon)
			nOnTot = int(round(percentage*nCon))
			nOn = np.zeros(sizeComm) + nOnTot/sizeComm
			for i in xrange(nOnTot%sizeComm): nOn[i]+=1
		nOn = comm.scatter(nOn, root=0)

		ncIndexes = range(len(netcons))
		rnd.shuffle(ncIndexes)
		for indx in ncIndexes[:int(nOn)]: netcons[indx].active(True)

	def set_frequency(self,frequency):
		""" Set the frequency of stimulation.

		Note that currently all DoFs have the same percentage of afferents recruited.
		Keyword arguments:
		frequency -- Stimulation frequency in Hz; it has to be lower than the
		maximum stimulation frequency imposed by the AfferentFiber model.
		"""
		if rank == 0:
			if frequency>0 and frequency<self._maxFrequency:
				self._frequency = frequency
				self._stim.interval = 1000.0/self._frequency
			elif frequency<=0:
				self._frequency = 0
				self._stim.interval = 10000
			elif frequency>=self._maxFrequency:
				raise(Exception("The stimulation frequency exceeds the maximum frequency imposed by the AfferentFiber model."))
