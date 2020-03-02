from Cell import Cell
from neuron import h

class MyelinatedFiber(Cell):
	""" Neuron Biophysical myelinated fiber model.

	The model integrates an axon model developed by Richardson et al. 2000.
	"""

	def __init__(self,length=20000,diameter=9.):
		""" Object initialization. 

		Keyword arguments:
		length -- length of the fiber in um (default = 20000)
		diameter -- diameter of the fibr in um (default = 9)
		"""

		Cell.__init__(self)
		
		self._diameterParanode = diameter
		self._diameterNode = 0.32*diameter+0.056
		self._lengthNode = 1
		self._lengthParanode = 100*self._diameterParanode
		self.nNodes = int(length/(self._lengthNode+self._lengthParanode))

		self._create_sections()
		self._build_topology()
		self._define_biophysics()

	def __del__(self):
		""" Object destruction. """
		Cell.__del__(self)

	"""
	Specific Methods of this class
	"""

	def _create_sections(self):
		""" Create the sections of the cell. """
		# NOTE: cell=self is required to tell NEURON of this object.
		self.node = [h.Section(name='node',cell=self) for x in range(self.nNodes)]
		self.paranode = [h.Section(name='paranode',cell=self) for x in range(self.nNodes)]

	def _build_topology(self):
		""" connect the sections together """
		# childSection.connect(parentSection, [parentX], [childEnd])

		for i in range(self.nNodes-1):
			self.paranode[i].connect(self.node[i],1,0)
			self.node[i+1].connect(self.paranode[i],1,0)
		self.paranode[i+1].connect(self.node[i+1],1,0)

	def _define_biophysics(self):
		""" Assign the membrane properties across the cell. """
		for node,paranode in zip(self.node,self.paranode):
			node.nseg=1
			node.diam=self._diameterNode
			node.L=self._lengthNode
			node.Ra=70
			node.cm=2
			node.insert('axnode')
			node.gnapbar_axnode = 0

			paranode.nseg=5
			paranode.diam=self._diameterParanode
			paranode.L=self._lengthParanode
			paranode.Ra=70
			paranode.cm=0.1/(2*9.15*paranode.diam+2*30)
			paranode.insert('pas')
			paranode.g_pas=0.001/(2*9.15*paranode.diam+2*30)
			paranode.e_pas=-85

	"""
	Redefinition of inherited methods
	"""

	def connect_to_target(self):
		raise Exception("connect_to_target not implemented...")

	def is_artificial(self):
		""" Return a flag to check whether the cell is an integrate-and-fire or artificial cell. """
		return 0


