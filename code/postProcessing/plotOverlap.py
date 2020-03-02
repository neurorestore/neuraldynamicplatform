import argparse
import sys
sys.path.append('../code')
import subprocess
import matplotlib.pyplot as plt
import numpy as np
import os
import fnmatch
import time
import pickle
from tools import general_tools as gt

pathToResults = "../../postProcessing"

def main():
	# First load a2a, A08 and Control

	taStat = []
	gmStat = []
	a2a_name = "a2aAgonist"
	A08_name = "A08"
	Control_name = "Control"
	if len(resultFile)>1: print "Warning: multiple result files found!!!"
	with open(resultFile[0], 'r') as pickle_file:
		taSpikes = pickle.load(pickle_file)
		taEmg = pickle.load(pickle_file)
		taStatVal = pickle.load(pickle_file)
		gmSpikes = pickle.load(pickle_file)
		gmEmg = pickle.load(pickle_file)
		gmStatVal = pickle.load(pickle_file)
	taStat.append(taStatVal)
	gmStat.append(gmStatVal)

if __name__ == '__main__':
	main()
