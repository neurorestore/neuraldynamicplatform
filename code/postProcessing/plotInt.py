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
	resultsFolder = "../../results/"
	toLoad = "2018_09_24_static_reflex_recording_min0.8_max1.5batchSRR_seedn_0__SS_RORa_w1_0.0_w2_-0.01_w3_0.022_sr.p"
	meanFr = load_results(toLoad, resultsFolder)


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
