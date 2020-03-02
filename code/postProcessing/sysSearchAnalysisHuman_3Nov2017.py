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
import time

def main():

	folderName = "Results_sysHumanGod_3Nov2017"
	pathToResults = "../../results/"+folderName+"/analyses/"
	extMuscle = "SOL"
	flexMuscle = "TA"

	gaitCyclesFileName = "./generateForSimInputs/output/humanGaitCyclesB13.p"
	with open(gaitCyclesFileName, 'r') as pickle_file:
		heelStrikes = pickle.load(pickle_file)
		footOffs = pickle.load(pickle_file)
	totSimTime = 4000

	eesAmplitudes = [250,270]
	eesFrequencies = [20,60]
	delays = [2,16]


	weights_1 = 0.014*np.arange(1,2.01,0.25) #in templateFrwSimHuman.txt: Iaf->Mn
	weights_3 = 0.011*np.arange(1,2.01,0.25) #in templateFrwSimHuman.txt: IIf->ExcInt

	weights_2 = 0.011*np.arange(1,4.01,0.33) #in templateFrwSimHuman.txt: Iaf->IaInt
	weights_4 = 0.011*np.arange(1,4.01,0.33) #in templateFrwSimHuman.txt: IIf->IaInt


	""" Step 1: find nice trials """
	niceTrials = np.zeros([weights_1.size,weights_2.size,weights_4.size],dtype=bool)
	print niceTrials.shape

	iD, delay = 0,2
	i,eesAmplitude = 3,250
	# i,eesAmplitude = 4,270
	eesFrequency = 60

	for i1,w1_3 in enumerate(zip(weights_1,weights_3)):
		w1,w3 = w1_3
		for i2,w2 in enumerate(weights_2):
			for i3,w4 in enumerate(weights_4):

				pattern = "*"+str(eesFrequency)+"Hz_Delay_"+str(delay)+\
					"ms_human_Tonic_w1_"+str(w1)+"_w2_"+str(w2)+"_w3_"+str(w3)+"_w4_"+str(w4)+"_"+str(eesAmplitude)+"_sysHumanGod.p"
				meanFr = load_results(pattern,"../../results/"+folderName)
				if meanFr:
					alternationMn,meanFrMn,_ = ppt.computeAlternationScore(meanFr[flexMuscle]['Mn'],meanFr[extMuscle]['Mn'])

				# (the meanfr could be lower)
				if  np.percentile(meanFr[flexMuscle]['Mn'],90)>5 and np.percentile(meanFr[extMuscle]['Mn'],90)>5 and alternationMn>0.9:
					niceTrials[i1,i2,i3] = True
					print np.percentile(meanFr[flexMuscle]['Mn'],90),np.percentile(meanFr[extMuscle]['Mn'],90)
					print "\n\n\nmean fr:%d\n\nalternation:%f "%(meanFrMn,alternationMn)

					# pattern = "*"+str(eesFrequency)+"Hz_Delay_"+str(16)+\
					# 	"ms_human_Tonic_w1_"+str(w1)+"_w2_"+str(w2)+"_w3_"+str(w3)+"_w4_"+str(w4)+"_"+str(eesAmplitude)+"_sysHumanGod.p"
					# meanFr = load_results(pattern,"../../results/"+folderName)
					# if meanFr:
					# 	alternationMn16,meanFrMn16,_ = ppt.computeAlternationScore(meanFr[flexMuscle]['Mn'],meanFr[extMuscle]['Mn'])
					# 	if alternationMn16+0.05<alternationMn:
					# 		niceTrials[i1,i2,i3] = True
					# 		print "\n\n\nmean fr:%d\n\nalternation:%f "%(meanFrMn,alternationMn)

	# niceTrials = np.zeros([weights_1.size,weights_2.size,weights_4.size],dtype=bool)
	# niceTrials[1,:,:]=True
	i1s,i2s,i3s =np.nonzero(niceTrials)

	fig,ax = plt.subplots(1,4,figsize=(16,9),sharey=True)
	print i1s
	print i2s
	print i3s
	ax[0].hist(i1s,range(weights_1.size+1),(0,weights_1.size))
	ax[0].set_xticks(np.arange(0,weights_1.size)+0.5)
	ax[0].set_xticklabels(weights_1)
	ax[0].set_xlabel('w1')
	ax[1].hist(i1s,range(weights_3.size+1),(0,weights_3.size))
	ax[1].set_xticks(np.arange(0,weights_3.size)+0.5)
	ax[1].set_xticklabels(weights_3)
	ax[1].set_xlabel('w3')
	ax[2].hist(i2s,range(weights_2.size+1),(0,weights_2.size))
	ax[2].set_xticks(np.arange(0,weights_2.size)+0.5)
	ax[2].set_xticklabels(weights_2)
	ax[2].set_xlabel('w2')
	ax[3].hist(i3s,range(weights_4.size+1),(0,weights_4.size))
	ax[3].set_xticks(np.arange(0,weights_4.size)+0.5)
	ax[3].set_xticklabels(weights_4)
	ax[3].set_xlabel('w4')
	figName = time.strftime("/%Y_%m_%d_weightsHists_delay_"+str(delay)+"_freq_"+str(eesFrequency)+"_amp_"+str(eesAmplitude)+".pdf")
	plt.savefig(pathToResults+figName, format="pdf",transparent=True)

	plt.show(block=True)
	plt.pause(1)

	""" Step 2: plot nice trials for different fre and amp and del """
	# i1s,i2s,i3s =np.nonzero(niceTrials)
	# redAi = "#e9342f"
	# bluAi = "#00aaeb"
	# redDarkAi = "#661311"
	# bluDarkAi = "#023c52"
	# count=0
	# for i1,i2,i3 in zip(i1s,i2s,i3s):
	# 	fig,ax = plt.subplots(len(eesAmplitudes)*len(eesFrequencies),2,figsize=(16,9))
	# 	name = "w1:%f w2:%f w3:%f w4:%f"%(weights_1[i1],weights_2[i2],weights_3[i1],weights_4[i3])
	# 	fig.suptitle(name,fontsize=14)
	#
	# 	for i,delay in enumerate(delays):
	#
	# 		for j,eesAmplitude in enumerate(eesAmplitudes):
	# 			for k,eesFrequency in enumerate(eesFrequencies):
	# 				pattern = "*"+str(eesFrequency)+"Hz_Delay_"+str(delay)+\
	# 					"ms_human_Tonic_w1_"+str(weights_1[i1])+"_w2_"+str(weights_2[i2])+"_w3_"+str(weights_3[i1])+"_w4_"+str(weights_4[i3])+"_"+str(eesAmplitude)+"_sysHumanGod.p"
	# 				meanFr = load_results(pattern,"../../results/"+folderName)
	# 				if meanFr:
	# 					# get gait cycles
	# 					if not 'heelStrikeSamples' in locals():
	# 						nSamples = len(meanFr[extMuscle]["Mn"])
	# 						dtMeanFr = float(totSimTime)/nSamples
	# 						heelStrikeSamples = [int(x) for x in heelStrikes*1000./dtMeanFr]
	# 						footOffSamples = [int(x) for x in footOffs*1000./dtMeanFr]
	# 						samples = range(nSamples)
	# 						stance = np.zeros(nSamples).astype(bool)
	# 						for strike,off in zip(heelStrikeSamples,footOffSamples):
	# 							if strike>nSamples: break
	# 							stance[strike:off]=True
	# 					if i==0:
	# 						red = redAi
	# 						blu = bluAi
	# 						lab = "Mn"
	# 					else:
	# 						red = redDarkAi
	# 						blu = bluDarkAi
	# 						lab = "Iaint"
	# 					ax[j*2+k,0].plot(meanFr[extMuscle]['Mn'],color=red)
	# 					ax[j*2+k,0].plot(meanFr[flexMuscle]['Mn'],color=blu)
	# 					ax[j*2+k,0].fill_between(samples, 0, 50, where=stance, facecolor='#b0abab', alpha=0.25)
	#
	# 					ax[j*2+k,1].plot(meanFr[extMuscle]['IaInt'],'-.',color=red)
	# 					ax[j*2+k,1].plot(meanFr[flexMuscle]['IaInt'],'-.',color=blu)
	# 					ax[j*2+k,1].fill_between(samples, 0, 180, where=stance, facecolor='#b0abab', alpha=0.25)
	#
	# 					if i==0: ax[j*2+k,i].set_ylabel("freq: %d amp: %d"%(eesFrequency,eesAmplitude))
	# 					if j==0 and k ==0: ax[j*2+k,i].set_title(lab)
	#
	# 	figName = time.strftime("/%Y_%m_%d_SS_"+name+".pdf")
	# 	plt.savefig(pathToResults+figName, format="pdf",transparent=True)

		# plt.show(block=False)
		# count+=1
		# if count==10:
		# 	raw_input("press a key to continue")
		# 	for i in range(count):plt.close()
		# 	count=0
	# plt.show()



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
