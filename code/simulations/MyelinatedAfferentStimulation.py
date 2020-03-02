from mpi4py import MPI
from neuron import h
from Simulation import Simulation
from cells import MyelinatedFiber
from cells import MyelinatedFiberMcInt
import time
import numpy as np
import matplotlib.pyplot as plt

comm = MPI.COMM_WORLD
sizeComm = comm.Get_size()
rank = comm.Get_rank()

class MyelinatedAfferentStimulation(Simulation):
	""" Simulation to visualize traveling action potentials in myelinated afferent fibers. """

	def __init__(self, parallelContext, tstop = 100, fiberType="richardson"):
		""" Object initialization.

		Keyword arguments:
		parallelContext -- Neuron parallelContext object.
		tstop -- Time in ms at wich the simulation will stop (default = 100).
		fiberType -- Type of fiber model to use; it could be either "richardson"
		or "mcintyre" (default = "richardson").
		"""

		Simulation.__init__(self, parallelContext)

		if rank==1:
			print "\nWarning: mpi execution in this simulation is not supported and therfore useless."
			print "Only the results of the first process are considered...\n"

		if fiberType == "richardson": self.fiber = MyelinatedFiber()
		elif fiberType == "mcintyre": self.fiber = MyelinatedFiberMcInt()
		else: raise Exception("unkown fiber type\n Chose between 'richardson' and 'mcintyre'")

		# Initialize lists
		self._stim = []
		self._syn = []
		self._netcons = []

		self._set_tstop(tstop)
		# To plot the results with a high resolution we use an integration step equal to the Neuron dt
		self._set_integration_step(h.dt)

		# Initialize a 2d numpy array to hold the membrane potentials of the whole fiber over time
		self._membranPot = np.zeros((self.fiber.nNodes,int(np.ceil(self._get_tstop()/self._get_integration_step()+1))))
		self._count=0

	"""
	Redefinition of inherited methods
	"""

	def _update(self):
		""" Update simulation parameters. """
		for j in range(self.fiber.nNodes): self._membranPot[j,self._count] = self.fiber.node[j](0.5).v
		self._count+=1

	def save_results(self):
		""" Save the simulation results. """
		print "No data to save...use the plot method to visualize and save the plots"

	def plot(self):
		""" Plot the simulation results. """
		if rank == 0:
			fig, ax = plt.subplots(figsize=(9,7))
			im = ax.imshow(self._membranPot, interpolation='nearest',origin="lower",extent=[0,self._get_tstop(),0,self.fiber.nNodes], aspect='auto')
			ax.set_title("Action potential collision")

			# Move left and bottom spines outward by 10 points
			ax.spines['left'].set_position(('outward', 10))
			ax.spines['bottom'].set_position(('outward', 10))
			# Hide the right and top spines
			ax.spines['right'].set_visible(False)
			ax.spines['top'].set_visible(False)
			# Only show ticks on the left and bottom spines
			ax.yaxis.set_ticks_position('left')
			ax.xaxis.set_ticks_position('bottom')
			fig.colorbar(im, orientation='vertical')

			plt.ylabel('Fiber nodes')
			plt.xlabel('Time (ms)')

			fileName = time.strftime("%Y_%m_%d_MyelinatedAfferentStimulation.pdf")
			plt.savefig(self._resultsFolder+fileName, format="pdf",transparent=True)
			plt.show()

	"""
	Specific Methods of this class
	"""

	def attach_current_clamp(self,segment, amp=0.1, delay=1, dur=1):
		""" Attach a current Clamp to a segment.

		Keyword arguments:
		segment -- Segment object to attach the current clamp.
		amp -- Magnitude of the current (default = 0.1).
		delay -- Onset of the injected current (default = 0.1).
		dur -- Duration of the stimulus (default = 1).
		"""

		self._stim.append(h.IClamp(segment(0.5)))
		self._stim[-1].delay = delay
		self._stim[-1].dur = dur
		self._stim[-1].amp = amp

	def attach_netstim(self,segment,stimFreq,nPulses=1000,delay=1):
		""" Attach a Neuron NetStim object to a segment.

		Keyword arguments:
		segment -- Segment object to attach the NetStim.
		stimFreq -- Frequency of stimulation.
		nPulses -- Number of pulses to send (default = 1000).
		delay -- Onset of the stimulation (default = 1).
		"""

		self._syn.append(h.ExpSyn(segment(0.5)))
		self._syn[-1].tau = 0.1
		self._syn[-1].e= 50
		self._stim.append(h.NetStim())
		self._stim[-1].interval = 1000/stimFreq
		self._stim[-1].number = nPulses
		self._stim[-1].start = delay
		self._stim[-1].noise = 0
		self._netcons.append(h.NetCon(self._stim[-1],self._syn[-1]))
		self._netcons[-1].weight[0] = 1
		self._netcons[-1].delay =1
