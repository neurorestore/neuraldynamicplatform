from mpi4py import MPI
from neuron import h
import numpy as np
from scipy import interpolate
from cells import Motoneuron
from cells import IntFireMn
from cells import AfferentFiber
import random as rnd
import time
from tools import firings_tools as tlsf
from tools import seed_handler as sh
sh.set_seed()

comm = MPI.COMM_WORLD
sizeComm = comm.Get_size()
rank = comm.Get_rank()

class BaselineActivity():
	""" Epidural Electrical Stimulation model. """

	def __init__(self,parallelContext,neuralNetwork,firingRate):
		""" Object initialization.

		Keyword arguments:
		parallelContext -- Neuron parallelContext object.
		neuralNetwork -- NeuralNetwork instance to connect to this object.
		firingRate -- Dictionary containing the average firing rate of the
		different cells populations of interneurons.
		"""
		self._pc = parallelContext
		self._nn = neuralNetwork
		self._fr = firingRate


		# Lets assign an Id to the stim object (high value to be sure is not already take from some cell)
		self._stimId = 2000000
		# Initialize a dictionary to contain all the netstim
		self._netStims = {}
		self._netStimsId = {}
		# Initialize a dictionary to contain all the connections between the stim objects and the stimulated cells
		self._connections = {}

		# Connect the stimulation to all muscles of the neural network
		self._connect_to_network()

	def __del__(self):
		self._pc.gid_clear() # It removes also the gid of the network...


	def _connect(self,targetsId,cellType,netconList,netStims,Ids):
		""" Connect this object to target cells.

		Keyword arguments:
		targetsId -- List with the id of the target cells.
		cellType -- String defining the cell type.
		netconList -- List in which we append the created netCon Neuron objects.
		netStims -- List in which we append the created nestims
		Ids -- List in which we append the IDs of the created nestims
		"""

		for targetId in targetsId:

			self._stimId+=1
			# check whether this id is associated with a cell in this host.
			if not self._pc.gid_exists(targetId): continue

			# Tell this host it has this stim
			Ids.append(self._stimId)
			self._pc.set_gid2node(Ids[-1], rank)

			# Create the stim objetc
			netStims.append(h.NetStim())
			netStims[-1].number = 10000000000
			netStims[-1].start = 0.1
			netStims[-1].noise = 1 #intervals have negexp distribution
			if self._fr[cellType]>0: netStims[-1].interval = 1000.0/self._fr[cellType][int(np.random.randint(0,100000))]
			else: netStims[-1].interval = 1000000

			# Associate the cell with this host and id
			# the nc is also necessary to use this cell as a source for all other hosts
			nc = h.NetCon(netStims[-1],None)
			self._pc.cell(Ids[-1], nc)

			# Target interneuron
			target = self._pc.gid2cell(targetId)
			# create the connections
			nc = self._pc.gid_connect(Ids[-1],target)
			nc.weight[0] = 1.01 # every input shoul dinduce a spike fromerly 1.01
			nc.delay = 1 # delay of the connection
			nc.active(True)
			netconList.append(nc)


	def _connect_to_network(self):
		""" Connect this object to the NeuralNetwork object. """
		# Iterate over all DoFs
		for muscle in self._nn.cellsId:
			self._connections[muscle] = {}
			self._netStims[muscle] = {}
			self._netStimsId[muscle] = {}
			# Iterate over all type of cells
			for cellType in self._nn.cellsId[muscle]:
				if cellType in self._nn.get_interneurons_names():
					# Add a list to the dictionary of netcons and not only..
					self._connections[muscle][cellType] = []
					self._netStims[muscle][cellType] = []
					self._netStimsId[muscle][cellType] = []
					# connect the netstim to all these cells
					self._connect(self._nn.cellsId[muscle][cellType],cellType,self._connections[muscle][cellType],self._netStims[muscle][cellType],self._netStimsId[muscle][cellType])
				comm.Barrier()
