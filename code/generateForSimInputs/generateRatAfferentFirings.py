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

dt = 0.005

lengthFile = "./generateForSimInputs/data/rat/GMTA_fiberLength_static.txt"
fiberLengthRange = ldt.readOpensimData(lengthFile,['angle','ext','flex'],['ankle_flx','MG','TA'])

gaitFile = "./generateForSimInputs/data/rat/GMTA_fiberLength_locomotion.txt"
fiberLengthGait = ldt.readOpensimData(gaitFile,['time','ext','flex'],["Coordinates(Deg.)",'MG','TA'])
fiberLengthGait['dt'] = (fiberLengthGait['time'][-1]-fiberLengthGait['time'].min())/fiberLengthGait['time'].size

emgFile = "./generateForSimInputs/data/rat/#208_100903_P0_BIP_TM9_4_ANA.csv"
musclesActivation = ldt.readGlabRecordedAnalogData(emgFile,['ext','flex'],['RMG','RTA'])
musclesActivation['dt'] = 0.0005
musclesActivation['time'] = np.arange(len(musclesActivation['ext']))*musclesActivation['dt']
for muscle in ['ext','flex']:
	musclesActivation[muscle] = et.compute_envelope(musclesActivation[muscle],musclesActivation['dt']*1000)

kinFile = "./generateForSimInputs/data/rat/#208_100903_P0_BIP_TM9_4_KIN.csv"
footHeight = ldt.readGlabRecordedAnalogData(kinFile,['height'],["RTip_Z"])
footHeight['dt'] = 0.005
footHeight['time'] = np.arange(len(footHeight['height']))*footHeight['dt']

eventFile = "./generateForSimInputs/data/rat/#208_100903_P0_BIP_TM9_4_EVENTS.p"
restingAngle = 0

ai = AfferentInput(dt,restingAngle,fiberLengthRange,fiberLengthGait,musclesActivation,footHeight,eventFile)
SAI = ai.computeSAIFr("_rat")
RA = ai.computeRAFr("_rat")
IIFlex,IIExt =ai.computeIIFr("_rat")
IAFlex,IAExt =ai.computeIaFr("_rat")

motFile = "./generateForSimInputs/data/rat/generatedFiles/Rat208_matlabAll_19-Apr-2017.mot"
kinematic = ldt.readCsvGeneral(motFile,8,['time','ankle_flx',"hip_flx","knee_flx"],['time','ankle_flx',"hip_flx","knee_flx"])
kinematic['dt'] = (kinematic['time'][-1]-kinematic['time'].min())/kinematic['time'].size

""" Generate figures """


fig,ax = plt.subplots(6)
ax[0].plot(ai.get_fiber_length_locomotion()[0],color='b')
ax[0].plot(ai.get_fiber_length_locomotion()[1],color='r')
ax[0].plot([0,len(ai.get_fiber_length_locomotion()[0])],[ai.get_fiber_length_rest()[0],ai.get_fiber_length_rest()[0]],color='b')
ax[0].plot([0,len(ai.get_fiber_length_locomotion()[0])],[ai.get_fiber_length_rest()[1],ai.get_fiber_length_rest()[1]],color='r')

ax[1].plot(ai.get_emg_locomotion()[0],color='b')
ax[1].plot(ai.get_emg_locomotion()[1],color='r')

ax[2].plot(IAExt,color='b')
ax[2].plot(IAFlex,color='r')

ax[3].plot(IIExt,color='b')
ax[3].plot(IIFlex,color='r')

ax[4].plot(SAI,color='k')
ax[5].plot(RA,color='k')

fig,ax = plt.subplots(3,sharey=True)
fig.suptitle('kinematics')
ax[0].plot(kinematic['time'],kinematic['hip_flx'])
ax[0].set_ylabel('hip')
ax[1].plot(kinematic['time'],kinematic['knee_flx'])
ax[1].set_ylabel('knee')
ax[2].plot(kinematic['time'],kinematic['ankle_flx'])
ax[2].set_ylabel('ankle')

fig,ax = plt.subplots(1,sharey=True)
fig.suptitle('Foot height')
ax.plot(footHeight['time'],footHeight['height'])
ax.set_ylabel('height (mm)')


""" Generate figures """
redAi = "#e9342f"
bluAi = "#00aaeb"
# Smooth the data with a moving average
nSamples = len(IAExt)
IAExtFilt = np.zeros(nSamples)
IAFlexFilt = np.zeros(nSamples)
IIExtFilt = np.zeros(nSamples)
IIFlexFilt = np.zeros(nSamples)
SAIFilt = np.zeros(nSamples)
RAFilt = np.zeros(nSamples)
windowSize = int(0.05/dt)
for i in xrange(windowSize,nSamples):
	IAExtFilt[i-int(round(windowSize/2))] = IAExt[i-windowSize:i].mean()
	IAFlexFilt[i-int(round(windowSize/2))] = IAFlex[i-windowSize:i].mean()
	IIExtFilt[i-int(round(windowSize/2))] = IIExt[i-windowSize:i].mean()
	IIFlexFilt[i-int(round(windowSize/2))] = IIFlex[i-windowSize:i].mean()
	SAIFilt[i-int(round(windowSize/2))] = SAI[i-windowSize:i].mean()
	RAFilt[i-int(round(windowSize/2))] = RA[i-windowSize:i].mean()

emgExtFilt = np.zeros(nSamples)
emgFlexFilt = np.zeros(nSamples)
windowSize = int(0.05/dt)
for i in xrange(windowSize,nSamples):
	emgExtFilt[i-int(round(windowSize/2))] = np.array(ai.get_emg_locomotion()[0])[i-windowSize:i].mean()
	emgFlexFilt[i-int(round(windowSize/2))] = np.array(ai.get_emg_locomotion()[1])[i-windowSize:i].mean()

# Load gait cycle phases
gaitCyclesFileName = "./generateForSimInputs/output/ratGaitCycles.p"
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
fig,ax = plt.subplots(6)

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

ax[4].plot(SAIFilt,color="k")
ax[4].fill_between(samples, 0, 50, where=stance, facecolor='#b0abab', alpha=1)
ax[4].set_ylabel('SAI fr')

ax[5].plot(RAFilt,color='k')
ax[5].fill_between(samples, 0, 50, where=stance, facecolor='#b0abab', alpha=1)
ax[5].set_ylabel('RA fr')

# get gait cycles
nSamples = len(kinematic['time'])
heelStrikeSamples = [int(x) for x in heelStrikes/kinematic['dt']]
footOffSamples = [int(x) for x in footOffs/kinematic['dt']]
samples = range(nSamples)
stance = np.zeros(nSamples).astype(bool)
for strike,off in zip(heelStrikeSamples,footOffSamples):
	if strike>nSamples: break
	stance[strike:off]=True
# Figure 2 - kinematics
fig,ax = plt.subplots(3,sharey=True)
fig.suptitle('kinematics')
ax[0].plot(kinematic['time'],kinematic["hip_flx"])
ax[0].fill_between(kinematic['time'], min(kinematic["hip_flx"]), max(kinematic["hip_flx"]), where=stance, facecolor='#b0abab', alpha=1)
ax[0].set_ylabel('hip')
ax[1].plot(kinematic['time'],kinematic["knee_flx"])
ax[1].fill_between(kinematic['time'], min(kinematic["knee_flx"]), max(kinematic["knee_flx"]), where=stance, facecolor='#b0abab', alpha=1)
ax[1].set_ylabel('knee')
ax[2].plot(kinematic['time'],kinematic["ankle_flx"])
ax[2].fill_between(kinematic['time'], min(kinematic["ankle_flx"]), max(kinematic["ankle_flx"]), where=stance, facecolor='#b0abab', alpha=1)
ax[2].set_ylabel('ankle')


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

figName = time.strftime("/%Y_%m_%d_RatAfferentsFirings.pdf")
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
ax[0].plot(kinematic['time'][startPlot:stopPlot],kinematic["hip_flx"][startPlot:stopPlot])
ax[0].fill_between(kinematic['time'][startPlot:stopPlot], min(kinematic["hip_flx"][startPlot:stopPlot]), max(kinematic["hip_flx"][startPlot:stopPlot]), where=reducedStance, facecolor='#b0abab', alpha=1)
ax[0].set_ylabel('hip')
ax[1].plot(kinematic['time'][startPlot:stopPlot],kinematic["knee_flx"][startPlot:stopPlot])
ax[1].fill_between(kinematic['time'][startPlot:stopPlot], min(kinematic["knee_flx"][startPlot:stopPlot]), max(kinematic["knee_flx"][startPlot:stopPlot]), where=reducedStance, facecolor='#b0abab', alpha=1)
ax[1].set_ylabel('knee')
ax[2].plot(kinematic['time'][startPlot:stopPlot],kinematic["ankle_flx"][startPlot:stopPlot])
ax[2].fill_between(kinematic['time'][startPlot:stopPlot], min(kinematic["ankle_flx"][startPlot:stopPlot]), max(kinematic["ankle_flx"][startPlot:stopPlot]), where=reducedStance, facecolor='#b0abab', alpha=1)
ax[2].set_ylabel('ankle')

figName = time.strftime("/%Y_%m_%d_RatKin.pdf")
plt.savefig(pathToResults+figName, format="pdf",transparent=True)



plt.show()
