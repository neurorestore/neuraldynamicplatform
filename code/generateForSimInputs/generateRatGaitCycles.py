import sys
sys.path.append('../code')
from tools import load_data_tools as ldt
from tools import emg_tools as et
from AfferentInput import AfferentInput
import matplotlib.pyplot as plt
import numpy as np
import pickle


""" get gait cycles """
kinFile = "./generateForSimInputs/data/rat/#208_100903_P0_BIP_TM9_4_KIN.csv"
footHeight = ldt.readGlabRecordedAnalogData(kinFile,['height'],["RTip_Z"])
footHeight['dt'] = 0.005
footHeight['time'] = np.arange(len(footHeight['height']))*footHeight['dt']


fig1,ax = plt.subplots(1,figsize=(12,6))
ax.plot(footHeight['time']-footHeight['time'][0],footHeight['height'])

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

gaitCyclesFileName = "./generateForSimInputs/output/ratGaitCycles.p"
with open(gaitCyclesFileName, 'w') as pickle_file:
    pickle.dump(heelStrikes, pickle_file)
    pickle.dump(footOffs, pickle_file)
