import sys
import pickle
import numpy as np
import subprocess
import matplotlib.pyplot as plt
plt.rcParams.update({'font.size': 6})
import sys
sys.path.append('../code')
from tools import general_tools as gt
from tools import post_processing_tools as ppt

def main():
	""" Open the plot of a Forward systematic search analysis. """

	if len(sys.argv)<2:
		print "Error in arguments. Required arguments:"
		print "\t folderName/"
		sys.exit(-1)

	folderName = sys.argv[1]
	eesFrequency = 40
	eesAmplitude = 235
	delays=[2,16]
	weightMultiplier = 1./np.linspace(1.,0.25,10)
	weights_1 = 0.018/np.linspace(1.,0.25,10) #in templateFrwSimHuman.txt: Iaf->Mn
	weights_2 = 0.011/np.linspace(1.,0.25,10) #in templateFrwSimHuman.txt: Iaf & IIf->IaInt
	weights_3 = 0.011/np.linspace(1.,0.25,10) #in templateFrwSimHuman.txt: IIf->IIExInt

	alternationMn = -1*np.ones([len(delays),weights_1.size,weights_2.size])
	meanFrMn =  -1*np.ones([len(delays),weights_1.size,weights_2.size])
	meanFrRatioMn =  -1*np.ones([len(delays),weights_1.size,weights_2.size])
	alternationIaInt = -1*np.ones([len(delays),weights_1.size,weights_2.size])
	meanFrIaInt =  -1*np.ones([len(delays),weights_1.size,weights_2.size])
	meanFrRatioIaInt =  -1*np.ones([len(delays),weights_1.size,weights_2.size])

	for iD, delay in enumerate(delays):
		for i1,ws in enumerate(zip(weights_1,weights_3)):
			w1,w3 = ws
			for i2,w2 in enumerate(weights_2):
				pattern = "*"+str(eesFrequency)+"Hz_Delay_"+str(delay)+\
					"ms_human__w1_"+str(w1)+"_w2_"+str(w2)+"_w3_"+str(w3)+"_"+str(eesAmplitude)+"_sysHuman.p"
				fileToLoad = gt.find(pattern, "../../results/"+folderName)
				if not fileToLoad:
					print alternationMn
					raise(Exception('\tfile with pattern: '+pattern+' not found'))

				print "\tloading file: "+fileToLoad[0]
				with open(fileToLoad[0], 'r') as pickle_file:
					estimatedEmg = pickle.load(pickle_file)
					meanFr = pickle.load(pickle_file)
				alternationMn[iD,i1,i2],meanFrMn[iD,i1,i2],meanFrRatioMn[iD,i1,i2] = ppt.computeAlternationScore(meanFr['TA']['Mn'],meanFr['SOL']['Mn'])
				alternationIaInt[iD,i1,i2],meanFrIaInt[iD,i1,i2],meanFrRatioIaInt[iD,i1,i2] = ppt.computeAlternationScore(meanFr['TA']['IaInt'],meanFr['SOL']['IaInt'])



# Load rat control data



def plot_all_emg(day,eesAmplitude,eesFrequency,delay,weights_1,weights_2,weights_3,weightMultiplier):
	""" Plots the EMG signals for the different parameters. """
	fig, ax = plt.subplots(weights_1.size,weights_2.size ,figsize=(16,9),sharex='col',sharey='col')
	for i1,ws in enumerate(zip(weights_1,weights_3)):
		w1,w3 = ws
		for i2,w2 in enumerate(weights_2):
			pattern = "*"+str(eesFrequency)+"Hz_Delay_"+str(delay)+\
				"ms_human__w1_"+str(w1)+"_w2_"+str(w2)+"_w3_"+str(w3)+"_"+str(eesAmplitude)+"_sysHuman.p"
			fileToLoad = gt.find(pattern, "../../results/sysHumanVsRat/")
			if not fileToLoad:
				plt.show()
				raise(Exception('\tfile with pattern: '+pattern+' not found'))

			print "found file: "+fileToLoad[0]
			with open(fileToLoad[0], 'r') as pickle_file:
				estimatedEmg = pickle.load(pickle_file)
			ax[i1,i2].plot(estimatedEmg['SOL']['Mn'],'r')
			ax[i1,i2].plot(estimatedEmg['TA']['Mn'],'b')
			ax[i1,i2].xaxis.set_ticklabels([])
			ax[i1,i2].yaxis.set_ticklabels([])
			ax[i1,i2].xaxis.set_ticks([])
			ax[i1,i2].yaxis.set_ticks([])
			if i2==0:ax[i1,i2].set_ylabel("wMult \n %1.3f"%(weightMultiplier[i1]))
			if i1==weights_1.size-1:ax[i1,i2].set_xlabel("w2 = "+str(w2))

if __name__ == '__main__':
	main()
	#TODO look at iaint fr - maybe we should decrease its power to the mn to see a stronger effect
