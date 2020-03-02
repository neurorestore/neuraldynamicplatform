import sys
sys.path.append('../code')
from tools import load_data_tools as ldt
from tools import emg_tools as et
from AfferentInput import AfferentInput
import matplotlib.pyplot as plt
import numpy as np

restingAngle = 0

dt = 0.005

lengthFile = "./generateForSimInputs/data/rat/GMTA_fiberLength_static.txt"
fiberLengthRange = ldt.readOpensimData(lengthFile,['angle','ext','flex'],['ankle_flx','MG','TA'])


cybex = "./generateForSimInputs/data/rat/cybex/cybexRat.txt"
fiberLengthGait = ldt.readOpensimData(cybex,['time','ext','flex'],["Coordinates(Deg.)",'MG','TA'])
fiberLengthGait['dt'] = (fiberLengthGait['time'][-1]-fiberLengthGait['time'].min())/fiberLengthGait['time'].size


musclesActivation = ldt.readOpensimData(cybex,['time','ext','flex'],["Coordinates(Deg.)",'MG','TA'])
musclesActivation['dt'] = (musclesActivation['time'][-1]-musclesActivation['time'].min())/musclesActivation['time'].size
musclesActivation['ext'] = musclesActivation['ext']*0. + 0.02
musclesActivation['flex'] = musclesActivation['ext']*0. + 0.02


footHeight= {'height':musclesActivation['flex'], 'time':musclesActivation['time'],'dt':musclesActivation['dt']}

ai = AfferentInput(dt,restingAngle,fiberLengthRange,fiberLengthGait,musclesActivation,footHeight)
IITA,IIMG =ai.computeIIFr("_rat_cybex")
IATA,IAMG =ai.computeIaFr("_rat_cybex")


motFile = "./generateForSimInputs/data/rat/cybex/ratCybexAnkleControl.mot"
kinematic = ldt.readCsvGeneral(motFile,8,['time','ankle_flx'],['time','ankle_flx'])

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

ax[2].plot(IAMG,color='b')
ax[2].plot(IATA,color='r')
ax[2].set_ylabel('Ia fr')

ax[3].plot(IIMG,color='b')
ax[3].plot(IITA,color='r')
ax[3].set_ylabel('II fr')

fig,ax = plt.subplots(1,sharey=True)
fig.suptitle('kinematics')
ax.plot(kinematic['time'],kinematic['ankle_flx'])
ax.set_ylabel('ankle')

plt.show()
