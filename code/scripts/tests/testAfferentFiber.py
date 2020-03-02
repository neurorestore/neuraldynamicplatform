#!/opt/local/bin/python

import sys
sys.path.append('../code')
from neuron import h
from cells import AfferentFiber
import numpy as np
import matplotlib.pyplot as plt
import random as rnd
import time


def main():
	"""
	This program can be used to evaluate how natural spikes collide with the spikes
	induced by epidural electrical stimulation (EES) of the spinal cord.
	These collisions are tigthly linked to three different factors:
	1) Length of the fiber and therfore the time delay needed by an action potential
	to travel from the begginning of the fiber to the end.
	2) The firing rate of the fiber.
	3) The frequency of stimulation of the fiber.
	These three parameters (delay, fiberFr and eesFr) have to be provided as input arguments.
	"""

	argc = len(sys.argv)
	if (argc < 4):
		print "\nProblem in arguments\nParameters: delay, fiberFr, eesFr, slow/fast"
		sys.exit(-1)

	delay = float(sys.argv[1])
	fiberFr = float(sys.argv[2])
	eesFr = float(sys.argv[3])
	start = time.time()

	#Create fiber
	fiber = AfferentFiber(delay)
	fiber.set_firing_rate(fiberFr)


	rnd.seed(10)
	scale = rnd.random()
	ees = h.NetStim()
	ees.interval = 1000.0/eesFr
	ees.number = 1000
	ees.start = 10.0*scale
	ees.noise = 0


	#Create cell target of the fiber
	cell = h.IntFire4()
	cell.taue= 0.5
	cell.taui1=0.6
	cell.taui2=1
	cell.taum= 5

	nc = h.NetCon(ees, fiber.cell)
	nc.delay = 1
	nc.weight[0] = AfferentFiber.get_ees_weight()

	nc2 = h.NetCon(fiber.cell, cell)
	nc2.delay = 1
	nc2.weight[0] = 0.1

	h.finitialize()
	totTime = 5200
	m = -1*np.zeros(int(totTime/h.dt+1.999))
	t = -1*np.zeros(int(totTime/h.dt+1.999))
	t0 = i = 0

	print "\nEES frequency: "+str(eesFr)+"(Hz) starting at "+str(ees.start)+" (ms)"
	print "Fiber interval: "+str(fiber._interval)+"(ms) ,delay of "+str(delay)+" (ms)\n"

	while h.t<totTime:
		h.fadvance()
		m[i]=cell.M(0)
		t[i]=h.t
		i+=1
		if h.t-t0>=AfferentFiber.get_update_period():
			t0=h.t
			fiber.update(h.t)
			# print "ees "+str(fiber._eesSpikes[:5])+"\t nat "+str(fiber._naturalSpikes[:3])


	stats = fiber.get_stats()

	end = time.time()
	print "time: ",(end - start)
	fig, ax = plt.subplots(figsize=(8,4))
	plt.plot(t,m)
	ax.set_title(stats)
	plt.show()


if __name__ == '__main__':
	main()
