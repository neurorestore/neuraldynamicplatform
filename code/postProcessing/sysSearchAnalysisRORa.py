import sys
import pickle
import numpy as np
import subprocess
from tools import general_tools as gt

def main():
	""" Analyse the results of a Forward systematic search. """

	if len(sys.argv)<3:
		print "Error in arguments. Required arguments:"
		print "\t resultsFolder"
		print "\t 0-1 to open or not the results."

	pathToResultsDay = sys.argv[1]
	plot = bool(int(sys.argv[2]))

	weights_1 = np.round(np.linspace(0.002,0.02,6),3)
	weights_2 = np.round(np.linspace(0.002,0.02,6),3)
	weights_3 = np.round(np.linspace(0.00,0.04,8),3)
	weights_4 = np.round(np.linspace(0.00,-0.0075,3),3)

	alternation,meanFrs,meanFrRatio,_ = extract_results(weights_1,weights_2,weights_3,weights_4,pathToResultsDay)


	# Find the indexes that leads to a good alternation wiht 5HT and a bad alternation
	# when no drug is simulated
	# Between these find the indexes that leads to nice alternation and decent
	# meanFrs/meanFrRatio when ees is at 29
	minAltThrDrug = 0.8
	minFrThrDrug = 10
	ratioThrMaxDrug = 1
	ratioThrMinDrug = 0
	maxFrThrNoDrug = 10


	print np.sum(alternation['drug'][:]>minAltThrDrug)
	print np.sum(meanFrRatio['drug'][:]>ratioThrMinDrug)
	print np.sum(meanFrRatio['drug'][:]<ratioThrMaxDrug)
	print np.sum(meanFrs['noDrug'][:]<maxFrThrNoDrug)

	condition = (alternation['drug'][:]>minAltThrDrug)\
				& (meanFrRatio['drug'][:]>ratioThrMinDrug)\
				& (meanFrRatio['drug'][:]<ratioThrMaxDrug)\
				& (meanFrs['noDrug'][:]<maxFrThrNoDrug)\


	ws1,ws2,ws3,ws4 = np.where(condition)
	print "\t{0:d} results found".format(len(ws1))
	for w1,w2,w3,w4 in zip(ws1,ws2,ws3,ws4):
		print "w1:{0:.4f}, w2:{1:.4f}, w3:{2:.4f}, w4:{3:.4f},\talternation_noDrug: {4:.2f}, meanFrs_drug: {5:.2f},\talternation_drug: {6:.2f}, ratio_drug: {7:.2f}".format(\
			weights_1[w1],weights_2[w2],weights_3[w3],weights_4[w4],alternation["noDrug"][w1,w2,w3,w4],meanFrs["drug"][w1,w2,w3,w4],alternation["drug"][w1,w2,w3,w4],\
			meanFrRatio["drug"][w1,w2,w3,w4])
		if plot:
			fileToLoad=[]
			pattern = "*"+str(weights_1[w1])+"_w2_"+str(weights_2[w2])+"_w3_"+str(weights_3[w3])+"_w4_"+str(weights_4[w4])+"_fs_artificial.pdf"
			fileToLoadNoDrug = gt.find(pattern, pathToResultsDay)
			pattern = "*"+str(weights_1[w1])+"_w2_"+str(weights_2[w2])+"_w3_"+str(weights_3[w3])+"_w4_"+str(weights_4[w4])+"_fs_artificial_5HT.pdf"
			fileToLoadDrug = gt.find(pattern, pathToResultsDay)
			for image in [fileToLoadNoDrug[0],fileToLoadDrug[0]]:
				print image
				openImage = "open "+image
				preview = subprocess.call(openImage,shell=True)
			raw_input("Press Enter to continue...")

def extract_results(weights_1,weights_2,weights_3,weights_4,pathToResultsDay):
	alternation = {}
	meanFrs = {}
	meanFrRatio = {}
	firingRate={}
	alternation["noDrug"] = -1*np.ones([weights_1.size,weights_2.size,weights_3.size,weights_4.size])
	meanFrs["noDrug"] = -1*np.ones([weights_1.size,weights_2.size,weights_3.size,weights_4.size])
	meanFrRatio["noDrug"] = -1*np.ones([weights_1.size,weights_2.size,weights_3.size,weights_4.size])
	firingRate["noDrug"] = -1*np.ones([weights_1.size,weights_2.size,weights_3.size,weights_4.size],dtype=object)

	alternation["drug"] = -1*np.ones([weights_1.size,weights_2.size,weights_3.size,weights_4.size])
	meanFrs["drug"] = -1*np.ones([weights_1.size,weights_2.size,weights_3.size,weights_4.size])
	meanFrRatio["drug"] = -1*np.ones([weights_1.size,weights_2.size,weights_3.size,weights_4.size])
	firingRate["drug"] = -1*np.ones([weights_1.size,weights_2.size,weights_3.size,weights_4.size],dtype=object)

	nSim = len(weights_1)*len(weights_2)*len(weights_3)*len(weights_4)
	count=0.
	percLastPrint=0.
	printPeriod = 0.01
	extractedResults = gt.find("EMGdata.p", pathToResultsDay)
	if not extractedResults:
		for i1,w1 in enumerate(weights_1):
			for i2,w2 in enumerate(weights_2):
				for i3,w3 in enumerate(weights_3):
					for i4,w4 in enumerate(weights_4):
						pattern = "*"+str(w1)+"_w2_"+str(w2)+"_w3_"+str(w3)+"_w4_"+str(w4)+"_fs_artificial.p"
						fileToLoadNoDrug = gt.find(pattern, pathToResultsDay)
						pattern = "*"+str(w1)+"_w2_"+str(w2)+"_w3_"+str(w3)+"_w4_"+str(w4)+"_fs_artificial_5HT.p"
						fileToLoadDrug = gt.find(pattern, pathToResultsDay)
						alternation["noDrug"][i1,i2,i3,i4],meanFrs["noDrug"][i1,i2,i3,i4],meanFrRatio["noDrug"][i1,i2,i3,i4],firingRate["noDrug"][i1,i2,i3,i4] = computePhasicity(fileToLoadNoDrug[0])
						alternation["drug"][i1,i2,i3,i4],meanFrs["drug"][i1,i2,i3,i4],meanFrRatio["drug"][i1,i2,i3,i4],firingRate["drug"][i1,i2,i3,i4] = computePhasicity(fileToLoadDrug[0])
						count+=1
						if count/nSim-percLastPrint>=printPeriod:
							percLastPrint=count/nSim
							print str(round(count/nSim*100))+"% of simulations extracted..."
		with open(pathToResultsDay+"EMGdata.p", 'w') as pickle_file:
			pickle.dump(alternation,pickle_file)
			pickle.dump(meanFrs,pickle_file)
			pickle.dump(meanFrRatio,pickle_file)
			pickle.dump(firingRate,pickle_file)
	else:
		with open(extractedResults[0], 'r') as pickle_file:
			alternation = pickle.load(pickle_file)
			meanFrs = pickle.load(pickle_file)
			meanFrRatio = pickle.load(pickle_file)
			firingRate = pickle.load(pickle_file)
	return alternation,meanFrs,meanFrRatio,firingRate

def computePhasicity(fileToLoad):
	""" Computes the phasicity score for a given file. """

	with open(fileToLoad, 'r') as pickle_file:
		estimatedEmg = pickle.load(pickle_file)
		meanFr = pickle.load(pickle_file)


	flexMnFr = np.array(meanFr['TA']['Mn'])
	extMnFr = np.array(meanFr['GM']['Mn'])
	if flexMnFr.size<extMnFr.size:
		flexMnFr = np.append(flexMnFr,np.zeros(extMnFr.size-flexMnFr.size))
	elif flexMnFr.size>extMnFr.size:
		extMnFr = np.append(extMnFr,np.zeros(flexMnFr.size-extMnFr.size))
	firingRate = meanFr

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

	return alternation,meanFr,meanFrRatio,firingRate

if __name__ == '__main__':
	main()
