import numpy as np
import pandas as pd
from tools import general_tools  as gt
from parameters import HumanParameters as hp
from parameters import RatParameters as rp

def readGlabRecordedAnalogData(file2read,outLabels,signalsName):
    outDict = {}
    dataFrame = pd.read_csv(file2read,header=2,skiprows=[3])
    for label,muscle in zip(outLabels,signalsName):
        outDict[label] = dataFrame[muscle].values
    return outDict

def readCsvGeneral(file2read,headerLines,outLabels,signalsName,sep='\t'):
    outDict = {}
    dataFrame = pd.read_csv(file2read,header=headerLines,sep=sep)
    for label,muscle in zip(outLabels,signalsName):
        outDict[label] = dataFrame[muscle].values
    return outDict

def readOpensimData(file2read,labels,varNames):
    outDict = {}
    dataFrame = pd.read_csv(file2read,header=6,sep='\t')
    for label,varName in zip(labels,varNames):
        outDict[label] = dataFrame[varName].values
    return outDict

def load_afferent_input(species='rat',muscles=None,exp="locomotion"):
    """ Load previously computed affarent inputs """
    afferentsInput = None
    if species == 'rat':
        muscles = {"ext":"GM","flex":"TA"}
        afferents = {}
        afferents[muscles["flex"]] = {}
        afferents[muscles["ext"]] = {}
        if exp == "locomotion":
            afferents[muscles["flex"]]['Iaf'] = list(gt.load_txt_mpi('../afferentsFirings/meanFr_Ia_TA_rat.txt'))
            afferents[muscles["flex"]]['IIf'] = list(gt.load_txt_mpi('../afferentsFirings/meanFr_II_TA_rat.txt'))
            afferents[muscles["ext"]]['Iaf'] = list(gt.load_txt_mpi('../afferentsFirings/meanFr_Ia_GM_rat.txt'))
            afferents[muscles["ext"]]['IIf'] = list(gt.load_txt_mpi('../afferentsFirings/meanFr_II_GM_rat.txt'))
            afferents[muscles["flex"]]['II_RAf_foot'] = list(gt.load_txt_mpi('../afferentsFirings/meanFr_RA_rat.txt'))
            afferents[muscles["flex"]]['II_SAIf_foot'] = list(gt.load_txt_mpi('../afferentsFirings/meanFr_SAI_rat.txt'))
            afferents[muscles["ext"]]['II_RAf_foot'] = list(gt.load_txt_mpi('../afferentsFirings/meanFr_RA_rat.txt'))
            afferents[muscles["ext"]]['II_SAIf_foot'] = list(gt.load_txt_mpi('../afferentsFirings/meanFr_SAI_rat.txt'))
            afferents[muscles["flex"]]['II_RAf'] = list(gt.load_txt_mpi('../afferentsFirings/meanFr_RA_rat.txt'))
            afferents[muscles["flex"]]['II_SAIf'] = list(gt.load_txt_mpi('../afferentsFirings/meanFr_SAI_rat.txt'))
            afferents[muscles["ext"]]['II_RAf'] = list(gt.load_txt_mpi('../afferentsFirings/meanFr_RA_rat.txt'))
            afferents[muscles["ext"]]['II_SAIf'] = list(gt.load_txt_mpi('../afferentsFirings/meanFr_SAI_rat.txt'))
        elif exp == "cybex":
            afferents[muscles["flex"]]['Iaf'] = list(gt.load_txt_mpi('../afferentsFirings/meanFr_Ia_TA_rat_cybex.txt'))
            afferents[muscles["flex"]]['IIf'] = list(gt.load_txt_mpi('../afferentsFirings/meanFr_II_TA_rat_cybex.txt'))
            afferents[muscles["ext"]]['Iaf'] = list(gt.load_txt_mpi('../afferentsFirings/meanFr_Ia_GM_rat_cybex.txt'))
            afferents[muscles["ext"]]['IIf'] = list(gt.load_txt_mpi('../afferentsFirings/meanFr_II_GM_rat_cybex.txt'))
        elif exp == "static":
            fr = rp.get_interneurons_baseline_fr()
            #afferents[muscles["flex"]]['Iaf'] = list(np.random.poisson(lam=fr["Iaf"], size=100000))
            #afferents[muscles["flex"]]['IIf'] = list(np.random.poisson(lam=fr["IIf"], size=100000))
            afferents[muscles["flex"]]['Iaf'] = list(fr["Iaf"]*np.ones(100000))
            afferents[muscles["flex"]]['IIf'] = list(fr["IIf"]*np.ones(100000))
            afferents[muscles["flex"]]['II_RAf_foot'] = list(fr["II_RAf_foot"]*np.ones(100000))
            afferents[muscles["flex"]]['II_SAIf_foot'] = list(fr["II_SAIf_foot"]*np.ones(100000))
            afferents[muscles["flex"]]['II_RAf'] = list(fr["II_SAIf_foot"]*np.ones(100000))
            afferents[muscles["flex"]]['II_SAIf'] = list(fr["II_SAIf_foot"]*np.ones(100000))
            # afferents[muscles["flex"]]['II_RAf_foot'] = list(np.zeros(100000))
            # afferents[muscles["flex"]]['II_SAIf_foot'] = list(np.zeros(100000))
            # afferents[muscles["flex"]]['II_RAf'] = list(np.zeros(100000))
            # afferents[muscles["flex"]]['II_SAIf'] = list(np.zeros(100000))
            #afferents[muscles["ext"]]['Iaf'] = list(np.random.poisson(lam=fr["Iaf"], size=100000))
            #afferents[muscles["ext"]]['IIf'] = list(np.random.poisson(lam=fr["IIf"], size=100000))
            afferents[muscles["ext"]]['Iaf'] = list(fr["Iaf"]*np.ones(100000))
            afferents[muscles["ext"]]['IIf'] = list(fr["IIf"]*np.ones(100000))
            afferents[muscles["ext"]]['II_RAf_foot'] = list(fr["II_RAf_foot"]*np.ones(100000))
            afferents[muscles["ext"]]['II_SAIf_foot'] = list(fr["II_SAIf_foot"]*np.ones(100000))
            afferents[muscles["ext"]]['II_RAf'] = list(fr["II_SAIf_foot"]*np.ones(100000))
            afferents[muscles["ext"]]['II_SAIf'] = list(fr["II_SAIf_foot"]*np.ones(100000))
            # afferents[muscles["ext"]]['II_RAf_foot'] = list(np.zeros(100000))
            # afferents[muscles["ext"]]['II_SAIf_foot'] = list(np.zeros(100000))
            # afferents[muscles["ext"]]['II_RAf'] = list(np.zeros(100000))
            # afferents[muscles["ext"]]['II_SAIf'] = list(np.zeros(100000))
        dtUpdateAfferent = 5
        afferentsInput = [afferents,dtUpdateAfferent]
    elif species == 'human':
        if not muscles: muscles = hp.get_muscles_dict()
        if not muscles["flex"]=="TA": raise(Exception("Invalid flex muscle"))
        afferents = {}
        afferents[muscles["flex"]] = {}
        afferents[muscles["ext"]] = {}
        if exp == "locomotion":
            afferents[muscles["flex"]]['Iaf'] = list(gt.load_txt_mpi(hp.get_flex_Ia_afferents_locomotion_files()))
            afferents[muscles["flex"]]['IIf'] = list(gt.load_txt_mpi(hp.get_flex_II_afferents_locomotion_files()))
            afferents[muscles["ext"]]['Iaf'] = list(gt.load_txt_mpi(hp.get_ext_Ia_afferents_locomotion_files()))
            afferents[muscles["ext"]]['IIf'] = list(gt.load_txt_mpi(hp.get_ext_II_afferents_locomotion_files()))
        elif exp == "cybex":
            afferents[muscles["flex"]]['Iaf'] = list(gt.load_txt_mpi('../afferentsFirings/meanFr_Ia_TA_human_cybex.txt'))
            afferents[muscles["flex"]]['IIf'] = list(gt.load_txt_mpi('../afferentsFirings/meanFr_II_TA_human_cybex.txt'))
            if muscles["ext"] == "GL":
                afferents[muscles["ext"]]['Iaf'] = list(gt.load_txt_mpi('../afferentsFirings/meanFr_Ia_GL_human_cybex.txt'))
                afferents[muscles["ext"]]['IIf'] = list(gt.load_txt_mpi('../afferentsFirings/meanFr_II_GL_human_cybex.txt'))
            elif muscles["ext"] == "SOL":
                afferents[muscles["ext"]]['Iaf'] = list(gt.load_txt_mpi('../afferentsFirings/meanFr_Ia_SOL_human_cybex.txt'))
                afferents[muscles["ext"]]['IIf'] = list(gt.load_txt_mpi('../afferentsFirings/meanFr_II_SOL_human_cybex.txt'))
            else: raise(Exception("Invalid ext muscle"))
        dtUpdateAfferent = 5
        afferentsInput = [afferents,dtUpdateAfferent]
    return afferentsInput
