import sys
sys.path.append('../code')
from tools import load_data_tools as ldt
from tools import emg_tools as et
from AfferentInput import AfferentInput
import matplotlib.pyplot as plt
import numpy as np
import pickle


""" get gait cycles """
kinFile = "./generateForSimInputs/data/human/HuMoD-database/generatedFiles/Subject_B_speed_1.3_31-Oct-2017_KIN.csv"
# kinFile = "./generateForSimInputs/data/human/floatData/generatedFiles/H_JBM_20150109_04TM_NF_01_30-Apr-2018_KIN.csv"
footHeight = ldt.readCsvGeneral(kinFile,1,['time','height_toe','height_cal'],['time','leftToe','leftCalf'])
footHeight['dt'] = (footHeight['time'][-1]-footHeight['time'].min())/footHeight['time'].size


fig1,ax = plt.subplots(1,figsize=(12,6))
ax.plot(footHeight['time']-footHeight['time'][0],footHeight['height_toe'],'b')
ax.plot(footHeight['time']-footHeight['time'][0],footHeight['height_cal'],'r')

fig1.suptitle("Please select all heel strikes")
plt.draw()
plt.pause(1)
temp = fig1.ginput(n=0,timeout=240)
if len(temp)==0: raise(Exception("no heel strikes detected..."))
else: heelStrikes = np.atleast_1d([ float(x) for x,_ in temp])
print heelStrikes

fig1.suptitle("Please select all foot offs")
plt.draw()
plt.pause(1)
temp = fig1.ginput(n=0,timeout=240)
if len(temp)==0: raise(Exception("no foot offs detected..."))
else: footOffs = np.atleast_1d([ float(x) for x,_ in temp])
print footOffs

plt.draw()

gaitCyclesFileName = "./generateForSimInputs/output/humanGaitCyclesB13.p"
# gaitCyclesFileName = "./generateForSimInputs/output/humanGaitCyclesFloat.p"
with open(gaitCyclesFileName, 'w') as pickle_file:
    pickle.dump(heelStrikes, pickle_file)
    pickle.dump(footOffs, pickle_file)
