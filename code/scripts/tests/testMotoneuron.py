#!/opt/local/bin/python

import sys
sys.path.append('../code')
from neuron import h
from cells import Motoneuron
import numpy as np
import matplotlib.pyplot as plt

def main():
	"""
	This program can be used to evaluate the Motoneuron membrane dynamics in response to
	excitatory or inhibitory inputs.
	To run the program it is neccessary to provide three arguments:
	1) the weight of the inputs (a number greater than 0)
	2) Whether we simulate a Motoneuron with the 5ht compound or not (0 or 1)
	3) the type of synpase we want to simulate. This value could be either:
		"excitatory" to simulate standard excitatory synapses
		"inhibitory" to simulate standard inhibitory synapses
		"ees" to simulate excitation induced by the epidural elcetrical stimulation
		custom-s to simulate an excitatory synapse directly on the soma of the Motoneuron
		custom-dn to simulate an excitatory synapse directly on the nth compartement of
		the denritic tree (n can range from 0 to 6)
	"""

	argc = len(sys.argv)
	if (argc < 4):
		print "\nProblem in arguments\nParameters: weight - drug - synapse"
		print "weight: number"
		print "drug: 0/1"
		print "Synapse: excitatory inhibitory ees custom-s custom-d0 custom-d1 ... custom-d6"
		sys.exit(-1)

	weight = float(sys.argv[1])
	drug = int(sys.argv[2])
	synapse = sys.argv[3]
	print synapse

	h.celsius = 37
	stim = h.NetStim()
	stim.interval=2
	stim.start=100
	stim.noise=0
	stim.number=10000

	mn = Motoneuron(drug)

	if synapse=="excitatory": mn.create_synapse("excitatory")
	elif synapse=="inhibitory": mn.create_synapse("inhibitory")
	elif synapse=="ees": mn.create_synapse("ees")
	elif synapse=="custom-s": syn = h.ExpSyn(mn.soma(0.5))
	elif synapse=="custom-d0": syn = h.ExpSyn(mn.dendrite[0](0.5))
	elif synapse=="custom-d1": syn = h.ExpSyn(mn.dendrite[1](0.5))
	elif synapse=="custom-d2": syn = h.ExpSyn(mn.dendrite[2](0.5))
	elif synapse=="custom-d3": syn = h.ExpSyn(mn.dendrite[3](0.5))
	elif synapse=="custom-d4": syn = h.ExpSyn(mn.dendrite[4](0.5))
	elif synapse=="custom-d5": syn = h.ExpSyn(mn.dendrite[5](0.5))
	elif synapse=="custom-d6": syn = h.ExpSyn(mn.dendrite[6](0.5))
	if synapse[0]=="c":
		syn.tau = 0.5
		syn.e = 0
		mn.synapses.append(syn)

	sd = mn.connect_to_target(None)
	ap=h.Vector()
	sd.record(ap)

	nc = h.NetCon(stim, mn.synapses[-1])
	nc.delay=1
	nc.weight[0]=weight



	h.finitialize(-70)
	totTime = 1000
	m = -1*np.zeros(int(totTime/h.dt+.999))
	t = -1*np.zeros(int(totTime/h.dt+.999))
	t0 = i = 0


	while h.t<totTime:
		h.fadvance()
		m[i]=mn.soma.v
		t[i]=h.t
		i+=1

	print "\n\nMn firing rate is: "+str(ap.size()*1000/totTime)+"Hz \n"

	fig, ax = plt.subplots(figsize=(8,4))
	plt.plot(t,m)
	plt.show()

if __name__ == '__main__':
	main()
