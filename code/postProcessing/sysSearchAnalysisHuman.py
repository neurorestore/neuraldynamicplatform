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
import warnings

def main():
	""" Open the plot of a Forward systematic search analysis. """

	if len(sys.argv)<2:
		print "Error in arguments. Required arguments:"
		print "\t folderName/"
		sys.exit(-1)

	folderName = sys.argv[1]
	extMuscle = "GL"
	flexMuscle = "TA"

	eesAmplitudes = [1,235,250,270]
	eesLowAmplitudes = ["%0.15_0_0"] #  change tp ["0.15_0_0"]
	eesFrequency = 59
	eesHighFrequency = 600

	delays = [2,16]

	weights_1 = 0.018*np.arange(1,2.01,0.25) #in templateFrwSimHuman.txt: Iaf->Mn
	weights_2 = 0.011*np.arange(1,4.01,0.25) #in templateFrwSimHuman.txt: Iaf->IaInt
	weights_3 = 0.011*np.arange(0.5,3.01,0.25) #in templateFrwSimHuman.txt: IIf->IIExInt & IIf->IaInt

	niceTrials = np.zeros([weights_1.size,weights_2.size,weights_3.size],dtype=bool)

	iD, delay = 0,2
	i,eesAmplitude = 3,250
	i,eesAmplitude = 4,270

	for i1,w1 in enumerate(weights_1):
		for i2,w2 in enumerate(weights_2):
			for i3,w3 in enumerate(weights_3):

				pattern = "*"+str(eesFrequency)+"Hz_Delay_"+str(delay)+\
					"ms_human_Tonic_w1_"+str(w1)+"_w2_"+str(w2)+"_w3_"+str(w3)+"_"+str(eesAmplitude)+"_sysHuman.p"
				meanFr = load_results(pattern,"../../results/"+folderName)
				if meanFr:
					alternationMn,meanFrMn,_ = ppt.computeAlternationScore(meanFr[flexMuscle]['Mn'],meanFr[extMuscle]['Mn'])

				# (the meanfr could be lower)
				if  np.mean(meanFr[flexMuscle]['Mn'])>5 and np.mean(meanFr[extMuscle]['Mn'])>5 and alternationMn>0.7:
					niceTrials[i1,i2,i3] = True
					print "\n\n\nmean fr:%d\n\nalternation:%f "%(meanFrMn,alternationMn)

					# pattern = "*"+str(eesFrequency)+"Hz_Delay_"+str(16)+\
					# 	"ms_human_Tonic_w1_"+str(w1)+"_w2_"+str(w2)+"_w3_"+str(w3)+"_"+str(eesAmplitude)+"_sysHuman.p"
					# meanFr = load_results(pattern,"../../results/"+folderName)
					# if meanFr:
					# 	alternationMn16,meanFrMn16,_ = ppt.computeAlternationScore(meanFr[flexMuscle]['Mn'],meanFr[extMuscle]['Mn'])
					# 	if alternationMn16+0.05<alternationMn:
					# 		niceTrials[i1,i2,i3] = True
					# 		print "\n\n\nmean fr:%d\n\nalternation:%f "%(meanFrMn,alternationMn)


	i1s,i2s,i3s =np.nonzero(niceTrials)

	fig,ax = plt.subplots(1,3,figsize=(16,9))
	print i1s
	print i2s
	print i3s
	ax[0].hist(i1s,range(weights_1.size+1),(0,weights_1.size))
	ax[0].set_xticks(np.arange(0,weights_1.size)+0.5)
	ax[0].set_xticklabels(weights_1)
	ax[1].hist(i2s,range(weights_2.size+1),(0,weights_2.size))
	ax[1].set_xticks(np.arange(0,weights_2.size)+0.5)
	ax[1].set_xticklabels(weights_2)
	ax[2].hist(i3s,range(weights_3.size+1),(0,weights_3.size))
	ax[2].set_xticks(np.arange(0,weights_3.size)+0.5)
	ax[2].set_xticklabels(weights_3)
	plt.show()

	count=0
	for i1,i2,i3 in zip(i1s,i2s,i3s):
		fig,ax = plt.subplots(len(eesAmplitudes)+len(eesLowAmplitudes),2,figsize=(16,9))
		fig.suptitle("w1:%f w2:%f w3:%f amplitude:%d"%(weights_1[i1],weights_2[i2],weights_3[i3],eesAmplitude),fontsize=14)

		for i,delay in enumerate(delays):

			for j,eesAmplitude in enumerate(eesAmplitudes):
				patternTonic = "*"+str(eesFrequency)+"Hz_Delay_"+str(delay)+\
					"ms_human_Tonic_w1_"+str(weights_1[i1])+"_w2_"+str(weights_2[i2])+"_w3_"+str(weights_3[i3])+"_"+str(eesAmplitude)+"_sysHuman.p"
				meanFr = load_results(patternTonic,"../../results/"+folderName)
				if meanFr:
					ax[j,i].plot(meanFr[extMuscle]['Mn'],'r')
					ax[j,i].plot(meanFr[extMuscle]['IaInt'],'-.r')
					ax[j,i].plot(meanFr[flexMuscle]['Mn'],'b')
					ax[j,i].plot(meanFr[flexMuscle]['IaInt'],'-.b')
			for j,eesLowAmplitude in enumerate(eesLowAmplitudes):
				patternHFLA = "*"+str(eesHighFrequency)+"Hz_Delay_"+str(delay)+\
					"ms_human_HFLA_"+eesLowAmplitude+"_w1_"+str(weights_1[i1])+"_w2_"+str(weights_2[i2])+"_w3_"+str(weights_3[i3])+"__sysHuman.p"
				meanFr = load_results(patternHFLA,"../../results/"+folderName)
				if meanFr:
					ax[j+len(eesAmplitudes),i].plot(meanFr[extMuscle]['Mn'],'r')
					ax[j+len(eesAmplitudes),i].plot(meanFr[extMuscle]['IaInt'],'-.r')
					ax[j+len(eesAmplitudes),i].plot(meanFr[flexMuscle]['Mn'],'b')
					ax[j+len(eesAmplitudes),i].plot(meanFr[flexMuscle]['IaInt'],'-.b')
					# print "TODO: add statistics on plots"

		plt.show(block=False)
		count+=1
		if count==10:
			raw_input("press a key to continue")
			for i in range(count):plt.close()
			count=0
	plt.show()

				# fileName = "Delay_"+str(delay)+"ms_human_w1_"+str(w1)+"_w2_"+str(w2)+"_w3_"+str(w3)+"_sysHuman.pdf"
				# plt.savefig("../../results/"+folderName+fileName, format="pdf",transparent=True)
				# plt.show(block=False)
				# plt.pause(1)
				# plt.close()

def load_results(pattern,resultsFolder):
	fileToLoad = gt.find(pattern, resultsFolder)
	if not fileToLoad:
		warnings.warn('\tfile with pattern: '+pattern+' not found')
		return None
	else:
		print "\tloading file: "+fileToLoad[0]
		with open(fileToLoad[0], 'r') as pickle_file:
			_ = pickle.load(pickle_file)
			meanFr = pickle.load(pickle_file)
		return meanFr

if __name__ == '__main__':
	main()
