import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys
import pickle
sys.path.append('../code')
from tools import emg_tools as et
from tools import general_tools as gt
from tools import load_data_tools as ldt

pathToResults = "../../results"

modulationDt = 0.05
kinBasedModulation = False
emgBasedModulation = False
kinEmgBasedModulation = False
sensoryKinEmgBasedModulation = True
proportionalSensoryKinEmgBasedModulation = True

DEBUG = True
flexMuscle = "TA"
extMuscle = "SOL" #SOL or GL
flexMuscleHumod = "TA_L"
extMuscleHumod = "SOL_L"

colors={flexMuscle:"#00aaeb",extMuscle:"#e9342f"}


if kinBasedModulation:

    kinFile = "./generateForSimInputs/data/human/HuMoD-database/generatedFiles/Subject_B_speed_1.3_10-Jul-2017_KIN.csv" # need to check the speed
    footHeight = ldt.readCsvGeneral(kinFile,1,['time','height'],['time','leftToe'])
    footHeight['dt'] = (footHeight['time'][-1]-footHeight['time'].min())/footHeight['time'].size

    # Load gait cycle phases
    gaitCyclesFileName = "./generateForSimInputs/output/humanGaitCyclesB13.p"
    with open(gaitCyclesFileName, 'r') as pickle_file:
        heelStrikes = pickle.load(pickle_file)
        footOffs = pickle.load(pickle_file)
    # get gait cycles
    nSamples = footHeight['time'].size
    heelStrikeSamples = [int(x) for x in heelStrikes/footHeight['dt']]
    footOffSamples = [int(x) for x in footOffs/footHeight['dt']]
    samples = range(nSamples)
    swing = np.ones(nSamples)
    for strike,off in zip(heelStrikeSamples,footOffSamples):
        if strike>=nSamples: break
        if off>nSamples:off=nSamples
        swing[strike:off]=0

    dwnSamplFcr = int(modulationDt/footHeight['dt'])
    swing = swing[0:-1:dwnSamplFcr]

    stim = {extMuscle:np.zeros(swing.size),
            flexMuscle:np.zeros(swing.size)}
    stim[extMuscle][np.nonzero(swing==0)] = 1
    stim[flexMuscle][np.nonzero(swing)] = 1


    plt.figure()
    plt.plot(footHeight['height'][0:-1:dwnSamplFcr])
    plt.plot(stim[extMuscle]*100,color=colors[extMuscle])
    plt.plot(stim[flexMuscle]*100,color=colors[flexMuscle])

    resultsFolder = "generateForSimInputs/output/"
    fileName = "spatiotemporalStimulationHumanKinBased.p"
    eesModulation = {"modulation":stim, "dt":1000*dwnSamplFcr*footHeight['dt'], "type":"binary"}
    with open(resultsFolder+fileName, 'w') as pickle_file:
    	pickle.dump(eesModulation, pickle_file)

if emgBasedModulation:

    emgFile = "./generateForSimInputs/data/human/HuMoD-database/generatedFiles/Subject_B_speed_1.3_10-Jul-2017_EMG.csv"
    musclesActivation = ldt.readCsvGeneral(emgFile,1,['time',extMuscle,flexMuscle],['time',extMuscleHumod,flexMuscleHumod])
    musclesActivation['dt'] = (musclesActivation['time'][-1]-musclesActivation['time'].min())/musclesActivation['time'].size


    stim = {}
    dwnSamplFcr = int(modulationDt/musclesActivation['dt'])
    plt.figure()
    for muscle in [extMuscle,flexMuscle]:
    	musclesActivation[muscle] -= musclesActivation[muscle].min()
        musclesActivation[muscle] /= musclesActivation[muscle].max()
        tempStim = np.zeros(musclesActivation[muscle].size)
        threshold = musclesActivation[muscle].min() + np.std(musclesActivation[muscle])*0.25
        tempStim[musclesActivation[muscle]>threshold] = 1
        tempStimFilt = et.binary_majority_voting(tempStim,400)
        stim[muscle] = tempStimFilt[0:-1:dwnSamplFcr]

        plt.plot(musclesActivation[muscle],color=colors[muscle])
        plt.plot(tempStimFilt,color=colors[muscle])

    resultsFolder = "generateForSimInputs/output/"
    fileName = "spatiotemporalStimulationHumanEmgBased.p"
    eesModulation = {"modulation":stim, "dt":1000*dwnSamplFcr*musclesActivation['dt'], "type":"binary"}
    with open(resultsFolder+fileName, 'w') as pickle_file:
        pickle.dump(eesModulation, pickle_file)

if kinEmgBasedModulation:

    kinFile = "./generateForSimInputs/data/human/HuMoD-database/generatedFiles/Subject_B_speed_1.3_10-Jul-2017_KIN.csv" # need to check the speed
    footHeight = ldt.readCsvGeneral(kinFile,1,['time','height'],['time','leftToe'])
    footHeight['dt'] = (footHeight['time'][-1]-footHeight['time'].min())/footHeight['time'].size

    emgFile = "./generateForSimInputs/data/human/HuMoD-database/generatedFiles/Subject_B_speed_1.3_10-Jul-2017_EMG.csv"
    musclesActivation = ldt.readCsvGeneral(emgFile,1,['time',extMuscle,flexMuscle],['time',extMuscleHumod,flexMuscleHumod])
    musclesActivation['dt'] = (musclesActivation['time'][-1]-musclesActivation['time'].min())/musclesActivation['time'].size

    # Load gait cycle phases
    gaitCyclesFileName = "./generateForSimInputs/output/humanGaitCyclesB13.p"
    with open(gaitCyclesFileName, 'r') as pickle_file:
        heelStrikes = pickle.load(pickle_file)
        footOffs = pickle.load(pickle_file)
    # get gait cycles
    nSamples = footHeight['time'].size
    heelStrikeSamples = [int(x) for x in heelStrikes/footHeight['dt']]
    footOffSamples = [int(x) for x in footOffs/footHeight['dt']]
    samples = range(nSamples)
    swing = np.ones(nSamples)
    for strike,off in zip(heelStrikeSamples,footOffSamples):
        if strike>=nSamples: break
        if off>nSamples:off=nSamples
        swing[strike:off]=0

    dwnSamplFcrKin = int(modulationDt/footHeight['dt'])
    swingDs = swing[0:-1:dwnSamplFcrKin]

    stimKin = {extMuscle:np.zeros(swingDs.size),
            flexMuscle:np.zeros(swingDs.size)}
    stimKin[extMuscle][np.nonzero(swingDs==0)] = 1
    stimKin[flexMuscle][np.nonzero(swingDs)] = 1

    stim = {}
    dwnSamplFcrEmg = int(modulationDt/musclesActivation['dt'])
    muscelActDs = {}
    for muscle in [extMuscle,flexMuscle]:
    	musclesActivation[muscle] -= musclesActivation[muscle].min()
        musclesActivation[muscle] /= musclesActivation[muscle].max()
        muscelActDs[muscle] = musclesActivation[muscle][0:-1:dwnSamplFcrEmg]
        sizeDiff = stimKin[muscle].size - muscelActDs[muscle].size
        if sizeDiff > 0:
            stimKin[muscle] = stimKin[muscle][:-1-sizeDiff]
        elif sizeDiff < 0:
            for i in range(abs(sizeDiff)):
                stimKin[muscle] = np.append(stimKin[muscle],stimKin[muscle][-1])

        stim[muscle] = np.zeros(muscelActDs[muscle].size)
        #select slices where stimKin is 1
        IndexesStimKinOn = np.squeeze(np.nonzero(stimKin[muscle]==1))

        #perform thresholding with emg
        threshold = muscelActDs[muscle][IndexesStimKinOn].min() + np.std(muscelActDs[muscle][IndexesStimKinOn])*0.75
        indexesThreshold = np.squeeze(np.nonzero(muscelActDs[muscle][IndexesStimKinOn]>threshold))
        indexesSelected = IndexesStimKinOn[indexesThreshold]
        stim[muscle][indexesSelected] = 1

        #majority voting
        stim[muscle] = et.binary_majority_voting(stim[muscle],4)

    # Create figure
    fig,ax = plt.subplots(4)
    ax[0].plot(samples,footHeight['height'],'k')
    ax[0].fill_between(samples, 0, np.max(footHeight['height']), where=swing==0, facecolor='#b0abab', alpha=1)
    ax[0].set_xlim([0,nSamples])

    nSamples = musclesActivation['time'].size
    emgExtFilt = np.copy(musclesActivation[extMuscle])
    emgFlexFilt = np.copy(musclesActivation[flexMuscle])
    windowSize = int(0.05/musclesActivation['dt'])
    for i in xrange(windowSize,nSamples):
        emgExtFilt[i-int(round(windowSize/2))] = musclesActivation[extMuscle][i-windowSize:i].mean()
        emgFlexFilt[i-int(round(windowSize/2))] = musclesActivation[flexMuscle][i-windowSize:i].mean()
    # get gait cycles
    heelStrikeSamples = [int(x) for x in heelStrikes/musclesActivation['dt']]
    footOffSamples = [int(x) for x in footOffs/musclesActivation['dt']]
    samples = range(nSamples)
    swing = np.ones(nSamples)
    for strike,off in zip(heelStrikeSamples,footOffSamples):
        if strike>=nSamples: break
        if off>nSamples:off=nSamples
        swing[strike:off]=0
    ax[1].plot(samples,emgFlexFilt,color=colors[flexMuscle])
    ax[1].fill_between(samples, 0, 1, where=swing==0, facecolor='#b0abab', alpha=1)
    ax[1].set_xlim([0,nSamples])

    ax[2].plot(samples,emgExtFilt,color=colors[extMuscle])
    ax[2].fill_between(samples, 0, 1, where=swing==0, facecolor='#b0abab', alpha=1)
    ax[2].set_xlim([0,nSamples])


    ax[3].plot(range(stim[extMuscle].size),muscelActDs[extMuscle],color=colors[extMuscle])
    ax[3].plot(range(stim[flexMuscle].size),muscelActDs[flexMuscle],color=colors[flexMuscle])
    ax[3].fill_between(range(stim[extMuscle].size),0,1,where=stim[extMuscle]==1,facecolor=colors[extMuscle])
    ax[3].fill_between(range(stim[flexMuscle].size),0,1,where=stim[flexMuscle]==1,facecolor=colors[flexMuscle])
    ax[3].set_xlim([0,stim[flexMuscle].size])

    figName = time.strftime("/%Y_%m_%d_HumanSolPhasicStim.pdf")
    plt.savefig(pathToResults+figName, format="pdf",transparent=True)

    resultsFolder = "generateForSimInputs/output/"
    fileName = "spatiotemporalStimulationHumanKinEmgBased.p"
    eesModulation = {"modulation":stim, "dt":1000*dwnSamplFcrEmg*musclesActivation['dt'], "type":"binary"}
    with open(resultsFolder+fileName, 'w') as pickle_file:
        pickle.dump(eesModulation, pickle_file)

if sensoryKinEmgBasedModulation:
    modulationDtTemp = 0.01

    # load kinematic
    kinFile = "./generateForSimInputs/data/human/HuMoD-database/generatedFiles/Subject_B_speed_1.3_10-Jul-2017_KIN.csv" # need to check the speed
    footHeight = ldt.readCsvGeneral(kinFile,1,['time','height'],['time','leftToe'])
    footHeight['dt'] = (footHeight['time'][-1]-footHeight['time'].min())/footHeight['time'].size

    # Load gait cycle phases
    gaitCyclesFileName = "./generateForSimInputs/output/humanGaitCyclesB13.p"
    with open(gaitCyclesFileName, 'r') as pickle_file:
        heelStrikes = pickle.load(pickle_file)
        footOffs = pickle.load(pickle_file)
    # get gait cycles
    nSamples = footHeight['time'].size
    heelStrikeSamples = [int(x) for x in heelStrikes/footHeight['dt']]
    footOffSamples = [int(x) for x in footOffs/footHeight['dt']]
    samples = range(nSamples)
    swing = np.ones(nSamples)
    for strike,off in zip(heelStrikeSamples,footOffSamples):
        if strike>=nSamples: break
        if off>nSamples:off=nSamples
        swing[strike:off]=0
    dwnSamplFcrKin = int(modulationDtTemp/footHeight['dt'])
    swingDs = swing[0:-1:dwnSamplFcrKin]
    heelStrikeSamples = [int(x/dwnSamplFcrKin) for x in heelStrikeSamples]
    #Load EMGs
    emgFile = "./generateForSimInputs/data/human/HuMoD-database/generatedFiles/Subject_B_speed_1.3_10-Jul-2017_EMG.csv"
    musclesActivation = ldt.readCsvGeneral(emgFile,1,['time',extMuscle,flexMuscle],['time',extMuscleHumod,flexMuscleHumod])
    musclesActivation['dt'] = (musclesActivation['time'][-1]-musclesActivation['time'].min())/musclesActivation['time'].size
    muscelActDs = {}
    dwnSamplFcrEmg = int(modulationDtTemp/musclesActivation['dt'])
    for muscle in [extMuscle,flexMuscle]:
        musclesActivation[muscle] -= musclesActivation[muscle].min()
        musclesActivation[muscle] /= musclesActivation[muscle].max()
        muscelActDs[muscle] = musclesActivation[muscle][0:-1:dwnSamplFcrEmg]

    #Load Sensory
    afferents = {}
    afferents[extMuscle] = {}
    afferents[flexMuscle] = {}
    afferents[flexMuscle]['Iaf'] = gt.load_txt_mpi('../afferentsFirings/meanFr_Ia_TA_humanBl.txt')
    afferents[flexMuscle]['IIf'] = gt.load_txt_mpi('../afferentsFirings/meanFr_II_TA_humanBl.txt')
    afferents[extMuscle]['Iaf'] = gt.load_txt_mpi('../afferentsFirings/meanFr_Ia_SOL_humanBl.txt')
    afferents[extMuscle]['IIf'] = gt.load_txt_mpi('../afferentsFirings/meanFr_II_SOL_humanBl.txt')
    afferents["dt"] = 0.005
    sensoryDs = {}
    dwnSamplFcrSensory = int(modulationDtTemp/afferents["dt"])
    for muscle in [extMuscle,flexMuscle]:
        sensoryDs[muscle] = {}
        sensoryDs[muscle]['Iaf'] = afferents[muscle]['Iaf'][0:-1:dwnSamplFcrSensory]
        sensoryDs[muscle]['IIf'] = afferents[muscle]['IIf'][0:-1:dwnSamplFcrSensory]

    # Extract emg and sensory features for every gaitcycle
    nSamplesAverageGait = np.mean([len(sensoryDs[extMuscle]['Iaf'][heelStrikeSamples[j]:heelStrikeSamples[j+1]-1]) for j in xrange(len(heelStrikeSamples)-1)],dtype=int)
    print nSamplesAverageGait
    sensoryFeaturesGaitcycle = {}
    for muscle in [extMuscle,flexMuscle]:
        sensoryFeaturesGaitcycle[muscle] = {"Iaf":[],"IIf":[],"emg":[]}
    for j in xrange(len(heelStrikeSamples)-1):
        for muscle in [extMuscle,flexMuscle]:
            x = sensoryDs[muscle]['Iaf'][heelStrikeSamples[j]:heelStrikeSamples[j+1]-1]/sensoryDs[muscle]['Iaf'].max()
            ratio = len(x)/float(nSamplesAverageGait)
            sensoryFeaturesGaitcycle[muscle]["Iaf"].append(np.interp(np.arange(0, len(x), ratio), np.arange(0, len(x)), x))
            x = sensoryDs[muscle]['IIf'][heelStrikeSamples[j]:heelStrikeSamples[j+1]-1]/sensoryDs[muscle]['IIf'].max()
            sensoryFeaturesGaitcycle[muscle]["IIf"].append(np.interp(np.arange(0, len(x), ratio), np.arange(0, len(x)), x))
            x = muscelActDs[muscle][heelStrikeSamples[j]:heelStrikeSamples[j+1]-1]/muscelActDs[muscle][0:sensoryDs[muscle]['Iaf'].size].max()
            sensoryFeaturesGaitcycle[muscle]["emg"].append(np.interp(np.arange(0, len(x), ratio), np.arange(0, len(x)), x))

    # Average across every gait cycles
    meanSensoryFeaturesGaitcycle = {}
    for i,muscle in enumerate([extMuscle,flexMuscle]):
        meanSensoryFeaturesGaitcycle[muscle]={}
        meanSensoryFeaturesGaitcycle[muscle]["Iaf"] = np.mean(sensoryFeaturesGaitcycle[muscle]["Iaf"],axis=0)
        semIa = np.std(sensoryFeaturesGaitcycle[muscle]["Iaf"],axis=0)/(np.sqrt(len(sensoryFeaturesGaitcycle[muscle]["Iaf"])-1))
        meanSensoryFeaturesGaitcycle[muscle]["IIf"] = np.mean(sensoryFeaturesGaitcycle[muscle]["IIf"],axis=0)
        semII = np.std(sensoryFeaturesGaitcycle[muscle]["IIf"],axis=0)/(np.sqrt(len(sensoryFeaturesGaitcycle[muscle]["IIf"])-1))
        meanSensoryFeaturesGaitcycle[muscle]["emg"] = np.mean(sensoryFeaturesGaitcycle[muscle]["emg"],axis=0)
        semEmg = np.std(sensoryFeaturesGaitcycle[muscle]["emg"],axis=0)/(np.sqrt(len(sensoryFeaturesGaitcycle[muscle]["emg"])-1))

    # Compute and plot stim template for every gait cycle
    fig,ax=plt.subplots(3,2)
    timeVect =  np.arange(nSamplesAverageGait)
    stimAverageGaitCycle = {}
    for i,muscle in enumerate([extMuscle,flexMuscle]):
        stimAverageGaitCycle[muscle] = np.copy(meanSensoryFeaturesGaitcycle[muscle]["Iaf"])
        stimAverageGaitCycle[muscle] += meanSensoryFeaturesGaitcycle[muscle]["IIf"]
        stimAverageGaitCycle[muscle] += meanSensoryFeaturesGaitcycle[muscle]["emg"]
        stimAverageGaitCycle[muscle] /= stimAverageGaitCycle[muscle].max()
        stimAverageGaitCycle[muscle][stimAverageGaitCycle[muscle]<np.percentile(stimAverageGaitCycle[muscle],75)]=0
        stimAverageGaitCycle[muscle][stimAverageGaitCycle[muscle]>=np.percentile(stimAverageGaitCycle[muscle],75)]=1
        ax[0,i].plot(meanSensoryFeaturesGaitcycle[muscle]["Iaf"],c=colors[muscle])
        ax[0,i].plot(stimAverageGaitCycle[muscle],c=colors[muscle])
        ax[0,i].fill_between(timeVect, meanSensoryFeaturesGaitcycle[muscle]["Iaf"]-semIa, meanSensoryFeaturesGaitcycle[muscle]["Iaf"]+semIa, facecolor=colors[muscle], alpha=0.5)
        ax[1,i].plot(meanSensoryFeaturesGaitcycle[muscle]["IIf"],c=colors[muscle])
        ax[1,i].plot(stimAverageGaitCycle[muscle],c=colors[muscle])
        ax[1,i].fill_between(timeVect, meanSensoryFeaturesGaitcycle[muscle]["IIf"]-semII, meanSensoryFeaturesGaitcycle[muscle]["IIf"]+semII, facecolor=colors[muscle], alpha=0.5)
        ax[2,i].plot(meanSensoryFeaturesGaitcycle[muscle]["emg"],c=colors[muscle])
        ax[2,i].plot(stimAverageGaitCycle[muscle],c=colors[muscle])
        ax[2,i].fill_between(timeVect, meanSensoryFeaturesGaitcycle[muscle]["emg"]-semEmg, meanSensoryFeaturesGaitcycle[muscle]["emg"]+semEmg, facecolor=colors[muscle], alpha=0.5)

    #Compute final stim
    stim = {extMuscle:np.zeros(swingDs.size),
        flexMuscle:np.zeros(swingDs.size)}
    for j in xrange(len(heelStrikeSamples)):
        for muscle in [extMuscle,flexMuscle]:

            if j==0:
                nSamples = heelStrikeSamples[j]-1
                stim[muscle][:nSamples]  = stimAverageGaitCycle[muscle][-nSamples-1:-1]
                nSamples = heelStrikeSamples[j+1]-heelStrikeSamples[j]-1
                ratio = float(nSamplesAverageGait)/nSamples
                x = stimAverageGaitCycle[muscle]
                stimSpecificGait = np.interp(np.arange(0, len(x), ratio), np.arange(0, len(x)), x)
                stim[muscle][heelStrikeSamples[j]:heelStrikeSamples[j+1]-1]  = stimSpecificGait
            elif j==len(heelStrikeSamples)-1:
                nSamples = swingDs.size-heelStrikeSamples[j]
                if nSamples>nSamplesAverageGait:
                    ratio = float(nSamplesAverageGait)/nSamples
                    x = stimAverageGaitCycle[muscle]
                    stimSpecificGait = np.interp(np.arange(0, len(x), ratio), np.arange(0, len(x)), x)
                    stim[muscle][-nSamples-1:-1] = stimSpecificGait
                else:
                    stim[muscle][-nSamples-1:-1] = stimAverageGaitCycle[muscle][0:nSamples]
            else:
                nSamples = heelStrikeSamples[j+1]-heelStrikeSamples[j]-1
                ratio = float(nSamplesAverageGait)/nSamples
                x = stimAverageGaitCycle[muscle]
                stimSpecificGait = np.interp(np.arange(0, len(x), ratio), np.arange(0, len(x)), x)
                stim[muscle][heelStrikeSamples[j]:heelStrikeSamples[j+1]-1]  = stimSpecificGait


    dwnSamplFcr = int(modulationDt/modulationDtTemp)
    plt.figure()
    for muscle in [extMuscle,flexMuscle]:
        stim[muscle] = np.ceil(stim[muscle][0:-1:dwnSamplFcr])
        plt.plot(stim[muscle],c=colors[muscle])
    swingDs = swingDs[0:-1:dwnSamplFcr]
    plt.plot(swingDs,'k')
    plt.show(block=False)

    resultsFolder = "generateForSimInputs/output/"
    fileName = "spatiotemporalStimulationHumanSensoryBased.p"
    eesModulation = {"modulation":stim, "dt":1000*modulationDt, "type":"binary"}
    with open(resultsFolder+fileName, 'w') as pickle_file:
    	pickle.dump(eesModulation, pickle_file)

if proportionalSensoryKinEmgBasedModulation:
    modulationDtTemp = 0.01

    # load kinematic
    kinFile = "./generateForSimInputs/data/human/HuMoD-database/generatedFiles/Subject_B_speed_1.3_10-Jul-2017_KIN.csv" # need to check the speed
    footHeight = ldt.readCsvGeneral(kinFile,1,['time','height'],['time','leftToe'])
    footHeight['dt'] = (footHeight['time'][-1]-footHeight['time'].min())/footHeight['time'].size

    # Load gait cycle phases
    gaitCyclesFileName = "./generateForSimInputs/output/humanGaitCyclesB13.p"
    with open(gaitCyclesFileName, 'r') as pickle_file:
        heelStrikes = pickle.load(pickle_file)
        footOffs = pickle.load(pickle_file)
    # get gait cycles
    nSamples = footHeight['time'].size
    heelStrikeSamples = [int(x) for x in heelStrikes/footHeight['dt']]
    footOffSamples = [int(x) for x in footOffs/footHeight['dt']]
    samples = range(nSamples)
    swing = np.ones(nSamples)
    for strike,off in zip(heelStrikeSamples,footOffSamples):
        if strike>=nSamples: break
        if off>nSamples:off=nSamples
        swing[strike:off]=0
    dwnSamplFcrKin = int(modulationDtTemp/footHeight['dt'])
    swingDs = swing[0:-1:dwnSamplFcrKin]
    heelStrikeSamples = [int(x/dwnSamplFcrKin) for x in heelStrikeSamples]
    #Load EMGs
    emgFile = "./generateForSimInputs/data/human/HuMoD-database/generatedFiles/Subject_B_speed_1.3_10-Jul-2017_EMG.csv"
    musclesActivation = ldt.readCsvGeneral(emgFile,1,['time',extMuscle,flexMuscle],['time',extMuscleHumod,flexMuscleHumod])
    musclesActivation['dt'] = (musclesActivation['time'][-1]-musclesActivation['time'].min())/musclesActivation['time'].size
    muscelActDs = {}
    dwnSamplFcrEmg = int(modulationDtTemp/musclesActivation['dt'])
    for muscle in [extMuscle,flexMuscle]:
        musclesActivation[muscle] -= musclesActivation[muscle].min()
        musclesActivation[muscle] /= musclesActivation[muscle].max()
        muscelActDs[muscle] = musclesActivation[muscle][0:-1:dwnSamplFcrEmg]

    #Load Sensory
    afferents = {}
    afferents[extMuscle] = {}
    afferents[flexMuscle] = {}
    afferents[flexMuscle]['Iaf'] = gt.load_txt_mpi('../afferentsFirings/meanFr_Ia_TA_humanBl.txt')
    afferents[flexMuscle]['IIf'] = gt.load_txt_mpi('../afferentsFirings/meanFr_II_TA_humanBl.txt')
    afferents[extMuscle]['Iaf'] = gt.load_txt_mpi('../afferentsFirings/meanFr_Ia_SOL_humanBl.txt')
    afferents[extMuscle]['IIf'] = gt.load_txt_mpi('../afferentsFirings/meanFr_II_SOL_humanBl.txt')
    afferents["dt"] = 0.005
    sensoryDs = {}
    dwnSamplFcrSensory = int(modulationDtTemp/afferents["dt"])
    for muscle in [extMuscle,flexMuscle]:
        sensoryDs[muscle] = {}
        sensoryDs[muscle]['Iaf'] = afferents[muscle]['Iaf'][0:-1:dwnSamplFcrSensory]
        sensoryDs[muscle]['IIf'] = afferents[muscle]['IIf'][0:-1:dwnSamplFcrSensory]

    # Extract emg and sensory features for every gaitcycle
    nSamplesAverageGait = np.mean([len(sensoryDs[extMuscle]['Iaf'][heelStrikeSamples[j]:heelStrikeSamples[j+1]-1]) for j in xrange(len(heelStrikeSamples)-1)],dtype=int)
    print nSamplesAverageGait
    sensoryFeaturesGaitcycle = {"swing":[]}
    for muscle in [extMuscle,flexMuscle]:
        sensoryFeaturesGaitcycle[muscle] = {"Iaf":[],"IIf":[],"emg":[]}
    for j in xrange(len(heelStrikeSamples)-1):
        for muscle in [extMuscle,flexMuscle]:
            x = sensoryDs[muscle]['Iaf'][heelStrikeSamples[j]:heelStrikeSamples[j+1]-1]/sensoryDs[muscle]['Iaf'].max()
            ratio = len(x)/float(nSamplesAverageGait)
            sensoryFeaturesGaitcycle[muscle]["Iaf"].append(np.interp(np.arange(0, len(x), ratio), np.arange(0, len(x)), x))
            x = sensoryDs[muscle]['IIf'][heelStrikeSamples[j]:heelStrikeSamples[j+1]-1]/sensoryDs[muscle]['IIf'].max()
            sensoryFeaturesGaitcycle[muscle]["IIf"].append(np.interp(np.arange(0, len(x), ratio), np.arange(0, len(x)), x))
            x = muscelActDs[muscle][heelStrikeSamples[j]:heelStrikeSamples[j+1]-1]/muscelActDs[muscle][0:sensoryDs[muscle]['Iaf'].size].max()
            sensoryFeaturesGaitcycle[muscle]["emg"].append(np.interp(np.arange(0, len(x), ratio), np.arange(0, len(x)), x))
        x = swingDs[heelStrikeSamples[j]:heelStrikeSamples[j+1]-1]
        sensoryFeaturesGaitcycle["swing"].append(np.interp(np.arange(0, len(x), ratio), np.arange(0, len(x)), x))

    # Average across every gait cycles
    meanSensoryFeaturesGaitcycle = {}
    for i,muscle in enumerate([extMuscle,flexMuscle]):
        meanSensoryFeaturesGaitcycle[muscle]={}
        meanSensoryFeaturesGaitcycle[muscle]["Iaf"] = np.mean(sensoryFeaturesGaitcycle[muscle]["Iaf"],axis=0)
        semIa = np.std(sensoryFeaturesGaitcycle[muscle]["Iaf"],axis=0)/(np.sqrt(len(sensoryFeaturesGaitcycle[muscle]["Iaf"])-1))
        meanSensoryFeaturesGaitcycle[muscle]["IIf"] = np.mean(sensoryFeaturesGaitcycle[muscle]["IIf"],axis=0)
        semII = np.std(sensoryFeaturesGaitcycle[muscle]["IIf"],axis=0)/(np.sqrt(len(sensoryFeaturesGaitcycle[muscle]["IIf"])-1))
        meanSensoryFeaturesGaitcycle[muscle]["emg"] = np.mean(sensoryFeaturesGaitcycle[muscle]["emg"],axis=0)
        semEmg = np.std(sensoryFeaturesGaitcycle[muscle]["emg"],axis=0)/(np.sqrt(len(sensoryFeaturesGaitcycle[muscle]["emg"])-1))
    meanSensoryFeaturesGaitcycle["swing"] = np.mean(sensoryFeaturesGaitcycle["swing"],axis=0)
    semSwing = np.std(sensoryFeaturesGaitcycle["swing"],axis=0)/(np.sqrt(len(sensoryFeaturesGaitcycle["swing"])-1))
    # Compute and plot stim template for every gait cycle
    fig,ax=plt.subplots(4,2)
    timeVect =  np.arange(nSamplesAverageGait)
    stimAverageGaitCycle = {}
    for i,muscle in enumerate([extMuscle,flexMuscle]):
        stimAverageGaitCycle[muscle] = np.copy(meanSensoryFeaturesGaitcycle[muscle]["Iaf"])
        stimAverageGaitCycle[muscle] += meanSensoryFeaturesGaitcycle[muscle]["IIf"]
        stimAverageGaitCycle[muscle] += meanSensoryFeaturesGaitcycle[muscle]["emg"]
        stimAverageGaitCycle[muscle] /= stimAverageGaitCycle[muscle].max()
        ax[0,i].plot(meanSensoryFeaturesGaitcycle[muscle]["Iaf"],c=colors[muscle])
        ax[0,i].fill_between(timeVect, meanSensoryFeaturesGaitcycle[muscle]["Iaf"]-semIa, meanSensoryFeaturesGaitcycle[muscle]["Iaf"]+semIa, facecolor=colors[muscle], alpha=0.5)
        ax[1,i].plot(meanSensoryFeaturesGaitcycle[muscle]["IIf"],c=colors[muscle])
        ax[1,i].fill_between(timeVect, meanSensoryFeaturesGaitcycle[muscle]["IIf"]-semII, meanSensoryFeaturesGaitcycle[muscle]["IIf"]+semII, facecolor=colors[muscle], alpha=0.5)
        ax[2,i].plot(meanSensoryFeaturesGaitcycle[muscle]["emg"],c=colors[muscle])
        ax[2,i].fill_between(timeVect, meanSensoryFeaturesGaitcycle[muscle]["emg"]-semEmg, meanSensoryFeaturesGaitcycle[muscle]["emg"]+semEmg, facecolor=colors[muscle], alpha=0.5)
        ax[3,i].plot(stimAverageGaitCycle[muscle],c=colors[muscle])
        ax[3,i].plot(meanSensoryFeaturesGaitcycle["swing"],c="#858483")
        ax[3,i].fill_between(timeVect, meanSensoryFeaturesGaitcycle["swing"]-semSwing, meanSensoryFeaturesGaitcycle["swing"]+semSwing, facecolor="#858483", alpha=0.5)
    #Compute final stim
    stim = {extMuscle:np.zeros(swingDs.size),
        flexMuscle:np.zeros(swingDs.size)}
    for j in xrange(len(heelStrikeSamples)):
        for muscle in [extMuscle,flexMuscle]:

            if j==0:
                nSamples = heelStrikeSamples[j]-1
                stim[muscle][:nSamples]  = stimAverageGaitCycle[muscle][-nSamples-1:-1]
                nSamples = heelStrikeSamples[j+1]-heelStrikeSamples[j]-1
                ratio = float(nSamplesAverageGait)/nSamples
                x = stimAverageGaitCycle[muscle]
                stimSpecificGait = np.interp(np.arange(0, len(x), ratio), np.arange(0, len(x)), x)
                stim[muscle][heelStrikeSamples[j]:heelStrikeSamples[j+1]-1]  = stimSpecificGait
            elif j==len(heelStrikeSamples)-1:
                nSamples = swingDs.size-heelStrikeSamples[j]
                if nSamples>nSamplesAverageGait:
                    ratio = float(nSamplesAverageGait)/nSamples
                    x = stimAverageGaitCycle[muscle]
                    stimSpecificGait = np.interp(np.arange(0, len(x), ratio), np.arange(0, len(x)), x)
                    stim[muscle][-nSamples-1:-1] = stimSpecificGait
                else:
                    stim[muscle][-nSamples-1:-1] = stimAverageGaitCycle[muscle][0:nSamples]
            else:
                nSamples = heelStrikeSamples[j+1]-heelStrikeSamples[j]-1
                ratio = float(nSamplesAverageGait)/nSamples
                x = stimAverageGaitCycle[muscle]
                stimSpecificGait = np.interp(np.arange(0, len(x), ratio), np.arange(0, len(x)), x)
                stim[muscle][heelStrikeSamples[j]:heelStrikeSamples[j+1]-1]  = stimSpecificGait


    dwnSamplFcr = int(modulationDt/modulationDtTemp)
    plt.figure()
    for muscle in [extMuscle,flexMuscle]:
        stim[muscle] = stim[muscle][0:-1:dwnSamplFcr]
        plt.plot(stim[muscle],c=colors[muscle])
    swingDs = swingDs[0:-1:dwnSamplFcr]
    plt.plot(swingDs,'k')
    plt.show(block=False)

    resultsFolder = "generateForSimInputs/output/"
    fileName = "spatiotemporalProportionalStimulationHumanSensoryBased.p"
    eesModulation = {"modulation":stim, "dt":1000*modulationDt, "type":"proportional"}
    with open(resultsFolder+fileName, 'w') as pickle_file:
    	pickle.dump(eesModulation, pickle_file)


plt.show()
