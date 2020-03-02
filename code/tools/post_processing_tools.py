import numpy as np

def computeAlternationScore(flexFr,extFr,phasicityFlag=False):
	""" Computes the phasicity score given two firingRate profiles.
		flexFr and extFr need to be two numpy arrays with the same size.
	"""


	# Compute the overall mean fr
	flexMeanFr = flexFr.mean()
	extMeanFr = extFr.mean()
	meanFr = np.mean([flexMeanFr,extMeanFr])
	meanFrRatio = flexMeanFr/extMeanFr

	# Normalise firing rates
	flexFr = flexFr-flexFr.min()
	flexFr = flexFr/flexFr.max() if flexFr.max()>0 else flexFr
	extFr = extFr-extFr.min()
	extFr = extFr/extFr.max() if extFr.max()>0 else extFr

	alternation = ((1-flexFr*extFr)/extFr.size).sum()
	if not phasicityFlag: return alternation,meanFr,meanFrRatio
	else:

		#Duration ratio flex/ext from the same kinematic data used for Forward - Done in Matlab
		durRatio = 0.45
		ratioSimilarity = extMnFr.sum()*durRatio/flexMnFr.sum()
		phasicity = ratioSimilarity*alternation
		return alternation,meanFr,meanFrRatio,phasicity
