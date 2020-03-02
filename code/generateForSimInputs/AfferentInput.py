import sys
sys.path.append('../code')
import numpy as np
import pandas as pd
from tools import general_tools as gt
import pickle
import matplotlib.pyplot as plt

class AfferentInput():

	def __init__(self,dt,restingAngle,fiberLengthRange,fiberLengthGait,musclesActivation,footHeight,eventFile=None):

		self._dt = dt

		self._eventFile = eventFile

		self._fiberLengthRange = fiberLengthRange
		self._computeFiberLengthRest(restingAngle)

		self._fiberLengthGait = fiberLengthGait
		if self._fiberLengthGait['dt'] != self._dt:
			ratio = self._dt/self._fiberLengthGait['dt']
			self._fiberLengthGait = gt.resample(self._fiberLengthGait,['time','ext','flex'],ratio)
			self._fiberLengthGait['dt'] = self._dt

		self._footHeight = footHeight
		if self._footHeight['dt'] != self._dt:
			ratio = self._dt/self._footHeight['dt']
			self._footHeight = gt.resample(self._footHeight,['time','height'],ratio)
			self._footHeight['dt'] = self._dt

		self._musclesActivation = musclesActivation
		if self._musclesActivation['dt'] != self._dt:
			ratio = self._dt/self._musclesActivation['dt']
			self._musclesActivation = gt.resample(self._musclesActivation,['time','ext','flex'],ratio)
			self._musclesActivation['dt'] = self._dt
		self._normMusclesActivation()

		self._adjustDataLengths()

	def __del__(self):
		pass


	def _extract_foot_events(self):
		if self._eventFile is None:
			raise(Exception("If you want to compute the cutaneous firings, you need to provide a path for the event file (to load it or to create it)."))
		try:
			with open(self._eventFile, 'r') as pickle_file:
				self._footStrikes = pickle.load(pickle_file)
				self._footOffs = pickle.load(pickle_file)

		except IOError:
			print 'The evets need to be extracted..\nExtract the foot strikes first!'
			fig = plt.figure(figsize=(16,9))
			plt.plot(self._footHeight['height'])
			plt.title('Click on the foot strikes, then, close the image')
			temp = plt.ginput(100)
			self._footStrikes = np.array(temp)[:,0].astype(int)
			print "Now the foor offs!"
			fig = plt.figure(figsize=(16,9))
			plt.plot(self._footHeight['height'])
			plt.title('Click on the foot offs, then, close the image')
			temp = plt.ginput(100)
			self._footOffs = np.array(temp)[:,0].astype(int)
			with open(self._eventFile, 'w') as pickle_file:
				pickle.dump(self._footStrikes,pickle_file)
				pickle.dump(self._footOffs,pickle_file)

	def _computeFiberLengthRest(self,angleAtRest=-3):
		indRest = None
		for i,angle in enumerate(self._fiberLengthRange['angle']):
			if angle < angleAtRest+1 and angle > angleAtRest-1:
				indRest = i
				break
		self._lflex0 = self._fiberLengthRange['flex'][indRest]
		self._lext0 = self._fiberLengthRange['ext'][indRest]

	def _normMusclesActivation(self):
		noAct = []
		good = []
		for muscle in ['ext','flex']:
			minAct = min(self._musclesActivation[muscle])
			maxAct = max(self._musclesActivation[muscle])
			if minAct==maxAct: noAct.append(muscle)
			else: good.append(muscle)
			self._musclesActivation[muscle] = [float(act-minAct)/(maxAct-minAct) for act in self._musclesActivation[muscle]]
		if len(good)==1 or len(noAct)==1:
			self._musclesActivation[noAct[0]] = [goodAct*-1+1 for goodAct in self._musclesActivation[good[0]]]

	def _adjustDataLengths(self):
		self._nSamples = np.min([len(self._fiberLengthGait['time']),len(self._musclesActivation['time']),len(self._footHeight['time'])])
		self._fiberLengthGait['time'] = self._fiberLengthGait['time'][:self._nSamples]
		self._fiberLengthGait['ext'] = self._fiberLengthGait['ext'][:self._nSamples]
		self._fiberLengthGait['flex'] = self._fiberLengthGait['flex'][:self._nSamples]
		self._musclesActivation['time'] = self._musclesActivation['time'][:self._nSamples]
		self._musclesActivation['ext'] = self._musclesActivation['ext'][:self._nSamples]
		self._musclesActivation['flex'] = self._musclesActivation['flex'][:self._nSamples]
		self._footHeight['time'] = self._footHeight['time'][:self._nSamples]
		self._footHeight['height'] = self._footHeight['height'][:self._nSamples]

	def computeIaFr(self, fname=None, normFactor=1,muscName=["GM","TA"]):
		fr_Ia_Flex=None
		fr_Ia_Ext=None

		bias = 50
		vCoef = 4.3
		xCoef = 2
		expn = 0.6
		emgCoef = 50

		stretchTA = (self._fiberLengthGait['flex']-self._lflex0)*1000
		stretchMG = (self._fiberLengthGait['ext']-self._lext0)*1000

		# Compute stretch velocity [mm/s]
		velocityMG=[]
		velocityTA=[]
		velocityMG.append(0)
		velocityTA.append(0)
		for i in range(1,len(stretchTA)):
			velocityTA.append((stretchTA[i]-stretchTA[i-1])/self._fiberLengthGait['dt'])
			velocityMG.append((stretchMG[i]-stretchMG[i-1])/self._fiberLengthGait['dt'])

		# compute stretch vel^n
		vSignTA=[]
		vSignMG=[]
		for vTA,vMG in zip(velocityTA,velocityMG):
			if not vTA==0:vSignTA.append(vTA/abs(vTA))
			else:vSignTA.append(1)
			if not vMG==0:vSignMG.append(vMG/abs(vMG))
			else:vSignMG.append(1)
		vPowTA = [x*abs(y)**expn for x,y in zip(vSignTA,velocityTA)]
		vPowMG = [x*abs(y)**expn for x,y in zip(vSignMG,velocityMG)]

		#compute firing rates
		fr_Ia_Flex = np.array([bias + xCoef*i + vCoef*j + emgCoef*k for i,j,k in zip(stretchTA,vPowTA,self._musclesActivation['flex'])])
		fr_Ia_Ext = np.array([bias + xCoef*i + vCoef*j + emgCoef*k for i,j,k in zip(stretchMG,vPowMG,self._musclesActivation['ext'])])

		fr_Ia_Flex[fr_Ia_Flex<0]=0
		fr_Ia_Ext[fr_Ia_Ext<0]=0

		fr_Ia_Flex *= normFactor
		fr_Ia_Ext *= normFactor

		# save data
		if fname is not None:
			np.savetxt("./generateForSimInputs/output/meanFr_Ia_"+muscName[0]+fname+".txt", fr_Ia_Ext)
			np.savetxt("./generateForSimInputs/output/meanFr_Ia_"+muscName[1]+fname+".txt", fr_Ia_Flex)

		return (fr_Ia_Flex,fr_Ia_Ext)

	def computeIIFr(self, fname=None, normFactor=1,muscName=["GM","TA"]):
		fr_II_Flex=None
		fr_II_Ext=None

		bias = 80
		xCoef = 13.5
		emgCoef = 20

		stretchTA = (self._fiberLengthGait['flex']-self._lflex0)*1000
		stretchMG = (self._fiberLengthGait['ext']-self._lext0)*1000

		#compute firing rates
		fr_II_Flex = np.array([bias + xCoef*i + emgCoef*j for i,j in zip(stretchTA,self._musclesActivation['flex'])])
		fr_II_Ext = np.array([bias + xCoef*i + emgCoef*j for i,j in zip(stretchMG,self._musclesActivation['ext'])])

		fr_II_Flex[fr_II_Flex<0]=0
		fr_II_Ext[fr_II_Ext<0]=0

		fr_II_Flex *= normFactor
		fr_II_Ext *= normFactor

		# save data
		if fname is not None:
			np.savetxt("./generateForSimInputs/output/meanFr_II_"+muscName[0]+fname+".txt", fr_II_Ext)
			np.savetxt("./generateForSimInputs/output/meanFr_II_"+muscName[1]+fname+".txt", fr_II_Flex)

		return (fr_II_Flex,fr_II_Ext)

	def computeIbFr(self, fname=None, normFactor=1,muscName=["GM","TA"]):
		# TODO andreas
		return


	def computeSAIFr(self,fname=None,normFactor=1):
		try:
			with open("./generateForSimInputs/output/SAI_modelParameters.p", 'r') as pickle_file:
				A = pickle.load(pickle_file)
				K = pickle.load(pickle_file)
				C = pickle.load(pickle_file)
		except IOError:
			raise(Exception("You first nedd to build the SAI model running the build_SAI_model.py script!"))

		self._extract_foot_events()
		fr_SAI = np.zeros(self._nSamples)
		if self._footOffs.min() < self._footStrikes.min(): swingPhase = False
		else: swingPhase = True
		t = 1000
		for n in xrange(self._nSamples):
			if swingPhase:
				if n in self._footStrikes:
					swingPhase = False
					t=0
			else:
				fr_SAI[n] = 10*(A*np.exp(K*t)+C)
				t+=self._dt
				if n in self._footOffs: swingPhase = True

		# save data
		if fname is not None:
			np.savetxt("./generateForSimInputs/output/meanFr_SAI"+fname+".txt", fr_SAI)
		return fr_SAI

	def computeRAFr(self,fname=None,normFactor=1):
		try:
			with open("./generateForSimInputs/output/RA_modelParameters.p", 'r') as pickle_file:
				A = pickle.load(pickle_file)
				K = pickle.load(pickle_file)
		except IOError:
			raise(Exception("You first nedd to build the RA model running the build_RA_model.py script!"))

		self._extract_foot_events()
		fr_RA = np.zeros(self._nSamples)
		if self._footOffs.min() < self._footStrikes.min(): swingPhase = False
		else: swingPhase = True
		t = 1000
		for n in xrange(self._nSamples):
			if swingPhase:
				fr_RA[n] = 10*A*np.exp(K*2*t)
				t+=self._dt
				if n in self._footStrikes:
					swingPhase = False
					t=0
			else:
				fr_RA[n] = 10*A*np.exp(K*t)
				t+=self._dt
				if n in self._footOffs:
					swingPhase = True
					t=0

		# save data
		if fname is not None:
			np.savetxt("./generateForSimInputs/output/meanFr_RA"+fname+".txt", fr_RA)
		return fr_RA

	def get_emg_locomotion(self):
		return (self._musclesActivation['ext'],self._musclesActivation['flex'])

	def get_fiber_length_locomotion(self):
		return (self._fiberLengthGait['ext'],self._fiberLengthGait['flex'])

	def get_fiber_length_rest(self):
		return (self._lext0, self._lflex0,)
