import sys
import pickle
import numpy as np
import subprocess

def main():
	""" Analyse the results of a Forward systematic search. """

	if len(sys.argv)<3:
		print "Error in arguments. Required arguments:"
		print "\t pathToResults/day (YYYY_MM_DD)"
		print "\t 0-1 to open or not the results."

	pathToResultsDay = sys.argv[1]
	plot = bool(int(sys.argv[2]))
	
	eesFrequencies = [0,29,50]
	delays = [2,25]
	if "2016_01_19" in pathToResultsDay:
		weights_1 = np.linspace(0.004,0.04,10)
		weights_2 = np.linspace(-0.025,-0.0025,10)
	elif "2016_01_20" in pathToResultsDay:
		weights_1 = np.linspace(0.008,0.02,20)
		weights_2 = np.linspace(-0.01,-0.001,20)

	alternation = {}
	meanFrs = {}
	meanFrRatio = {}
	for eesFrequency in eesFrequencies:
		alternation[str(eesFrequency)]={}
		meanFrs[str(eesFrequency)]={}
		meanFrRatio[str(eesFrequency)]={}
		for delay in delays:
			alternation[str(eesFrequency)][str(delay)]=-1*np.ones([weights_1.size,weights_2.size,])
			meanFrs[str(eesFrequency)][str(delay)]=-1*np.ones([weights_1.size,weights_2.size,])
			meanFrRatio[str(eesFrequency)][str(delay)]=-1*np.ones([weights_1.size,weights_2.size,])
			for i1,w1 in enumerate(weights_1):
				for i2,w2 in enumerate(weights_2):
					fileToLoad = pathToResultsDay + "_FS_EES_235uA_"+str(eesFrequency)+"Hz_Delay_"+str(delay)+\
						"ms_w1_"+str(w1)+"_w2_"+str(w2)
					alternationTemp,meanFrTemp,meanFrRatioTemp = computePhasicity(fileToLoad)
					alternation[str(eesFrequency)][str(delay)][i1,i2] = alternationTemp
					meanFrs[str(eesFrequency)][str(delay)][i1,i2] = meanFrTemp
					meanFrRatio[str(eesFrequency)][str(delay)][i1,i2] = meanFrRatioTemp

	# Find the indexes that leads to a low energy when ees is 0 and delay is 2
	# Between these find the indexes that leads to nice alternation and decent 
	# meanFrs/meanFrRatio when ees is at 29
	maxFrThr0 =5
	altThr29=0.9
	minFrThr29 = 5
	ratioThrMax29 = 1
	ratioThrMin29 = 0.5
	condition = (meanFrs['0']['2'][:]<maxFrThr0)\
				& (meanFrs['29']['2'][:]>minFrThr29)\
				& (alternation['29']['2'][:]>altThr29)\
				& (meanFrRatio['29']['2'][:]>ratioThrMin29)\
				& (meanFrRatio['29']['2'][:]<ratioThrMax29)
	ws1,ws2 = np.where(condition)
	for w1,w2 in zip(ws1,ws2):
		print "w1:{0:.4f}, w2:{1:.4f},\tmean_fr0: {2:.2f}, mean_fr29: {3:.2f},\talternation29: {4:.2f}, rati029: {5:.2f}".format(\
			weights_1[w1],weights_2[w2],meanFrs['0']['2'][w1,w2],meanFrs['29']['2'][w1,w2],alternation['29']['2'][w1,w2],\
			meanFrRatio['29']['2'][w1,w2])
		if plot:
			fileToLoad=[]
			fileToLoad.append(pathToResultsDay + "_FS_EES_235uA_"+str(0)+"Hz_Delay_"+str(2)\
				+"ms_w1_"+str(weights_1[w1])+"_w2_"+str(weights_2[w2]))
			fileToLoad.append(pathToResultsDay + "_FS_EES_235uA_"+str(29)+"Hz_Delay_"+str(2)\
				+"ms_w1_"+str(weights_1[w1])+"_w2_"+str(weights_2[w2]))
			fileToLoad.append(pathToResultsDay + "_FS_EES_235uA_"+str(29)+"Hz_Delay_"+str(25)\
				+"ms_w1_"+str(weights_1[w1])+"_w2_"+str(weights_2[w2]))
			fileToLoad.append(pathToResultsDay + "_FS_EES_235uA_"+str(50)+"Hz_Delay_"+str(2)\
				+"ms_w1_"+str(weights_1[w1])+"_w2_"+str(weights_2[w2]))
			fileToLoad.append(pathToResultsDay + "_FS_EES_235uA_"+str(50)+"Hz_Delay_"+str(25)\
				+"ms_w1_"+str(weights_1[w1])+"_w2_"+str(weights_2[w2]))
			for image in fileToLoad:
				openImage = "open "+image+".pdf"
				preview = subprocess.call(openImage,shell=True)



	# Now check what we have with a delay of 25
	# Find the nice ones
	# Find the bad ones
	# Next: check if with high freq stim the badOnes become niceOnes --> paper :)



def computePhasicity(fileToLoad):
	""" Computes the phasicity score for a given file. """

	with open(fileToLoad+".p", 'r') as pickle_file:
		estimatedEmg = pickle.load(pickle_file)
		meanFr = pickle.load(pickle_file)


	flexMnFr = np.array(meanFr['ankle']['flex']['Mn'])
	extMnFr = np.array(meanFr['ankle']['ext']['Mn'])
	if flexMnFr.size<extMnFr.size:
		flexMnFr = np.append(flexMnFr,np.zeros(extMnFr.size-flexMnFr.size))
	elif flexMnFr.size>extMnFr.size:
		extMnFr = np.append(extMnFr,np.zeros(flexMnFr.size-extMnFr.size))

	# Compute the overall mean fr
	flexMeanFr = flexMnFr.mean()
	extMeanFr = extMnFr.mean()
	meanFr = np.mean([flexMeanFr,extMeanFr])
	meanFrRatio = flexMeanFr/extMeanFr

	# Normalise firing rates
	flexMnFr = flexMnFr-flexMnFr.min()
	flexMnFr = flexMnFr/flexMnFr.max()
	extMnFr = extMnFr-extMnFr.min()
	extMnFr = extMnFr/extMnFr.max()

	alternation = ((1-flexMnFr*extMnFr)/extMnFr.size).sum()

	#Duration ratio flex/ext from the same kinematic data used for Forward - Done in Matlab
	# durRatio = 0.45
	# ratioSimilarity = extMnFr.sum()*durRatio/flexMnFr.sum()
	# phasicity = ratioSimilarity*alternation
	
	return alternation,meanFr,meanFrRatio

if __name__ == '__main__':
	main()
