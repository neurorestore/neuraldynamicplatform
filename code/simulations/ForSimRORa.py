from mpi4py import MPI
from neuron import h
from ForwardSimulation import ForwardSimulation
from cells import AfferentFiber
import random as rnd
import time
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from tools import firings_tools as tlsf
import pickle
from tools import seed_handler as sh
sh.set_seed()

comm = MPI.COMM_WORLD
sizeComm = comm.Get_size()
rank = comm.Get_rank()

class ForSimRORa(ForwardSimulation):
	""" Integration of a NeuralNetwork object of two antagonist muscles over time given an input.
		EMG and afferent firing rates are the results extracted at the end of simulation.
	"""

	def plot(self,flexorMuscle,extensorMuscle,name="",showFig=True):
		""" Plot and save the simulation results.

		Keyword arguments:
		flexorMuscle -- flexor muscle to plot
		extensorMuscle -- extensor muscle to plot
		name -- string to add at predefined file name of the saved pdf.
		"""
		meanPercErasedApFlexIaf,percErasedApFlexIaf = self._get_perc_aff_ap_erased(flexorMuscle,self._Iaf)
		meanPercErasedApExtIaf,percErasedApExtIaf = self._get_perc_aff_ap_erased(extensorMuscle,self._Iaf)
		meanPercErasedApFlexIIf,percErasedApFlexIIf = self._get_perc_aff_ap_erased(flexorMuscle,self._IIf)
		meanPercErasedApExtIIf,percErasedApExtIIf = self._get_perc_aff_ap_erased(extensorMuscle,self._IIf)
		meanPerEraserApIaf = np.mean([meanPercErasedApFlexIaf,meanPercErasedApExtIaf])
		meanPerEraserApIIf = np.mean([meanPercErasedApFlexIIf,meanPercErasedApExtIIf])

		#should be on rank 0?
		if not self._ees == None:
			percFiberActEes = self._ees.get_amplitude()
			title = 'EES _ {0:.0f}uA _ {1:.0f}Hz _ Delay _ {2:.0f}ms '.format(percFiberActEes[0],self._ees.get_frequency(),\
				self._nn.cells[flexorMuscle][self._Iaf][0].get_delay())
			plt.suptitle(title+"\n Iaf = {0:.0f}%, IIf = {1:.0f}%, Mn = {2:.0f}%, PercErasedApIaf = {3:.0f}%, prasedApIIf = {4:.0f}% ".format(\
				100*percFiberActEes[1],100*percFiberActEes[2],100*percFiberActEes[3],meanPerEraserApIaf,meanPerEraserApIIf))
		else:
			title = ' No EES _ Delay _ {2:.0f} ms '.format(self._nn.cells[flexorMuscle][self._Iaf][0].get_delay())
			plt.suptitle(title+"\n PercErasedApIaf = {3:.0f}%, prasedApIIf = {4:.0f}% ".format(meanPerEraserApIaf,meanPerEraserApIIf))


		if rank == 0:
			if not self._nn.recordMotoneurons and not self._nn.recordMotoneurons:
				raise(Exception("To plot the results it is necessary to have the NeuralNetwork recordMotoneurons and recordAfferents flags set to True"))

			flexIaAfferentModel = self._meanFr[flexorMuscle][self._Iaf]
			flexIIAfferentModel = self._meanFr[flexorMuscle]['IIf']
			flexRAf_footAfferentModel = self._meanFr[flexorMuscle]['II_RAf_foot']
			flexSAIf_footAfferentModel = self._meanFr[flexorMuscle]['II_SAIf_foot']
			flexRAfAfferentModel = self._meanFr[flexorMuscle]['II_RAf']
			flexSAIfAfferentModel = self._meanFr[flexorMuscle]['II_SAIf']

			extIaAfferntModel = self._meanFr[extensorMuscle][self._Iaf]
			extIIAfferntModel = self._meanFr[extensorMuscle]['IIf']
			extRAf_footAfferntModel = self._meanFr[extensorMuscle]['II_RAf_foot']
			extSAIf_footAfferntModel = self._meanFr[extensorMuscle]['II_SAIf_foot']
			extRAfAfferntModel = self._meanFr[extensorMuscle]['II_RAf']
			extSAIfAfferntModel = self._meanFr[extensorMuscle]['II_SAIf']

			flexMnAll = [self._meanFr[flexorMuscle][mnName] for mnName in self._Mn]
			extMnAll = [self._meanFr[extensorMuscle][mnName] for mnName in self._Mn]
			flexMn = np.mean(flexMnAll,axis=0)
			extMn = np.mean(extMnAll,axis=0)

			if self._afferentModulation:
				flexIaAfferentInput = self._afferentInput[flexorMuscle][self._Iaf]
				flexIIAfferentInput = self._afferentInput[flexorMuscle]['IIf']
				flexRAf_footAfferentInput = self._afferentInput[flexorMuscle]['II_RAf_foot']
				flexSAIf_footAfferentInput = self._afferentInput[flexorMuscle]['II_SAIf_foot']
				flexRAfAfferentInput = self._afferentInput[flexorMuscle]['II_RAf']
				flexSAIfAfferentInput = self._afferentInput[flexorMuscle]['II_SAIf']

				extIaAfferentInput = self._afferentInput[extensorMuscle][self._Iaf]
				extIIAfferentInput = self._afferentInput[extensorMuscle]['IIf']
				extRAf_footAfferentInput = self._afferentInput[extensorMuscle]['II_RAf_foot']
				extSAIf_footAfferentInput = self._afferentInput[extensorMuscle]['II_SAIf_foot']
				extRAfAfferentInput = self._afferentInput[extensorMuscle]['II_RAf']
				extSAIfAfferentInput = self._afferentInput[extensorMuscle]['II_SAIf']

			tStop = self._get_tstop()
			info,temp = self._nn.get_mn_info()
			strInfo = []
			for line in info: strInfo.append(" ".join(line))

			fig1, ax1 = plt.subplots(2, 4,figsize=(24,10),sharex='col',sharey='col')
			""" Ia afferents fr subplots """
			ax1[0,0].plot(flexIaAfferentModel,color='b',label='model')
			if self._afferentModulation:
				ax1[0,0].plot(np.arange(0,tStop,self._dtUpdateAfferent),flexIaAfferentInput[:np.ceil(float(tStop)/self._dtUpdateAfferent).astype(int)],color='r',label='input')
			ax1[0,0].set_title('Ia afferents mean firing rate')
			ax1[0,0].legend(loc='upper right')
			ax1[0,0].set_ylabel("Ia firing rate (Hz) - flex")
			ax1[1,0].plot(extIaAfferntModel,color='b',label='model')
			if self._afferentModulation:
				ax1[1,0].plot(np.arange(0,tStop,self._dtUpdateAfferent),extIaAfferentInput[:np.ceil(float(tStop)/self._dtUpdateAfferent).astype(int)],color='r',label='input')
			ax1[1,0].legend(loc='upper right')
			ax1[1,0].set_ylabel("Ia firing rate (Hz) - ext")
			ax1[1,0].set_xlabel("time (ms)")

			""" afferents percAperased subplots """
			ax1[0,1].hist(percErasedApFlexIaf, bins=range(0,101,2), facecolor='green', alpha=0.75)
			ax1[0,1].set_title("Histogram of the Ap perc erased in Iaf")
			ax1[0,1].set_ylabel("Frquency - flex")
			ax1[0,1].axis([0, 100, 0, 60])
			ax1[1,1].hist(percErasedApExtIaf, bins=range(0,101,2), facecolor='green', alpha=0.75)
			ax1[1,1].set_ylabel("Frquency - ext")
			ax1[1,1].set_xlabel("Percentage %")
			ax1[1,1].axis([0, 100, 0, 60])

			""" Motoneurons subplots """
			ax1[0,2].plot(flexMn)
			ax1[0,2].set_title('Motoneurons mean firing rate')
			ax1[0,2].set_ylabel("Mn firing rate (Hz) - flex")
			ax1[1,2].plot(extMn)
			ax1[1,2].set_ylabel("Mn firing rate (Hz) - ext")
			ax1[1,2].set_xlabel("time (ms)")

			""" EMG plot """
			ax1[0,3].plot(self.get_estimated_emg(flexorMuscle),color='b',label='model')
			ax1[0,3].set_ylabel("amplutide (a.u.) - flex")
			ax1[0,3].set_xlabel("time (ms)")
			ax1[0,3].set_title('Estimated EMG')
			ax1[1,3].plot(self.get_estimated_emg(extensorMuscle),color='b',label='model')
			ax1[1,3].set_ylabel("amplutide (a.u.) - ext")
			ax1[1,3].set_xlabel("time (ms)")

			title = title.replace(" ","")
			if showFig:	plt.show()

			fig2, ax2 = plt.subplots(2, 5,figsize=(24,10),sharex='col',sharey='col')
			""" II afferents fr subplots """
			ax2[0,0].plot(flexIIAfferentModel,color='b',label='model')
			if self._afferentModulation:
				ax2[0,0].plot(np.arange(0,tStop,self._dtUpdateAfferent),flexIIAfferentInput[:np.ceil(float(tStop)/self._dtUpdateAfferent).astype(int)],color='r',label='input')
			ax2[0,0].set_title('II afferents mean firing rate')
			ax2[0,0].legend(loc='upper right')
			ax2[0,0].set_ylabel("II firing rate (Hz) - flex")
			ax2[1,0].plot(extIIAfferntModel,color='b',label='model')
			if self._afferentModulation:
				ax2[1,0].plot(np.arange(0,tStop,self._dtUpdateAfferent),extIIAfferentInput[:np.ceil(float(tStop)/self._dtUpdateAfferent).astype(int)],color='r',label='input')
			ax2[1,0].legend(loc='upper right')
			ax2[1,0].set_ylabel("II firing rate (Hz) - ext")
			ax2[1,0].set_xlabel("time (ms)")

			""" Cutaneous RA afferents fr subplots """
			ax2[0,1].plot(flexRAfAfferentModel,color='b',label='model')
			if self._afferentModulation:
				ax2[0,1].plot(np.arange(0,tStop,self._dtUpdateAfferent),flexRAfAfferentInput[:np.ceil(float(tStop)/self._dtUpdateAfferent).astype(int)],color='r',label='input')
			ax2[0,1].set_title('RA afferents mean firing rate')
			ax2[0,1].legend(loc='upper right')
			ax2[0,1].set_ylabel("RA firing rate (Hz) - flex")
			ax2[1,1].plot(extRAfAfferntModel,color='b',label='model')
			if self._afferentModulation:
				ax2[1,1].plot(np.arange(0,tStop,self._dtUpdateAfferent),extRAfAfferentInput[:np.ceil(float(tStop)/self._dtUpdateAfferent).astype(int)],color='r',label='input')
			ax2[1,1].legend(loc='upper right')
			ax2[1,1].set_ylabel("RA firing rate (Hz) - ext")
			ax2[1,1].set_xlabel("time (ms)")

			""" Cutaneous RA foot afferents fr subplots """
			ax2[0,2].plot(flexRAf_footAfferentModel,color='b',label='model')
			if self._afferentModulation:
				ax2[0,2].plot(np.arange(0,tStop,self._dtUpdateAfferent),flexRAf_footAfferentInput[:np.ceil(float(tStop)/self._dtUpdateAfferent).astype(int)],color='r',label='input')
			ax2[0,2].set_title('RA foot afferents mean firing rate')
			ax2[0,2].legend(loc='upper right')
			ax2[0,2].set_ylabel("RA foot firing rate (Hz) - flex")
			ax2[1,2].plot(extRAf_footAfferntModel,color='b',label='model')
			if self._afferentModulation:
				ax2[1,2].plot(np.arange(0,tStop,self._dtUpdateAfferent),extRAf_footAfferentInput[:np.ceil(float(tStop)/self._dtUpdateAfferent).astype(int)],color='r',label='input')
			ax2[1,2].legend(loc='upper right')
			ax2[1,2].set_ylabel("RA foot firing rate (Hz) - ext")
			ax2[1,2].set_xlabel("time (ms)")

			""" Cutaneous SAI afferents fr subplots """
			ax2[0,3].plot(flexSAIfAfferentModel,color='b',label='model')
			if self._afferentModulation:
				ax2[0,3].plot(np.arange(0,tStop,self._dtUpdateAfferent),flexSAIfAfferentInput[:np.ceil(float(tStop)/self._dtUpdateAfferent).astype(int)],color='r',label='input')
			ax2[0,3].set_title('SAI afferents mean firing rate')
			ax2[0,3].legend(loc='upper right')
			ax2[0,3].set_ylabel("SAI firing rate (Hz) - flex")
			ax2[1,3].plot(extSAIfAfferntModel,color='b',label='model')
			if self._afferentModulation:
				ax2[1,3].plot(np.arange(0,tStop,self._dtUpdateAfferent),extSAIfAfferentInput[:np.ceil(float(tStop)/self._dtUpdateAfferent).astype(int)],color='r',label='input')
			ax2[1,3].legend(loc='upper right')
			ax2[1,3].set_ylabel("SAI firing rate (Hz) - ext")
			ax2[1,3].set_xlabel("time (ms)")

			""" Cutaneous SAI foot afferents fr subplots """
			ax2[0,4].plot(flexSAIf_footAfferentModel,color='b',label='model')
			if self._afferentModulation:
				ax2[0,4].plot(np.arange(0,tStop,self._dtUpdateAfferent),flexSAIf_footAfferentInput[:np.ceil(float(tStop)/self._dtUpdateAfferent).astype(int)],color='r',label='input')
			ax2[0,4].set_title('SAI foot afferents mean firing rate')
			ax2[0,4].legend(loc='upper right')
			ax2[0,4].set_ylabel("SAI foot firing rate (Hz) - flex")
			ax2[1,4].plot(extSAIf_footAfferntModel,color='b',label='model')
			if self._afferentModulation:
				ax2[1,4].plot(np.arange(0,tStop,self._dtUpdateAfferent),extSAIf_footAfferentInput[:np.ceil(float(tStop)/self._dtUpdateAfferent).astype(int)],color='r',label='input')
			ax2[1,4].legend(loc='upper right')
			ax2[1,4].set_ylabel("SAI foot firing rate (Hz) - ext")
			ax2[1,4].set_xlabel("time (ms)")


			fig3 = plt.figure()
			ax3 = fig3.add_subplot(111)
			ax3.text(0.5, 0.5,"\n".join(strInfo), horizontalalignment='center',verticalalignment='center',transform=ax3.transAxes)
			ax3.xaxis.set_visible(False)
			ax3.yaxis.set_visible(False)




			fileName = time.strftime("%Y_%m_%d_FS_"+title+name+".pdf")
			pp = PdfPages(self._resultsFolder+fileName)
			pp.savefig(fig1)
			pp.savefig(fig2)
			pp.savefig(fig3)
			pp.close()


	def save_results(self,flexorMuscle,extensorMuscle,name=""):
		""" Save the resulting motoneurons mean firings and EMG.

		Keyword arguments:
		name -- string to add at predefined file name of the saved pdf (default = "").
		"""

		meanPercErasedApFlexIaf,percErasedApFlexIaf = self._get_perc_aff_ap_erased(flexorMuscle,self._Iaf)
		meanPercErasedApExtIaf,percErasedApExtIaf = self._get_perc_aff_ap_erased(extensorMuscle,self._Iaf)
		meanPerEraserApIaf = np.mean([meanPercErasedApFlexIaf,meanPercErasedApExtIaf])

		if rank == 0:
			if not self._ees == None:
				percFiberActEes = self._ees.get_amplitude()
				title = 'EES_{0:.0f}uA_{1:.0f}Hz_Delay_{2:.0f}ms'.format(percFiberActEes[0],self._ees.get_frequency(),\
					self._nn.cells[flexorMuscle][self._Iaf][0].get_delay())
			else: title = 'NoEES_Delay_{2:.0f}ms'.format(self._nn.cells[flexorMuscle][self._Iaf][0].get_delay())
			fileName = time.strftime("%Y_%m_%d_FS_"+title+name+".p")

			with open(self._resultsFolder+fileName, 'w') as pickle_file:
				pickle.dump(self._estimatedEMG, pickle_file)
				pickle.dump(self._meanFr, pickle_file)
				pickle.dump(meanPerEraserApIaf,pickle_file)
