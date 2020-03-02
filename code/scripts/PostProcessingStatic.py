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

pathToResults = "../../results"

name = "2018_09_14_static_reflex_recording_min0.8_max1.25batchSRR_seedn_0__SS_RORa_w1_0.011_w2_0.007_w3_0.011_sr.p"
resultFile = gt.find(name,pathToResults)
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
print taStat
