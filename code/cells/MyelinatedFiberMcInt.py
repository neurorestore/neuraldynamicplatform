from Cell import Cell
from neuron import h
import numpy as np

class MyelinatedFiberMcInt(Cell):
	""" Neuron Biophysical myelinated fiber model.

	The model integrates an axon model developed by McIntyre 2002.
	"""

	def __init__(self,diameterInd=3):
		""" Object initialization. 

		Keyword arguments:
		diameterInd -- index of the possibleDiameters list (default = 3)
		possibleDiameters = [5.7, 7.3, 8.7, 10.0, 11.5, 12.8, 14.0, 15.0, 16.0]
		"""

		Cell.__init__(self)
		
		self._init_parameters(diameterInd)
		self._create_sections()
		self._build_topology()
		self._define_biophysics()

	def __del__(self):
		""" Object destruction. """
		Cell.__del__(self)

	"""
	Specific Methods of this class
	"""
	
	def _init_parameters(self,diameterInd):
		""" Initialize all cell parameters. """

		# topological parameters
		self.nNodes = 21
		self._axonNodes=self.nNodes
		self._paraNodes1=40
		self._paraNodes2=40
		self._axonInter=120
		self._axonTotal=221
		# morphological parameters
		possibleDiameters = [5.7, 7.3, 8.7, 10.0, 11.5, 12.8, 14.0, 15.0, 16.0]
		self._fiberD=possibleDiameters[diameterInd]
		self._paraLength1=3  
		self._nodeLength=1.0
		self._spaceP1=0.002  
		self._spaceP2=0.004
		self._spaceI=0.004
		# electrical parameters
		self._rhoa=0.7e6 #Ohm-um
		self._mycm=0.1 #uF/cm2/lamella membrane
		self._mygm=0.001 #S/cm2/lamella membrane

		if self._fiberD==5.7:
			self._g=0.605 
			self._axonD=3.4
			self._nodeD=1.9
			self._paraD1=1.9
			self._paraD2=3.4
			self._deltax=500
			self._paraLength2=35
			self._nl=80
		if self._fiberD==8.7:
			self._g=0.661
			self._axonD=5.8
			self._nodeD=2.8
			self._paraD1=2.8
			self._paraD2=5.8
			self._deltax=1000
			self._paraLength2=40
			self._nl=110
		if self._fiberD==10.0:
			self._g=0.690
			self._axonD=6.9
			self._nodeD=3.3
			self._paraD1=3.3
			self._paraD2=6.9
			self._deltax=1150
			self._paraLength2=46
			self._nl=120
		if self._fiberD==11.5:
			self._g=0.700
			self._axonD=8.1
			self._nodeD=3.7
			self._paraD1=3.7
			self._paraD2=8.1
			self._deltax=1250
			self._paraLength2=50
			self._nl=130
		if self._fiberD==12.8:
			self._g=0.719
			self._axonD=9.2
			self._nodeD=4.2
			self._paraD1=4.2
			self._paraD2=9.2
			self._deltax=1350
			self._paraLength2=54
			self._nl=135
		if self._fiberD==14.0:
			self._g=0.739
			self._axonD=10.4
			self._nodeD=4.7
			self._paraD1=4.7
			self._paraD2=10.4
			self._deltax=1400
			self._paraLength2=56
			self._nl=140
		if self._fiberD==15.0:
			self._g=0.767
			self._axonD=11.5
			self._nodeD=5.0
			self._paraD1=5.0
			self._paraD2=11.5
			self._deltax=1450
			self._paraLength2=58
			self._nl=145
		if self._fiberD==16.0:
			self._g=0.791
			self._axonD=12.7
			self._nodeD=5.5
			self._paraD1=5.5
			self._paraD2=12.7
			self._deltax=1500
			self._paraLength2=60
			self._nl=150

		self._Rpn0=(self._rhoa*.01)/(np.pi*((((self._nodeD/2)+self._spaceP1)**2)-((self._nodeD/2)**2)))
		self._Rpn1=(self._rhoa*.01)/(np.pi*((((self._paraD1/2)+self._spaceP1)**2)-((self._paraD1/2)**2)))
		self._Rpn2=(self._rhoa*.01)/(np.pi*((((self._paraD2/2)+self._spaceP2)**2)-((self._paraD2/2)**2)))
		self._Rpx=(self._rhoa*.01)/(np.pi*((((self._axonD/2)+self._spaceI)**2)-((self._axonD/2)**2)))
		self._interLength=(self._deltax-self._nodeLength-(2*self._paraLength1)-(2*self._paraLength2))/6

	def _create_sections(self):
		""" Create the sections of the cell. """
		# NOTE: cell=self is required to tell NEURON of this object.
		self.node = [h.Section(name='node',cell=self) for x in range(self._axonNodes)]
		self.mysa = [h.Section(name='mysa',cell=self) for x in range(self._paraNodes1)]
		self.flut = [h.Section(name='flut',cell=self) for x in range(self._paraNodes2)]
		self.stin = [h.Section(name='stin',cell=self) for x in range(self._axonInter)]

	def _define_biophysics(self):
		""" Assign the membrane properties across the cell. """
		for node in self.node:
			node.nseg=1
			node.diam=self._nodeD
			node.L=self._nodeLength
			node.Ra=self._rhoa/10000
			node.cm=2
			node.insert('axnode')
			node.insert('extracellular')
			node.xraxial[0]=self._Rpn0
			node.xg[0]=1e10
			node.xc[0]=0

		for mysa in self.mysa:
			mysa.nseg=1
			mysa.diam=self._fiberD
			mysa.L=self._paraLength1
			mysa.Ra=self._rhoa*(1/(self._paraD1/self._fiberD)**2)/10000
			mysa.cm=2*self._paraD1/self._fiberD
			mysa.insert('pas')
			mysa.g_pas=0.001*self._paraD1/self._fiberD		
			mysa.e_pas=-80
			mysa.insert('extracellular')
			mysa.xraxial[0]=self._Rpn1
			mysa.xg[0]=self._mygm/(self._nl*2)
			mysa.xc[0]=self._mycm/(self._nl*2)

		for flut in self.flut:
			flut.nseg=1
			flut.diam=self._fiberD
			flut.L=self._paraLength2
			flut.Ra=self._rhoa*(1/(self._paraD2/self._fiberD)**2)/10000
			flut.cm=2*self._paraD2/self._fiberD
			flut.insert('pas')
			flut.g_pas=0.0001*self._paraD2/self._fiberD		
			flut.e_pas=-80
			flut.insert('extracellular')
			flut.xraxial[0]=self._Rpn2
			flut.xg[0]=self._mygm/(self._nl*2)
			flut.xc[0]=self._mycm/(self._nl*2)
		
		for stin in self.stin:
			stin.nseg=1
			stin.diam=self._fiberD
			stin.L=self._interLength
			stin.Ra=self._rhoa*(1/(self._axonD/self._fiberD)**2)/10000
			stin.cm=2*self._axonD/self._fiberD
			stin.insert('pas')
			stin.g_pas=0.0001*self._axonD/self._fiberD
			stin.e_pas=-80
			stin.insert('extracellular')
			stin.xraxial[0]=self._Rpx
			stin.xg[0]=self._mygm/(self._nl*2)
			stin.xc[0]=self._mycm/(self._nl*2)

	def _build_topology(self):
		""" connect the sections together """
		# childSection.connect(parentSection, [parentX], [childEnd])
		for i in range(self._axonNodes-1):
			self.node[i].connect(self.mysa[2*i],0,1)
			self.mysa[2*i].connect(self.flut[2*i],0,1)
			self.flut[2*i].connect(self.stin[6*i],0,1)
			self.stin[6*i].connect(self.stin[6*i+1],0,1)
			self.stin[6*i+1].connect(self.stin[6*i+2],0,1)
			self.stin[6*i+2].connect(self.stin[6*i+3],0,1)
			self.stin[6*i+3].connect(self.stin[6*i+4],0,1)
			self.stin[6*i+4].connect(self.stin[6*i+5],0,1)
			self.stin[6*i+5].connect(self.flut[2*i+1],0,1)
			self.flut[2*i+1].connect(self.mysa[2*i+1],0,1)
			self.mysa[2*i+1].connect(self.node[i+1],0,1)

	"""
	Redefinition of inherited methods
	"""

	def connect_to_target(self):
		raise Exception("connect_to_target not implemented...")

	def is_artificial(self):
		""" Return a flag to check whether the cell is an integrate-and-fire or artificial cell. """
		return 0
