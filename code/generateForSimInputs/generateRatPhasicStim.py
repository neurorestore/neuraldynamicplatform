import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys
import pickle
sys.path.append('../code')
from tools import emg_tools as et
from tools import load_data_tools as ldt

modulationDt = 0.05
kinBasedModulation = True
emgBasedModulation = True
kinEmgBasedModulation = True

DEBUG = True
if DEBUG: colors={'TA':'b','GM':'r'}


if kinBasedModulation:
    kinFile = "./generateForSimInputs/data/rat/#208_100903_P0_BIP_TM9_4_KIN.csv"
    footHeight = ldt.readGlabRecordedAnalogData(kinFile,['height'],["RTip_Z"])
    footHeight['dt'] = 0.005
    footHeight['time'] = np.arange(len(footHeight['height']))*footHeight['dt']

    dwnSamplFcr = int(modulationDt/footHeight['dt'])
    tempStim = np.zeros(footHeight['time'].size)
    threshold = np.std(footHeight['height'])*0.5
    tempStim[footHeight['height']>threshold] = 1

    tempStimFilt = et.binary_majority_voting(tempStim,50)
    tempStimFilt = tempStimFilt[0:-1:dwnSamplFcr]

    stim = {'GM':np.zeros(tempStimFilt.size),
            'TA':np.zeros(tempStimFilt.size)}
    stim['GM'][np.nonzero(tempStimFilt==0)] = 1
    stim['TA'][np.nonzero(tempStimFilt)] = 1

    if DEBUG:
        plt.figure()
        plt.plot(footHeight['height'][0:-1:dwnSamplFcr])
        plt.plot(stim['GM']*20,color=colors['GM'])
        plt.plot(stim['TA']*20,color=colors['TA'])

    resultsFolder = "generateForSimInputs/output/"
    fileName = "spatiotemporalStimulationRatKinBased.p"
    eesModulation = {"modulation":stim, "dt":1000*dwnSamplFcr*footHeight['dt']}
    with open(resultsFolder+fileName, 'w') as pickle_file:
    	pickle.dump(eesModulation, pickle_file)

if emgBasedModulation:
    emgFile = "./generateForSimInputs/data/rat/#208_100903_P0_BIP_TM9_4_ANA.csv"
    musclesActivation = ldt.readGlabRecordedAnalogData(emgFile,['GM','TA'],['RMG','RTA'])
    musclesActivation['dt'] = 0.0005
    musclesActivation['time'] = np.arange(len(musclesActivation['GM']))*musclesActivation['dt']

    stim = {}
    dwnSamplFcr = int(modulationDt/musclesActivation['dt'])
    if DEBUG: plt.figure()
    for muscle in ['GM','TA']:
    	musclesActivation[muscle] = et.compute_envelope(musclesActivation[muscle],musclesActivation['dt']*1000)
        tempStim = np.zeros(musclesActivation[muscle].size)
        threshold = np.std(musclesActivation[muscle])*0.5
        tempStim[musclesActivation[muscle]>threshold] = 1
        tempStimFilt = et.binary_majority_voting(tempStim,400)
        stim[muscle] = tempStimFilt[0:-1:dwnSamplFcr]
        if DEBUG:
            plt.plot(musclesActivation[muscle],color=colors[muscle])
            plt.plot(tempStimFilt,color=colors[muscle])

    resultsFolder = "generateForSimInputs/output/"
    fileName = "spatiotemporalStimulationRatEmgBased.p"
    eesModulation = {"modulation":stim, "dt":1000*dwnSamplFcr*musclesActivation['dt']}
    with open(resultsFolder+fileName, 'w') as pickle_file:
    	pickle.dump(eesModulation, pickle_file)

if kinEmgBasedModulation:
    kinFile = "./generateForSimInputs/data/rat/#208_100903_P0_BIP_TM9_4_KIN.csv"
    footHeight = ldt.readGlabRecordedAnalogData(kinFile,['height'],["RTip_Z"])
    footHeight['dt'] = 0.005
    footHeight['time'] = np.arange(len(footHeight['height']))*footHeight['dt']

    emgFile = "./generateForSimInputs/data/rat/#208_100903_P0_BIP_TM9_4_ANA.csv"
    musclesActivation = ldt.readGlabRecordedAnalogData(emgFile,['GM','TA'],['RMG','RTA'])
    musclesActivation['dt'] = 0.0005
    musclesActivation['time'] = np.arange(len(musclesActivation['GM']))*musclesActivation['dt']

    dwnSamplFcrKin = int(modulationDt/footHeight['dt'])
    tempStim = np.zeros(footHeight['time'].size)
    threshold = np.std(footHeight['height'])*0.5
    print threshold
    tempStim[footHeight['height']>threshold] = 1

    tempStimFilt = et.binary_majority_voting(tempStim,50)
    tempStimFilt = tempStimFilt[0:-1:dwnSamplFcrKin]

    stimKin = {'GM':np.zeros(tempStimFilt.size),
            'TA':np.zeros(tempStimFilt.size)}
    stimKin['GM'][np.nonzero(tempStimFilt==0)] = 1
    stimKin['TA'][np.nonzero(tempStimFilt)] = 1

    stim = {}
    dwnSamplFcrEmg = int(modulationDt/musclesActivation['dt'])
    if DEBUG: plt.figure()
    for muscle in ['GM','TA']:
        musclesActivation[muscle] = et.compute_envelope(musclesActivation[muscle],musclesActivation['dt']*1000)
        musclesActivation[muscle] = musclesActivation[muscle][0:-1:dwnSamplFcrEmg]
        sizeDiff = stimKin[muscle].size - musclesActivation[muscle].size
        if sizeDiff > 0:
            stimKin[muscle] = stimKin[muscle][:-1-sizeDiff]
        elif sizeDiff < 0:
            for i in range(abs(sizeDiff)):
                stimKin[muscle] = np.append(stimKin[muscle],stimKin[muscle][-1])

        stim[muscle] = np.zeros(musclesActivation[muscle].size)
        #select slices where stimKin is 1
        IndexesStimKinOn = np.squeeze(np.nonzero(stimKin[muscle]==1))

        #perform thresholding with emg
        threshold = musclesActivation[muscle][IndexesStimKinOn].min() + 0.25*np.std(musclesActivation[muscle][IndexesStimKinOn])
        indexesThreshold = np.squeeze(np.nonzero(musclesActivation[muscle][IndexesStimKinOn]>threshold))
        indexesSelected = IndexesStimKinOn[indexesThreshold]
        stim[muscle][indexesSelected] = 1

        #majority voting
        stim[muscle] = et.binary_majority_voting(stim[muscle],2)

        if DEBUG:
            plt.plot(musclesActivation[muscle],color=colors[muscle])
            plt.plot(stim[muscle],color=colors[muscle])

    resultsFolder = "generateForSimInputs/output/"
    fileName = "spatiotemporalStimulationRatKinEmgBased.p"
    eesModulation = {"modulation":stim, "dt":1000*dwnSamplFcrEmg*musclesActivation['dt']}
    with open(resultsFolder+fileName, 'w') as pickle_file:
    	pickle.dump(eesModulation, pickle_file)

if DEBUG: plt.show()
