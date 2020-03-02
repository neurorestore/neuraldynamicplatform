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
proportionalSensoryKinEmgBasedModulation = True

DEBUG = True
flexMuscle = "TA"
extMuscle = "SOL" #SOL or GL
flexMuscleHumod = "TA_L"
extMuscleHumod = "SOL_L"

colors={flexMuscle:"#00aaeb",extMuscle:"#e9342f"}


if proportionalSensoryKinEmgBasedModulation:
    modulationDtTemp = 0.01

    # load kinematic
    kinFile = "./generateForSimInputs/data/human/floatData/generatedFiles/H_JBM_20150109_04TM_NF_01_30-Apr-2018_KIN.csv" # need to check the speed
    footHeight = ldt.readCsvGeneral(kinFile,1,['time','height'],['time','leftToe'])
    footHeight['dt'] = (footHeight['time'][-1]-footHeight['time'].min())/footHeight['time'].size

    # Load gait cycle phases
    gaitCyclesFileName = "./generateForSimInputs/output/humanGaitCyclesFloat.p"
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
    emgFile = "./generateForSimInputs/data/human/floatData/generatedFiles/H_JBM_20150109_04TM_NF_01_30-Apr-2018_EMG.csv"
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
    afferents[flexMuscle]['Iaf'] = gt.load_txt_mpi('../afferentsFirings/meanFr_Ia_TA_humanfloatPaperJBl.txt')
    afferents[flexMuscle]['IIf'] = gt.load_txt_mpi('../afferentsFirings/meanFr_II_TA_humanfloatPaperJBl.txt')
    afferents[extMuscle]['Iaf'] = gt.load_txt_mpi('../afferentsFirings/meanFr_Ia_SOL_humanfloatPaperJBl.txt')
    afferents[extMuscle]['IIf'] = gt.load_txt_mpi('../afferentsFirings/meanFr_II_SOL_humanfloatPaperJBl.txt')
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
    figName = time.strftime("/_%Y_%m_%d_HumanFloatPhasicStim.pdf")
    plt.savefig(pathToResults+figName, format="pdf",transparent=True)


    #Compute final stim
    # Here we reload old gait cycles phases to compute the stim wrt the old phases
    # load kinematic
    kinFile = "./generateForSimInputs/data/human/HuMoD-database/generatedFiles/Subject_B_speed_1.3_10-Jul-2017_KIN.csv"
    footHeight = ldt.readCsvGeneral(kinFile,1,['time','height'],['time','leftToe'])
    footHeight['dt'] = (footHeight['time'][-1]-footHeight['time'].min())/footHeight['time'].size

    # Load gait cycle phases
    gaitCyclesFileName = "./generateForSimInputs/output/humanGaitCyclesB13.p"
    with open(gaitCyclesFileName, 'r') as pickle_file:
        heelStrikes = pickle.load(pickle_file)
        footOffs = pickle.load(pickle_file)
    # Get other trial gait cycles
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


    # Here we start computing the stim profile scpeicifc the extracted gait cycles
    #TODO need to discuss this
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
    fileName = "spatiotemporalProportionalStimulationHumanSensoryBased_fromFloatDataForHumData.p"
    eesModulation = {"modulation":stim, "dt":1000*modulationDt, "type":"proportional"}
    with open(resultsFolder+fileName, 'w') as pickle_file:
    	pickle.dump(eesModulation, pickle_file)


plt.show()
