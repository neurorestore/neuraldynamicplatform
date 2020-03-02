import sys
import pickle
import numpy as np
import subprocess
import matplotlib.pyplot as plt

def main():
	mod_file = "../../comp_up/2019_07_08_static_reflex_recording_min0.8_max1.6batchSRR_seedn_0__SS_RORa_w1_0.011_w2_0.005_sr_A08_up.p"
	with open(mod_file,"rb") as cur_file:
		para_1 = pickle.load(cur_file)
		para_2 = pickle.load(cur_file)
		para_3 = pickle.load(cur_file)
		para_4 = pickle.load(cur_file)
		para_5 = pickle.load(cur_file)
		para_6 = pickle.load(cur_file)
	print para_6


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
