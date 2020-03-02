import sys
sys.path.append('../code')
from tools import load_data_tools as ldt
from tools import emg_tools as et
from AfferentInput import AfferentInput
import matplotlib.pyplot as plt
import numpy as np

restingAngle = 0
normFactor = 0.25

dt = 0.005

lengthFile = "./generateForSimInputs/data/human/HuMoD-database/openSimOutputs/humanHumoD_B_ankleRange.txt"
fiberLengthRange = ldt.readOpensimData(lengthFile,['angle','ext','flex'],['ankle_angle_l','soleus_l','tib_ant_l'])


cybex = "./generateForSimInputs/data/human/cybex/cybexHuman.txt"
fiberLengthGait = ldt.readOpensimData(cybex,['time','ext','flex'],["Coordinates(Deg.)",'soleus_r','tib_ant_r'])
fiberLengthGait['dt'] = (fiberLengthGait['time'][-1]-fiberLengthGait['time'].min())/fiberLengthGait['time'].size


musclesActivation = ldt.readOpensimData(cybex,['time','ext','flex'],["Coordinates(Deg.)",'soleus_r','tib_ant_r'])
musclesActivation['dt'] = (musclesActivation['time'][-1]-musclesActivation['time'].min())/musclesActivation['time'].size
musclesActivation['ext'] = musclesActivation['ext']*0. + 0.02
musclesActivation['flex'] = musclesActivation['ext']*0. + 0.02


footHeight= {'height':musclesActivation['flex'], 'time':musclesActivation['time'],'dt':musclesActivation['dt']}

ai = AfferentInput(dt,restingAngle,fiberLengthRange,fiberLengthGait,musclesActivation,footHeight)
IITA,IIGL =ai.computeIIFr("_human_cybex",normFactor,["GL","TA"])
IATA,IAGL =ai.computeIaFr("_human_cybex",normFactor,["GL","TA"])


motFile = "./generateForSimInputs/data/human/cybex/humanCybexAnkleControl.mot"
kinematic = ldt.readCsvGeneral(motFile,8,['time','ankle_angle_r'],['time','ankle_angle_r'])

""" Generate figures """

fig,ax = plt.subplots(4)

ax[0].plot(ai.get_fiber_length_locomotion()[0],color='b',label='ext')
ax[0].plot(ai.get_fiber_length_locomotion()[1],color='r',label='flex')
ax[0].plot([0,len(ai.get_fiber_length_locomotion()[0])],[ai.get_fiber_length_rest()[0],ai.get_fiber_length_rest()[0]],color='b')
ax[0].plot([0,len(ai.get_fiber_length_locomotion()[0])],[ai.get_fiber_length_rest()[1],ai.get_fiber_length_rest()[1]],color='r')
ax[0].set_ylabel('fiber length')
ax[0].legend()

ax[1].plot(ai.get_emg_locomotion()[0],color='b')
ax[1].plot(ai.get_emg_locomotion()[1],color='r')
ax[1].set_ylabel('emg')

ax[2].plot(IAGL,color='b')
ax[2].plot(IATA,color='r')
ax[2].set_ylabel('Ia fr')

ax[3].plot(IIGL,color='b')
ax[3].plot(IITA,color='r')
ax[3].set_ylabel('II fr')

fig,ax = plt.subplots(1,sharey=True)
fig.suptitle('kinematics')
ax.plot(kinematic['time'],kinematic['ankle_angle_r'])
ax.set_ylabel('ankle')

plt.show()
