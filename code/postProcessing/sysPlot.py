import sys
import pickle
import numpy as np
import subprocess
import matplotlib.pyplot as plt

def main():
	""" Open the plot of a Forward systematic search analysis. """

	if len(sys.argv)<5:
		print "Error in arguments. Required arguments:"
		print "\t pathToResults/day (YYYY_MM_DD)"
		print "\t ees frequency"
		print "\t delay"
		print "\t w1"
		print "\t w2"
		print "For all the parameter it can be inserted either the desired value to plot or 'all'"
		sys.exit(-1)

	pathToResultsDay = sys.argv[1]

	if sys.argv[2]=="all": eesFrequencies=[0,29,50]
	else: eesFrequencies=[int(sys.argv[2])]
	
	if sys.argv[3]=="all": delays=[2,25]
	else: delays=[int(sys.argv[3])]
	
	if sys.argv[4]=="all":
		if "2016_01_20" in pathToResultsDay: weights_1 = np.linspace(0.008,0.02,20)
		elif "2016_01_19" in pathToResultsDay: weights_1 = np.linspace(0.004,0.04,10)
	else: weights_1=[float(sys.argv[4])]
	
	if sys.argv[5]=="all":
		if "2016_01_20" in pathToResultsDay:weights_2 = np.linspace(-0.01,-0.001,20)
		elif "2016_01_19" in pathToResultsDay:weights_2 = np.linspace(-0.025,-0.0025,10)
	else: weights_2=[float(sys.argv[5])]

	if sys.argv[4]==sys.argv[5]=="all":
		plot_all_emg(pathToResultsDay,eesFrequencies[0],delays[0],weights_1,weights_2)
		return
	
	for eesFre in eesFrequencies:
		for delay in delays:
			for w1 in weights_1:
				for w2 in weights_2:
					fileToLoad = pathToResultsDay+"_FS_EES_235uA_"+str(eesFre)+"Hz_Delay_"+str(delay)\
						+"ms_w1_"+"{:.3f}".format(w1)+"_w2_"+"{:.3f}".format(w2)
					openImage = ["open "+fileToLoad+".pdf"]
					preview = subprocess.Popen(openImage,shell=True)
					preview.wait()

def plot_all_emg(pathToResultsDay,eesFreq,delay,weights_1,weights_2):
	""" Plots the EMG signals for the different parameters. """
	fig, ax = plt.subplots(weights_1.size, weights_2.size,figsize=(22,12),sharex='col',sharey='col')
	for i1,w1 in enumerate(weights_1):
		for i2,w2 in enumerate(weights_2):
			fileToLoad = pathToResultsDay+"_FS_EES_235uA_"+str(eesFreq)+"Hz_Delay_"+str(delay)+\
							"ms_w1_"+str(w1)+"_w2_"+str(w2)+".p"
			with open(fileToLoad, 'r') as pickle_file:
				estimatedEmg = pickle.load(pickle_file)
			ax[i1,i2].plot(estimatedEmg['ankle']['ext']['Mn'],'r')
			ax[i1,i2].plot(estimatedEmg['ankle']['flex']['Mn'],'b')
			ax[i1,i2].xaxis.set_ticklabels([])
			ax[i1,i2].yaxis.set_ticklabels([])
			ax[i1,i2].xaxis.set_ticks([])
			ax[i1,i2].yaxis.set_ticks([])
			if i2==0:ax[i1,i2].set_ylabel("w1 \n"+str(w1))
			if i1==weights_1.size-1:ax[i1,i2].set_xlabel("w2 = "+str(w2))
	plt.show()

if __name__ == '__main__':
	main()