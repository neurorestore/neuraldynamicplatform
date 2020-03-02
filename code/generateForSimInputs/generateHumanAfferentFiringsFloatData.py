import sys
sys.path.append('../code')
from tools import load_data_tools as ldt
from tools import emg_tools as et
from AfferentInput import AfferentInput
import matplotlib.pyplot as plt
import numpy as np
import pickle
import time

pathToResults = "../../results"

halfROMankle = -12 # Roaas, Asbjorn, and Gunnar BJ Andersson. "Normal range of motion of the hip, knee and ankle joints in male subjects, 30-40 years of age." Acta Orthopaedica Scandinavica 53.2 (1982): 205-208.
halfROMknee = -71 # Roaas, Asbjorn, and Gunnar BJ Andersson. "Normal range of motion of the hip, knee and ankle joints in male subjects, 30-40 years of age." Acta Orthopaedica Scandinavica 53.2 (1982): 205-208.

restingAngle = -5.2
normFactorIa = 0.25
normFactorII = 0.2

dt = 0.005
subject = "floatPaperJB"

side = "l"
SIDE = "L"
flexMuscleOsim = "tib_ant"
extMuscleOsim = "soleus" # soleus_l or med_gas_l
flexMuscleHumod = "TA"
extMuscleHumod = "SOL" # SOL_L or GL_L
flexMuscleOut = "TA"
extMuscleOut = "SOL" # SOL or GL
ankleAngleOpenSim = "ankle_angle"
kneeAngleOpenSim = "knee_angle"
hipAngleOpenSim = "hip_flexion"


lengthFile = "./generateForSimInputs/data/human/HuMoD-database/openSimOutputs/humanHumoD_B_ankleRangeWithKneeAt30deg.txt" #Knee at 30 deg
fiberLengthRange = ldt.readOpensimData(lengthFile,['angle','ext','flex'],['ankle_angle_l',extMuscleOsim+"_l",flexMuscleOsim+"_l"])


gaitFile = "./generateForSimInputs/data/human/floatData/openSimOutputs/H_JBM_20150109_04TM_NF_01_30-Apr-2018.txt"
fiberLengthGait = ldt.readOpensimData(gaitFile,['time','ext','flex'],["Coordinates(Deg.)",extMuscleOsim+"_"+side,flexMuscleOsim+"_"+side])
fiberLengthGait['dt'] = (fiberLengthGait['time'][-1]-fiberLengthGait['time'].min())/fiberLengthGait['time'].size

emgFile = "./generateForSimInputs/data/human/floatData/generatedFiles/H_JBM_20150109_04TM_NF_01_30-Apr-2018_EMG.csv"
musclesActivation = ldt.readCsvGeneral(emgFile,1,['time','ext','flex'],['time',extMuscleHumod+"_"+SIDE,flexMuscleHumod+"_"+SIDE])
musclesActivation['dt'] = (musclesActivation['time'][-1]-musclesActivation['time'].min())/musclesActivation['time'].size

kinFile = "./generateForSimInputs/data/human/floatData/generatedFiles/H_JBM_20150109_04TM_NF_01_30-Apr-2018_KIN.csv"
footHeight = ldt.readCsvGeneral(kinFile,1,['time','height'],['time','leftToe'])
footHeight['dt'] = (footHeight['time'][-1]-footHeight['time'].min())/footHeight['time'].size

motFile = "./generateForSimInputs/data/human/floatData/generatedFiles/H_JBM_20150109_04TM_NF_01_30-Apr-2018.mot"

ai = AfferentInput(dt,restingAngle,fiberLengthRange,fiberLengthGait,musclesActivation,footHeight)
IIFlex,IIExt =ai.computeIIFr("_human"+subject+side,normFactorII,[extMuscleOut,flexMuscleOut])
IAFlex,IAExt =ai.computeIaFr("_human"+subject+side,normFactorIa,[extMuscleOut,flexMuscleOut])

kinematic = ldt.readCsvGeneral(motFile,8,['time',ankleAngleOpenSim+"_"+side,hipAngleOpenSim+"_"+side,kneeAngleOpenSim+"_"+side],['time',ankleAngleOpenSim+"_"+side,hipAngleOpenSim+"_"+side,kneeAngleOpenSim+"_"+side])
kinematic['dt'] = (kinematic['time'][-1]-kinematic['time'].min())/kinematic['time'].size

""" Generate figures """
redAi = "#e9342f"
bluAi = "#00aaeb"
# Smooth the data with a moving average
nSamples = len(IAExt)
IAExtFilt = np.zeros(nSamples)
IAFlexFilt = np.zeros(nSamples)
IIExtFilt = np.zeros(nSamples)
IIFlexFilt = np.zeros(nSamples)
windowSize = int(0.05/dt)
for i in xrange(windowSize,nSamples):
	IAExtFilt[i-int(round(windowSize/2))] = IAExt[i-windowSize:i].mean()
	IAFlexFilt[i-int(round(windowSize/2))] = IAFlex[i-windowSize:i].mean()
	IIExtFilt[i-int(round(windowSize/2))] = IIExt[i-windowSize:i].mean()
	IIFlexFilt[i-int(round(windowSize/2))] = IIFlex[i-windowSize:i].mean()

emgExtFilt = np.zeros(nSamples)
emgFlexFilt = np.zeros(nSamples)
windowSize = int(0.05/dt)
for i in xrange(windowSize,nSamples):
	emgExtFilt[i-int(round(windowSize/2))] = np.array(ai.get_emg_locomotion()[0])[i-windowSize:i].mean()
	emgFlexFilt[i-int(round(windowSize/2))] = np.array(ai.get_emg_locomotion()[1])[i-windowSize:i].mean()

# Load gait cycle phases
gaitCyclesFileName = "./generateForSimInputs/output/humanGaitCyclesFloat.p"
with open(gaitCyclesFileName, 'r') as pickle_file:
	heelStrikes = pickle.load(pickle_file)
	footOffs = pickle.load(pickle_file)

# get gait cycles
heelStrikeSamples = [int(x) for x in heelStrikes/dt]
footOffSamples = [int(x) for x in footOffs/dt]
samples = range(nSamples)
stance = np.zeros(nSamples).astype(bool)
for strike,off in zip(heelStrikeSamples,footOffSamples):
	if strike>nSamples: break
	stance[strike:off]=True
# Figure 1 - afferents and muscles stretch
fig,ax = plt.subplots(4)

ax[0].plot(ai.get_fiber_length_locomotion()[0],color=redAi,label='ext')
ax[0].plot(ai.get_fiber_length_locomotion()[1],color=bluAi,label='flex')
ax[0].plot([0,len(ai.get_fiber_length_locomotion()[0])],[ai.get_fiber_length_rest()[0],ai.get_fiber_length_rest()[0]],color=redAi)
ax[0].plot([0,len(ai.get_fiber_length_locomotion()[0])],[ai.get_fiber_length_rest()[1],ai.get_fiber_length_rest()[1]],color=bluAi)
ax[0].fill_between(samples, 0, np.max(ai.get_fiber_length_locomotion()), where=stance, facecolor='#b0abab', alpha=1)
ax[0].set_ylabel('fiber length')
ax[0].legend()

ax[1].plot(emgExtFilt,color=redAi)
ax[1].plot(emgFlexFilt,color=bluAi)
ax[1].fill_between(samples, 0, 1, where=stance, facecolor='#b0abab', alpha=1)
ax[1].set_ylabel('emg')

ax[2].plot(IAExtFilt,color=redAi)
ax[2].plot(IAFlexFilt,color=bluAi)
ax[2].fill_between(samples, 0, 50, where=stance, facecolor='#b0abab', alpha=1)
ax[2].set_ylabel('Ia fr')

ax[3].plot(IIExtFilt,color=redAi)
ax[3].plot(IIFlexFilt,color=bluAi)
ax[3].fill_between(samples, 0, 50, where=stance, facecolor='#b0abab', alpha=1)
ax[3].set_ylabel('II fr')

# get gait cycles
nSamples = len(kinematic['time'])
heelStrikeSamples = [int(x) for x in heelStrikes/kinematic['dt']]
footOffSamples = [int(x) for x in footOffs/kinematic['dt']]
samples = range(nSamples)
stance = np.zeros(nSamples).astype(bool)
for strike,off in zip(heelStrikeSamples,footOffSamples):
	if strike>nSamples: break
	stance[strike:off]=True

fileName = time.strftime("/%Y_%m_%d_afferentsAndMuscleStretch"+subject+side+flexMuscleOut+extMuscleOut+".pdf")
plt.savefig(pathToResults+fileName, format="pdf",transparent=True)


# Figure 2 - kinematics
fig,ax = plt.subplots(3,sharey=True)
fig.suptitle('kinematics')
ax[0].plot(kinematic['time'],kinematic[hipAngleOpenSim+"_"+side])
ax[0].fill_between(kinematic['time'], min(kinematic[hipAngleOpenSim+"_"+side]), max(kinematic[hipAngleOpenSim+"_"+side]), where=stance, facecolor='#b0abab', alpha=1)
ax[0].set_ylabel('hip')
ax[1].plot(kinematic['time'],kinematic[kneeAngleOpenSim+"_"+side])
ax[1].fill_between(kinematic['time'], min(kinematic[kneeAngleOpenSim+"_"+side]), max(kinematic[kneeAngleOpenSim+"_"+side]), where=stance, facecolor='#b0abab', alpha=1)
ax[1].set_ylabel('knee')
ax[2].plot(kinematic['time'],kinematic[ankleAngleOpenSim+"_"+side])
ax[2].fill_between(kinematic['time'], min(kinematic[ankleAngleOpenSim+"_"+side]), max(kinematic[ankleAngleOpenSim+"_"+side]), where=stance, facecolor='#b0abab', alpha=1)
ax[2].set_ylabel('ankle')

fileName = time.strftime("/%Y_%m_%d_kinematics"+subject+side+flexMuscleOut+extMuscleOut+".pdf")
plt.savefig(pathToResults+fileName, format="pdf",transparent=True)

# get gait cycles
nSamples = len(footHeight['time'])
heelStrikeSamples = [int(x) for x in heelStrikes/footHeight['dt']]
footOffSamples = [int(x) for x in footOffs/footHeight['dt']]
samples = range(nSamples)
stance = np.zeros(nSamples).astype(bool)
for strike,off in zip(heelStrikeSamples,footOffSamples):
	if strike>nSamples: break
	stance[strike:off]=True
#Figure 3 - foot height
fig,ax = plt.subplots(1,sharey=True)
fig.suptitle('foot height')
ax.plot(footHeight['time'],footHeight["height"])
ax.fill_between(footHeight['time'], min(footHeight["height"]), max(footHeight["height"]), where=stance, facecolor='#b0abab', alpha=1)
ax.set_ylabel('foot height')

""" plots with only 1 gait cycle """
startGaitCycleN = 2

# get gait cycles
nSamples = len(IAExt)
heelStrikeSamples = [int(x) for x in heelStrikes/dt]
footOffSamples = [int(x) for x in footOffs/dt]
samples = range(nSamples)
stance = np.zeros(nSamples).astype(bool)
for strike,off in zip(heelStrikeSamples,footOffSamples):
	if strike>nSamples: break
	stance[strike:off]=True
startPlot = heelStrikeSamples[startGaitCycleN-1]
stopPlot = heelStrikeSamples[startGaitCycleN]
if stopPlot>nSamples: stopPlot=nSamples
reducedSamples = range(stopPlot-startPlot)
reducedStance = stance[startPlot:stopPlot]
# Figure 1bis - afferents and muscles stretch
fig,ax = plt.subplots(4)

ax[0].plot(ai.get_fiber_length_locomotion()[0][startPlot:stopPlot],color=redAi,label='ext')
ax[0].plot(ai.get_fiber_length_locomotion()[1][startPlot:stopPlot],color=bluAi,label='flex')
ax[0].plot([0,len(reducedSamples)],[ai.get_fiber_length_rest()[0],ai.get_fiber_length_rest()[0]],color=redAi)
ax[0].plot([0,len(reducedSamples)],[ai.get_fiber_length_rest()[1],ai.get_fiber_length_rest()[1]],color=bluAi)
ax[0].fill_between(reducedSamples, 0, np.max(ai.get_fiber_length_locomotion()), where=reducedStance, facecolor='#b0abab', alpha=1)
ax[0].set_ylabel('fiber length')
ax[0].legend()

ax[1].plot(emgExtFilt[startPlot:stopPlot],color=redAi)
ax[1].plot(emgFlexFilt[startPlot:stopPlot],color=bluAi)
ax[1].fill_between(reducedSamples, 0, 1, where=reducedStance, facecolor='#b0abab', alpha=1)
ax[1].set_ylabel('emg')

ax[2].plot(IAExtFilt[startPlot:stopPlot],color=redAi)
ax[2].plot(IAFlexFilt[startPlot:stopPlot],color=bluAi)
ax[2].fill_between(reducedSamples, 0, 50, where=reducedStance, facecolor='#b0abab', alpha=1)
ax[2].set_ylabel('Ia fr')

ax[3].plot(IIExtFilt[startPlot:stopPlot],color=redAi)
ax[3].plot(IIFlexFilt[startPlot:stopPlot],color=bluAi)
ax[3].fill_between(reducedSamples, 0, 50, where=reducedStance, facecolor='#b0abab', alpha=1)
ax[3].set_ylabel('II fr')

figName = time.strftime("/%Y_%m_%d_HumanAfferentsFirings_"+subject+side+flexMuscleOut+extMuscleOut+".pdf")
plt.savefig(pathToResults+figName, format="pdf",transparent=True)

# get gait cycles
nSamples = len(kinematic['time'])
heelStrikeSamples = [int(x) for x in heelStrikes/kinematic['dt']]
footOffSamples = [int(x) for x in footOffs/kinematic['dt']]
samples = range(nSamples)
stance = np.zeros(nSamples).astype(bool)
for strike,off in zip(heelStrikeSamples,footOffSamples):
	if strike>nSamples: break
	stance[strike:off]=True
startPlot = heelStrikeSamples[startGaitCycleN-1]
stopPlot = heelStrikeSamples[startGaitCycleN]
if stopPlot>nSamples: stopPlot=nSamples
reducedSamples = range(stopPlot-startPlot)
reducedStance = stance[startPlot:stopPlot]
# Figure 2 - kinematics
fig,ax = plt.subplots(3,sharey=True)
fig.suptitle('kinematics')
ax[0].plot(kinematic['time'][startPlot:stopPlot],kinematic[hipAngleOpenSim+"_"+side][startPlot:stopPlot])
ax[0].fill_between(kinematic['time'][startPlot:stopPlot], min(kinematic[hipAngleOpenSim+"_"+side][startPlot:stopPlot]), max(kinematic[hipAngleOpenSim+"_"+side][startPlot:stopPlot]), where=reducedStance, facecolor='#b0abab', alpha=1)
ax[0].set_ylabel('hip')
ax[1].plot(kinematic['time'][startPlot:stopPlot],kinematic[kneeAngleOpenSim+"_"+side][startPlot:stopPlot])
ax[1].fill_between(kinematic['time'][startPlot:stopPlot], min(kinematic[kneeAngleOpenSim+"_"+side][startPlot:stopPlot]), max(kinematic[kneeAngleOpenSim+"_"+side][startPlot:stopPlot]), where=reducedStance, facecolor='#b0abab', alpha=1)
ax[1].set_ylabel('knee')
ax[2].plot(kinematic['time'][startPlot:stopPlot],kinematic[ankleAngleOpenSim+"_"+side][startPlot:stopPlot])
ax[2].fill_between(kinematic['time'][startPlot:stopPlot], min(kinematic[ankleAngleOpenSim+"_"+side][startPlot:stopPlot]), max(kinematic[ankleAngleOpenSim+"_"+side][startPlot:stopPlot]), where=reducedStance, facecolor='#b0abab', alpha=1)
ax[2].set_ylabel('ankle')

figName = time.strftime("/%Y_%m_%d_HumanKin_"+subject+side+flexMuscleOut+extMuscleOut+".pdf")
plt.savefig(pathToResults+figName, format="pdf",transparent=True)



plt.show()
