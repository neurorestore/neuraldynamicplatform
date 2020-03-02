from mpi4py import MPI
from neuron import h
from Simulation import Simulation
from cells import AfferentFiber
import random as rnd
import time
import sys
import numpy as np
import matplotlib.pyplot as plt
from tools import firings_tools as tlsf
from tools import afferents_tools as tlsa
from tools import RealTimePlotter as rtp

comm = MPI.COMM_WORLD
sizeComm = comm.Get_size()
rank = comm.Get_rank()

class ClosedLoop(Simulation):
	""" Closed loop simulation of a neuro-biomechanical model.

	Here the modeled neural network is integrated over time given the
	sensory information coming from the musculoskeletal model.

	Communication
		Information coming from the musculoskeletal model:
			- "time", i.e.: "6.54"
			- "muscleName stretch", i.e.: "right_ta 2.22"
			- "muscleName stretch"
			- "muscleName stretch"
			- ...
		Information to send at the musculoskeletal model:
			- "muscleName muscActivation", i.e. "right_ta 0.68"
			- "muscleName muscActivation"
			- "muscleName muscActivation"
	"""

	def __init__(self, parallelContext, neuralNetwork, dtCommunication, species="human", ees=None, tStop = 999999):
		""" Object initialization.

		Keyword arguments:
		parallelContext -- Neuron parallelContext object.
		neuralNetwork -- NeuralNetwork object.
		dtCommunication -- period of time in ms at wich the firing rate is updated from the musculoskeletal model.
		species -- 'mouse', 'rat' or 'human' (default == human))
		ees -- possible EES object connected to the NeuralNetwork. If no EES objects
		are connected use None (default = None).
		tStop -- Time in ms at wich the simulation will stop (default = 999999).
		"""

		Simulation.__init__(self,parallelContext)

		if rank==1:
			print "\nMPI execution: the cells are divided in the different hosts.\n"

		self._nn = neuralNetwork
		self._ees = ees #! Not really usefull...
		self._species = species
		self._set_integration_step(AfferentFiber.get_update_period())
		self._dtCommunication = dtCommunication
		self._set_tstop(tStop)

		self._init_afferents_fr()
		self._init_muscles_param()
		self._incoming_msg = ""
		self._doStep = False

		if rank==0:
			self._tMuscModel = -self._dtCommunication
			self.maxMnFr = 50. #Hz
			yLabels = self._muscAct.keys()
			self._plotter = rtp.RealTimePlotter(yLabels)


	"""
	Redefinition of inherited methods
	"""
	def _initialize(self):
		Simulation._initialize(self)
		self._timeUpdateAfferents = 0

	def _integrate(self):
		""" Integrate the neuronal cells for a defined integration time step ."""
		if self._doStep: Simulation._integrate(self)

	def _update(self):
		""" Update simulation parameters. """
		if self._doStep:
			self._nn.update_afferents_ap(h.t)
			if h.t-self._tLastStep>= (self._dtCommunication-0.5*self._get_integration_step()):
				if rank==0: print "dt integration completed."
				if rank==0: print "compute musc activations..."
				self._compute_musc_act()
				if rank==0: print "send data.."
				self._send_data()
				self._doStep = False
				self.plot()
		else:
			if rank==0:
				print "Waiting for a message..." # visto che e blocking questo non e necessario
				self._incoming_msg = sys.stdin.readline().rstrip("\n")
				print "Message received: "+str(self._incoming_msg)
				if self._incoming_msg == "COMM IN": self._doStep = True
			comm.Barrier()
			self._doStep = comm.bcast(self._doStep, root=0)
			if self._doStep:
				if rank==0: print "doing a step of simulation..."
				self._tLastStep = h.t
				self._get_data()
				if rank==0: print "data received..."
				self._update_afferents_fr()
				self._nn.set_afferents_fr(self._afferentFr)
				if rank==0: print "afferents updated..."

	def _end_integration(self):
		""" Print the total simulation time and extract the results. """
		Simulation._end_integration(self)
		self._extract_results()
		if rank==0: self._plotter.save_fig()

	def plot(self,name=""):
		if rank==0:
			yVals = self._muscAct.values()
			self._plotter.add_values(h.t,yVals)

	"""
	Specific Methods of this class
	"""

	def _init_afferents_fr(self):
		""" Initialize the dictionary necessary to update the afferent fibers. """
		self._afferentFr = {}
		for muscle in self._nn.cells:
			self._afferentFr[muscle]={}
			for cellType in self._nn.cells[muscle]:
				if cellType in self._nn.get_afferents_names():
					self._afferentFr[muscle][cellType]= 0.

	def _init_muscles_param(self):
		""" Initialize muscles parameters dictionaries. """
		muscleName = self._nn.cells.keys()[0]
		nMnList = comm.gather(len(self._nn.cells[muscleName]["Mn"]),root=0)
		if rank==0:
			self._nMn = sum(nMnList)
			self._muscStretch = {}
			self._muscStretchOld = {}
			self._muscStretchVel = {}
			self._muscAct = {}
			self._nApMn = {}

			self._timeWindowMnRec = 250.# ms
			nRecordingWindows = np.ceil(self._timeWindowMnRec/self._dtCommunication)

			for muscle in self._nn.cells:
				self._muscStretch[muscle] = 0.
				self._muscStretchOld[muscle] = 0.
				self._muscStretchVel[muscle] = 0.
				self._muscAct[muscle] = 0.
				self._nApMn[muscle] = np.zeros([int(nRecordingWindows),self._nMn])

	def _get_data(self):
		""" Read and update muscles stretch in mm and time in ms form the musculoskeletal model. """
		if rank ==0:
			# update values of the previous step
			for muscle in self._muscStretch: self._muscStretchOld[muscle]=self._muscStretch[muscle]
			tMuscModelOld = self._tMuscModel

			# Read the current time in the musculoskeletal model.
			self._tMuscModel = float(sys.stdin.readline().rstrip("\n"))
			dtMuscModel = self._tMuscModel-tMuscModelOld # this dt should be equal to the closedLoop period of the neural network

			if not abs(dtMuscModel-self._dtCommunication)<1.5:
				raise AssertionError("mismatch between the NN dt and the MM dt")
			# Read and update the muscles stretch from the musculoskeletal model.
			for i in self._muscStretch:
				# THe string coming from the musculoskeletal model has to be formatted as: "muscle(str) net(str) stretch(float)"
				muscInfo = sys.stdin.readline().rstrip("\n").split()
				muscle = muscInfo[0]
				self._muscStretch[muscle] = float(muscInfo[1])

			# Update the muscles stretch velocity
			if h.t != 0:
				for muscle in self._muscStretch:
						self._muscStretchVel[muscle] = (self._muscStretch[muscle]-self._muscStretchOld[muscle])/dtMuscModel

		comm.Barrier()

	def _update_afferents_fr(self):
		""" Estimate and update the afferents firing rate."""
		if rank==0: print "Start afferents info...\n"
		for muscle in self._afferentFr:
			if rank==0:
				# compute the afferents fr
				self._afferentFr[muscle]['Iaf'] = tlsa.compute_Ia_fr(self._muscStretch[muscle],self._muscStretchVel[muscle],self._muscAct[muscle],self._species)
				self._afferentFr[muscle]['IIf'] = tlsa.compute_II_fr(self._muscStretch[muscle],self._muscAct[muscle],self._species)
				print muscle+"stretch: ",self._muscStretch[muscle]
				print muscle+"stretch velocity: ",self._muscStretchVel[muscle]
				print muscle+"Iaf: ",self._afferentFr[muscle]['Iaf']
				print muscle+"IIf: ",self._afferentFr[muscle]['IIf']
			comm.Barrier()
			self._afferentFr[muscle]['Iaf'] = comm.bcast(self._afferentFr[muscle]['Iaf'],root=0)
			self._afferentFr[muscle]['IIf'] = comm.bcast(self._afferentFr[muscle]['IIf'],root=0)
		if rank==0: print "\n...end"

	def _compute_musc_act(self):
		""" Compute the muscle activations """
		nApMnNew = self._nn.get_ap_number(["Mn"])
		if rank==0:
			# Update the recorded windows of nMnAp
			for muscle in self._nApMn:
				for i in xrange(self._nApMn[muscle].shape[0]-1):
					self._nApMn[muscle][i,:] = self._nApMn[muscle][i+1,:]
				self._nApMn[muscle][-1,:] = nApMnNew[muscle]["Mn"]
				mnFr = (self._nApMn[muscle][-1,:].sum()-self._nApMn[muscle][0,:].sum())/self._nMn/self._timeWindowMnRec*1000
				self._muscAct[muscle] = mnFr/self.maxMnFr
				if self._muscAct[muscle]>1: self._muscAct[muscle]=1
		comm.Barrier()

	def _send_data(self):
		if rank==0:
			print "COMM_OUT"
			for muscle in self._muscAct: print " ".join([muscle,str(self._muscAct[muscle])])
			print "END"



	def _extract_results(self):
		""" Extract the simulation results. """
		if rank==0: print "Extracting the results",
		firings = {}
		self._meanFr = {}
		self._estimatedEMG = {}
		for muscle in self._nn.actionPotentials:
			firings[muscle]={}
			self._meanFr[muscle]={}
			self._estimatedEMG[muscle]={}
			for cell in self._nn.actionPotentials[muscle]:
				firings[muscle][cell] = tlsf.exctract_firings(self._nn.actionPotentials[muscle][cell])
				self._meanFr[muscle][cell] = tlsf.compute_mean_firing_rate(firings[muscle][cell])
				self._estimatedEMG[muscle][cell] = tlsf.synth_rat_emg(firings[muscle][cell])
				if rank==0: print ".",
		if rank==0: print "...completed."
