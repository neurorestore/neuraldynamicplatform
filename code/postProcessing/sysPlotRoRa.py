import sys
import pickle
import numpy as np
import subprocess
import matplotlib.pyplot as plt
from sysSearchAnalysisRORa import extract_results

def main():
	""" Open the plot of a Forward systematic search analysis. """

	if len(sys.argv)<5:
		print "Error in arguments. Required arguments:"
		print "\t pathToResults/"
		print "\t w1"
		print "\t w2"
		print "\t w3"
		print "\t w4"
		print "For all the parameter it can be inserted either the desired value to plot or 'all' - max 2 all"
		sys.exit(-1)

	pathToResultsDay = sys.argv[1]
	allWeights_1 = np.round(np.linspace(0.002,0.02,6),3)
	allWeights_2 = np.round(np.linspace(0.002,0.02,6),3)
	allWeights_3 = np.round(np.linspace(0.00,0.04,8),3)
	allWeights_4 = np.round(np.linspace(0.00,-0.0075,3),3)

	if sys.argv[2]=="all": 	iws1 = range(len(allWeights_1))
	else: iws1= np.argwhere(allWeights_1==float(sys.argv[2]))[0]
	if sys.argv[3]=="all": 	iws2 = range(len(allWeights_2))
	else: iws2= np.argwhere(allWeights_2==float(sys.argv[3]))[0]
	if sys.argv[4]=="all": 	iws3 = range(len(allWeights_3))
	else: iws3= np.argwhere(allWeights_3==float(sys.argv[4]))[0]
	if sys.argv[5]=="all": 	iws4 = range(len(allWeights_4))
	else: iws4= np.argwhere(allWeights_4==float(sys.argv[5]))[0]

	_,_,_,firingRate = extract_results(allWeights_1,allWeights_2,allWeights_3,allWeights_4,pathToResultsDay)
	if sys.argv[2]=="all" and sys.argv[3]=="all":
		for iw3 in iws3:
			for iw4 in iws4:
				plot_firing_rate_w1_w2(iws1,iws2,iw3,iw4,firingRate)
	if sys.argv[4]=="all" and sys.argv[5]=="all":
		for iw1 in iws1:
			for iw2 in iws2:
				plot_firing_rate_w3_w4(iw1,iw2,iws3,iws4,firingRate)


def plot_firing_rate_w1_w2(iws1,iws2,iw3,iw4,firingRate):
	""" Plots the EMG signals for the different parameters. """
	fig, ax = plt.subplots(len(iws1), len(iws2),figsize=(22,12),sharex='col',sharey='col')
	for iw1 in iws1:
		for iw2 in iws2:
			ax[iw1,iw2].plot(firingRate["drug"][iw1,iw2,iw3,iw4]['TA']['Mn'],'r')
			ax[iw1,iw2].plot(firingRate["drug"][iw1,iw2,iw3,iw4]['GM']['Mn'],'b')
			ax[iw1,iw2].xaxis.set_ticklabels([])
			ax[iw1,iw2].yaxis.set_ticklabels([])
			ax[iw1,iw2].xaxis.set_ticks([])
			ax[iw1,iw2].yaxis.set_ticks([])
			if iw2==0:ax[iw1,iw2].set_ylabel("iw1 \n"+str(iw1))
			if iw1==len(iws1)-1:ax[iw1,iw2].set_xlabel("iw2 = "+str(iw2))
	fig.suptitle("drug iw3 = "+str(iw3)+" iw4 = "+str(iw4))
	fig2, ax2 = plt.subplots(len(iws1), len(iws2),figsize=(22,12),sharex='col',sharey='col')
	for iw1 in iws1:
		for iw2 in iws2:
			ax2[iw1,iw2].plot(firingRate["noDrug"][iw1,iw2,iw3,iw4]['TA']['Mn'],'r')
			ax2[iw1,iw2].plot(firingRate["noDrug"][iw1,iw2,iw3,iw4]['GM']['Mn'],'b')
			ax2[iw1,iw2].xaxis.set_ticklabels([])
			ax2[iw1,iw2].yaxis.set_ticklabels([])
			ax2[iw1,iw2].xaxis.set_ticks([])
			ax2[iw1,iw2].yaxis.set_ticks([])
			if iw2==0:ax2[iw1,iw2].set_ylabel("iw1 \n"+str(iw1))
			if iw1==len(iws1)-1:ax2[iw1,iw2].set_xlabel("iw2 = "+str(iw2))
	fig2.suptitle("no drug iw3 = "+str(iw3)+" iw4 = "+str(iw4))
	plt.show()

def plot_firing_rate_w3_w4(iw1,iw2,iws3,iws4,firingRate):
	""" Plots the EMG signals for the different parameters. """
	fig, ax = plt.subplots(len(iws3), len(iws4),figsize=(22,12),sharex='col',sharey='col')
	for iw3 in iws3:
		for iw4 in iws4:
			ax[iw3,iw4].plot(firingRate["drug"][iw1,iw2,iw3,iw4]['TA']['Mn'],'r')
			ax[iw3,iw4].plot(firingRate["drug"][iw1,iw2,iw3,iw4]['GM']['Mn'],'b')
			ax[iw3,iw4].xaxis.set_ticklabels([])
			ax[iw3,iw4].yaxis.set_ticklabels([])
			ax[iw3,iw4].xaxis.set_ticks([])
			ax[iw3,iw4].yaxis.set_ticks([])
			if iw4==0:ax[iw3,iw4].set_ylabel("iw3 \n"+str(iw3))
			if iw3==len(iws3)-1:ax[iw3,iw4].set_xlabel("iw4 = "+str(iw4))
	fig.suptitle("drug iw1 = "+str(iw1)+" iw2 = "+str(iw2))
	fig2, ax2 = plt.subplots(len(iws3), len(iws4),figsize=(22,12),sharex='col',sharey='col')
	for iw3 in iws3:
		for iw4 in iws4:
			ax2[iw3,iw4].plot(firingRate["noDrug"][iw1,iw2,iw3,iw4]['TA']['Mn'],'r')
			ax2[iw3,iw4].plot(firingRate["noDrug"][iw1,iw2,iw3,iw4]['GM']['Mn'],'b')
			ax2[iw3,iw4].xaxis.set_ticklabels([])
			ax2[iw3,iw4].yaxis.set_ticklabels([])
			ax2[iw3,iw4].xaxis.set_ticks([])
			ax2[iw3,iw4].yaxis.set_ticks([])
			if iw4==0:ax2[iw3,iw4].set_ylabel("iw3 \n"+str(iw3))
			if iw3==len(iws3)-1:ax2[iw3,iw4].set_xlabel("iw4 = "+str(iw4))
	fig2.suptitle("no drug iw1 = "+str(iw1)+" iw2 = "+str(iw2))
	plt.show()

if __name__ == '__main__':
	main()
