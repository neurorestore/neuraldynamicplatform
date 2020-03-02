import sys
sys.path.append('../code')
import subprocess
import matplotlib.gridspec as gridspec
import numpy as np
import matplotlib.pyplot as plt
import pickle
import fnmatch
import os
from scipy import interpolate
from scipy.interpolate import interp1d
import colormaps as cmaps
from tools import general_tools as gt
import time


pathToResults = "../../results/AffEffModSweap"

def main():
	""" This program launches a parameters systematic search for a computeAfferentsEfferentsModulation.
	The different parameters that are changed over time are directly defined within this main function.
	The program doesn't have to be executed by MPI.
	"""

	# eesAmplitudes = range(200,321,10)
	eesAmplitudes = ["%"+"%.2f_0_0"%(i) for i in np.arange(0,1.01,.05)]
	# eesFrequencies = range(10,1001,20)
	eesFrequencies = np.logspace(1,3,50)
	# nrnStructureFile = "fsSFrFfMnArtMod.txt"
	# nrnStructureFile = "fsSFrFfMnArtModHuman.txt"
	nrnStructureFile = "fsMnArtModHuman.txt"
	# name = "FreqAmpModHuman_0367S"
	name = "FreqAmpModHuman_ArtmodHuman_10msBurst"

	nSim = len(eesFrequencies)*len(eesAmplitudes)
	count=0.
	percLastPrint=0.
	printPeriod = 0.05
	# simTime = 250
	simTime = 15
	species = "human"

	for eesAmplitude in eesAmplitudes:
		for eesFrequency in eesFrequencies:
			filName = name+"_amp_"+str(eesAmplitude)+"_freq_"+str(eesFrequency)
			resultFile = gt.find("*"+filName+".p",pathToResults)
			if not resultFile:
				returnCode = None
				while not returnCode==0:
					program = ['python','scripts/computeAfferentsEfferentsModulation.py',
						str(eesFrequency),str(eesAmplitude),species,nrnStructureFile,name,"--simTime",str(simTime)]
					print " ".join(program)
					forwardSimulation = subprocess.Popen(program, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
					returnCode = None
					while returnCode is None:
						message =  forwardSimulation.stdout.readline().rstrip("\n").split()
						if message != None:print "\t\t"+" ".join(message)+"\t\t"
						returnCode = forwardSimulation.poll()
					if returnCode != 0: print "\t\t\t\t Error n: ",forwardSimulation.poll()," resetting simulation..."
			count+=1
			if count/nSim-percLastPrint>=printPeriod:
				percLastPrint=count/nSim
				print str(round(count/nSim*100))+"% of simulations performed..."
	plot_stats(eesAmplitudes,eesFrequencies,simTime,name)

def plot_stats(eesAmplitudes,eesFrequencies,simTime,name):

	populationFr = {}
	populationFr["MnS"] = np.zeros([len(eesAmplitudes),len(eesFrequencies)])
	# populationFr["MnFf"] = np.zeros([len(eesAmplitudes),len(eesFrequencies)])
	# populationFr["MnFr"] = np.zeros([len(eesAmplitudes),len(eesFrequencies)])
	populationFr["Iaf"] = np.zeros([len(eesAmplitudes),len(eesFrequencies)])

	nActiveCells = {}
	nActiveCells["MnS"] = np.zeros([len(eesAmplitudes),len(eesFrequencies)])
	# nActiveCells["MnFf"] = np.zeros([len(eesAmplitudes),len(eesFrequencies)])
	# nActiveCells["MnFr"] = np.zeros([len(eesAmplitudes),len(eesFrequencies)])
	nActiveCells["Iaf"] = np.zeros([len(eesAmplitudes),len(eesFrequencies)])

	# maxActiveCells= {"MnS":20,"MnFf":20,"MnFr":20,"MnS_MnFf_MnFr":60,"Iaf":60}
	maxActiveCells= {"MnS":169,"Iaf":60}
	for i,eesAmplitude in enumerate(eesAmplitudes):
		for j,eesFrequency in enumerate(eesFrequencies):
			filName = name+"_amp_"+str(eesAmplitude)+"_freq_"+str(eesFrequency)
			resultFile = gt.find("*"+filName+".p",pathToResults)
			if len(resultFile)>1: print "Warning: multiple result files found!!!"
			with open(resultFile[0], 'r') as pickle_file:
				_temp_populationFr = pickle.load(pickle_file)
				_temp_nActiveCells = pickle.load(pickle_file)
				for muscle in _temp_populationFr:
					for cellName in  _temp_populationFr[muscle]:
						populationFr[cellName][i,j] = np.array(_temp_populationFr[muscle][cellName])/(float(simTime)/1000)/maxActiveCells[cellName]
						nActiveCells[cellName][i,j] = _temp_nActiveCells[muscle][cellName]

	# populationFr["MnS_MnFf_MnFr"] = (populationFr["MnS"]+populationFr["MnFf"]+populationFr["MnFr"])/3
	# nActiveCells["MnS_MnFf_MnFr"] = nActiveCells["MnS"]+nActiveCells["MnFf"]+nActiveCells["MnFr"]
	maxFr = {}
	maxFr["Iaf"] = np.max(populationFr["Iaf"])
	maxFr["MnS"] = np.max(populationFr["MnS"])
	# maxFr["MnS"] = np.max([populationFr["MnS"],populationFr["MnFf"],populationFr["MnFr"]])
	# maxFr["MnFf"] = np.max([populationFr["MnS"],populationFr["MnFf"],populationFr["MnFr"]])
	# maxFr["MnFr"] = np.max([populationFr["MnS"],populationFr["MnFf"],populationFr["MnFr"]])
	# maxFr["MnS_MnFf_MnFr"] = np.max([populationFr["MnS"],populationFr["MnFf"],populationFr["MnFr"]])

	ax = []
	sizeFactor = 3
	fig=plt.figure(figsize=(3*sizeFactor,4*sizeFactor))
	gs = gridspec.GridSpec(len(populationFr.keys()),2)
	gs.update(left=0.05, right=0.95, hspace=0.6, wspace=0.1)


	colorMap2 = plt.cm.YlGnBu
	colorMap = plt.cm.YlOrRd
	colorMap.set_bad(color="#20201f")
	colorMap2.set_bad(color="#20201f")
	# colorMap = cmaps.magma
	maxSpikes = np.max([np.max(populationFr[cellName]) for cellName in populationFr])

	cellNames = ["Iaf","MnS"]
	for i,cellName in enumerate(cellNames):
		# Plot on number of spikes
		ax.append(plt.subplot(gs[i,0]))
		data = np.ma.masked_where(populationFr[cellName]==0,populationFr[cellName])
		im = ax[-1].imshow(data, cmap=colorMap, interpolation='nearest',origin="lower",vmin = 0,vmax=maxFr[cellName],aspect='auto')
		ax[-1].set_title("Number of spikes - "+cellName)

		# Move left and bottom spines outward by 10 points
		ax[-1].spines['left'].set_position(('outward', 10))
		ax[-1].spines['bottom'].set_position(('outward', 10))
		# Hide the right and top spines
		ax[-1].spines['right'].set_visible(False)
		ax[-1].spines['top'].set_visible(False)
		# Only show ticks on the left and bottom spines
		ax[-1].yaxis.set_ticks_position('left')
		ax[-1].xaxis.set_ticks_position('bottom')

		ax[-1].set_xticks(range(len(eesFrequencies)))
		ax[-1].set_xticklabels(eesFrequencies)

		ax[-1].set_yticks(range(len(eesAmplitudes)))
		ax[-1].set_yticklabels(eesAmplitudes)

		ax[-1].set_ylabel("Stimulation amplitude \n(% of recruited fibers)")

		fig.colorbar(im, orientation='vertical',label="N spikes")

		# Plot on number of active cells
		ax.append(plt.subplot(gs[i,1]))
		# mask some 'bad' data, in your case you would have: data == 0
		data = np.ma.masked_where(nActiveCells[cellName]==0,nActiveCells[cellName])
		im = ax[-1].imshow(data, cmap=colorMap2, interpolation='nearest',origin="lower",vmin = 0, vmax = maxActiveCells[cellName],aspect='auto')
		ax[-1].set_title("Number of active cells - "+cellName)

		# Move left and bottom spines outward by 10 points
		ax[-1].spines['left'].set_position(('outward', 10))
		ax[-1].spines['bottom'].set_position(('outward', 10))
		# Hide the right and top spines
		ax[-1].spines['right'].set_visible(False)
		ax[-1].spines['top'].set_visible(False)
		# Only show ticks on the left and bottom spines
		ax[-1].yaxis.set_ticks_position('left')
		ax[-1].xaxis.set_ticks_position('bottom')

		ax[-1].set_xticks(range(len(eesFrequencies)))
		ax[-1].set_xticklabels(eesFrequencies)

		ax[-1].set_yticks(range(len(eesAmplitudes)))
		ax[-1].set_yticklabels(eesAmplitudes)

		fig.colorbar(im, orientation='vertical',label="N active cells")

	ax[-2].set_xlabel("Stimulation frequency (Hz)")
	ax[-1].set_xlabel("Stimulation frequency (Hz)")

	fileName = time.strftime("%Y_%m_%d_freqAmpDependancy.pdf")
	plt.savefig("../../results/"+fileName, format="pdf",transparent=True)

	fig2, ax2 = plt.subplots(2, 1)
	intervalHalfWidth = 5
	targetFiringrates = range(10,41,10)
	cmap = plt.get_cmap('winter')
	colors = cmap(np.linspace(0.1,0.9,len(targetFiringrates)))
	isomodulationCurves = []
	for n,target in enumerate(targetFiringrates):
		isomodulationCurves.append({})
		temp = np.zeros([len(eesAmplitudes),len(eesFrequencies)])*np.nan
		for i,eesAmplitude in enumerate(eesAmplitudes):
			for j,eesFrequency in enumerate(eesFrequencies):
				if populationFr["MnS_MnFf_MnFr"][i,j]>target-intervalHalfWidth and populationFr["MnS_MnFf_MnFr"][i,j]<target+intervalHalfWidth:
					if type(eesAmplitude) is str: temp[i,j] = eesAmplitude[1:4]
					else: temp[i,j] = eesAmplitude
		isomodulationCurves[-1]['max'] = fill_nan(np.nanmax(temp,axis=0))
		isomodulationCurves[-1]['mean'] = fill_nan(np.nanmean(temp,axis=0))
		isomodulationCurves[-1]['min'] = fill_nan(np.nanmin(temp,axis=0))

		ax2[0].plot(eesFrequencies,isomodulationCurves[-1]['max'],color=colors[n])
		ax2[0].plot(eesFrequencies,isomodulationCurves[-1]['mean'],color=colors[n])
		ax2[0].plot(eesFrequencies,isomodulationCurves[-1]['min'],color=colors[n])
		ax2[0].fill_between(eesFrequencies,isomodulationCurves[-1]['min'],isomodulationCurves[-1]['max'],color=colors[n],alpha=0.3)
		ax2[0].set_xscale("log")
		ax2[1].plot(eesFrequencies,isomodulationCurves[-1]['mean'],color=colors[n])

	fileName = time.strftime("/%Y_%m_%d_freqAmpDependancyIsoModCurves.pdf")
	plt.savefig(pathToResults+fileName, format="pdf",transparent=True)

	plt.show()

def fill_nan(A):
	"""
	interpolate to fill nan values
	"""
	inds = np.arange(A.shape[0])
	good = np.where(np.isfinite(A))
	A[np.isnan(A)] = np.interp(inds[np.isnan(A)], inds[good], A[good])
	return A

# ---Unused---
def load_rec_data():
	""" Load recruitment data from a previosly validated FEM model (Capogrosso et al 2013). """
	recI_MG=np.loadtxt('../recruitmentData/GM_full_S1_wire1')
	recI_TA=np.loadtxt('../recruitmentData/TA_full_S1_wire1')

	allPercIf_GM= recI_MG/max(recI_MG)
	allPercIf_TA= recI_TA/max(recI_TA)

	minCur = 0 #uA
	maxCur = 600 #uA

	nVal = recI_MG.size
	allPercIf= (allPercIf_GM+allPercIf_TA)/2

	currents = np.linspace(minCur,maxCur,nVal)
	f = interpolate.interp1d(currents, allPercIf)

	return f

def compute_error(amplitude,target,f):
	actualPerc =  f(amplitude)
	error = np.array(target-actualPerc)
	return error

def minimize(target,f,x0,errTol=0.01,dx=5,maxIters = 100000):
	error=9999
	x0 -= dx
	for i in xrange(maxIters):
		x0 += dx
		error = compute_error(x0,target,f)
		if error<errTol:break
	if error>errTol:raise Exception("minimization failed")
	print "out:",x0,"  target:",target,"  error:",error
	return x0,error

def find_corrisponding_amplitude(target,f):
	tp = (target, f)
	current,error = minimize(target, f,x0=150)
	return current

def transform_amp_perc_to_curr(eesAmplitude):
	f = load_rec_data()
	current = find_corrisponding_amplitude(eesAmplitude,f)
	return current


if __name__ == '__main__':
	main()
