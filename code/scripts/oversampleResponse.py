import argparse
import sys
sys.path.append('../code')
import subprocess
import matplotlib.pyplot as plt
import scipy as sp
from scipy import interpolate as ip
import numpy as np
import os
import fnmatch
import time
import pickle
from tools import general_tools as gt
from scipy.interpolate import spline

pathToResults = "../../comp_up"

def main():
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

	fig, ax = plt.subplots(2, 5,figsize=(16,9),sharex='col',sharey='col')
	for i in range(5):
		x_new = np.linspace(0, 100, 10000)
		x_old = np.linspace(0, 100, 100)
		#print len(x_old)
		#print len(taEmg[i])
		cur_ta = taEmg[i]
		new_cur_ta = np.interp(x_new,x_old,cur_ta)
		cur_gm = gmEmg[i]
		new_cur_gm = np.interp(x_new,x_old,cur_gm)
		#lol = ip.interp1d(x_old,cur_ta)
		#lol_2 = ip.interp1d(x_old,cur_gm)
		#new_cur_ta = lol(x_new)
		#new_cur_gm = lol_2(x_new)
		new_cur_ta = spline(x_old,cur_ta,x_new)
		new_cur_gm = spline(x_old,cur_gm,x_new)
		ax[0,i].plot(new_cur_ta[5000:7000])
		ax[1,i].plot(new_cur_gm[5000:7000])
	figName = "wat"
	plt.savefig(pathToResults+figName, format="pdf",transparent=True)


if __name__ == '__main__':
	main()
