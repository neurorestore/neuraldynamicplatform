from scipy.signal import butter, lfilter
import numpy as np
from collections import Counter
import seed_handler as sh
sh.set_seed()

def filter_data(data,dt,lowCut=20,highCut=500,order=5):
	nyq = 0.5 * (1000./dt)
	low = lowCut / nyq
	high = highCut / nyq
	b, a = butter(order, [low, high], btype='band')
	filteredData = np.array(lfilter(b, a, data))
	return filteredData

def compute_envelope(data,dt,lowCut=3,highCut=20,order=5):
	# Note the dt has to be in ms!
	# high pass
	nyq = 0.5 * (1000./dt)
	low = lowCut / nyq
	b, a = butter(order, low, btype='highpass')
	temp = np.array(lfilter(b, a,data))
	# absolute value
	absTemp = np.abs(temp)
	# low pass
	high = highCut / nyq
	b, a = butter(order, high, btype='lowpass')
	envelope = np.array(lfilter(b, a,absTemp))
	# Cut lower val than 0
	envelope[envelope<0]=0
	# Normalize
	temp = envelope-envelope.min()
	normEnvelope = temp/temp.max()
	return normEnvelope

def binary_majority_voting(data,nVotes):
	filteredData = []
	state = data[0]
	for i in range(len(data)-nVotes):
		if state == data[i]: filteredData.append(data[i])
		else:
			window = Counter(data[i:i+nVotes])
			majority = window.most_common(1)[0][0]
			filteredData.append(majority)
			if state != majority: state = majority

	# last samples
	for i in range(nVotes):
		filteredData.append(data[i-nVotes])
	return np.array(filteredData)
