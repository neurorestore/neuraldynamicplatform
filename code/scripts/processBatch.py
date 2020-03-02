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

pathToResults = "../../comp_up"

def main():
	taStat_mod = []
	gmStat_mod = []
	name = "batchSRR_seedn_0__SS_RORa_w1_0.011_w2_0.005_sr_A08_up"
	resultFile = gt.find("*"+name+".p",pathToResults)
	if len(resultFile)>1: print "Warning: multiple result files found!!!"
	with open(resultFile[0], 'r') as pickle_file:
		taSpikes = pickle.load(pickle_file)
		taEmg = pickle.load(pickle_file)
		taStatVal = pickle.load(pickle_file)
		gmSpikes = pickle.load(pickle_file)
		gmEmg = pickle.load(pickle_file)
		gmStatVal = pickle.load(pickle_file)
	taStat_mod.append(taStatVal)
	gmStat_mod.append(gmStatVal)

	taStat_con = []
	gmStat_con = []
	name = "batchSRR_seedn_0__SS_RORa_w1_0.011_w2_0.005_sr_Control_no_inhib"
	resultFile = gt.find("*"+name+".p",pathToResults)
	if len(resultFile)>1: print "Warning: multiple result files found!!!"
	with open(resultFile[0], 'r') as pickle_file:
		taSpikes = pickle.load(pickle_file)
		taEmg = pickle.load(pickle_file)
		taStatVal = pickle.load(pickle_file)
		gmSpikes = pickle.load(pickle_file)
		gmEmg = pickle.load(pickle_file)
		gmStatVal = pickle.load(pickle_file)
	taStat_con.append(taStatVal)
	gmStat_con.append(gmStatVal)

	ta_comp = []
	gm_comp = []
	for i in range(len(taStat_mod)):
		ta_comp.append(taStat_mod[i]/taStat_con[i])
		gm_comp.append(gmStat_mod[i]/gmStat_con[i])


	ax = plt.subplot(111)
	ax.bar(0.0, np.array(ta_comp).mean(), 0.2, yerr=np.array(ta_comp).std())
	ax.bar(0.2, np.array(gm_comp).mean(), 0.2, yerr=np.array(gm_comp).std())

	figName = "Comparison_A08_Pro_Increase"
	plt.savefig(pathToResults+figName, format="pdf",transparent=True)


if __name__ == '__main__':
	main()
