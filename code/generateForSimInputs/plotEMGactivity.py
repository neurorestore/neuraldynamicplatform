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

speed = "1.3" # 1.3 = 2m/s - 1.1 = 1m/s
subject = "B"

dt = 0.005
SIDE = "R"

flexMuscleHumod = "TA"
extMuscleHumod = "SOL"

if subject == "B":
	if speed == "1.1": emgFile = "./generateForSimInputs/data/human/HuMoD-database/generatedFiles/Subject_B_speed_1.1_13-Apr-2017_EMG.csv"
	elif speed == "1.3": emgFile = "./generateForSimInputs/data/human/HuMoD-database/generatedFiles/Subject_B_speed_1.3_10-Jul-2017_EMG.csv"
	musclesActivation = ldt.readCsvGeneral(emgFile,1,['time','ext','flex'],['time',extMuscleHumod+"_"+SIDE,flexMuscleHumod+"_"+SIDE])
	musclesActivation['dt'] = (musclesActivation['time'][-1]-musclesActivation['time'].min())/musclesActivation['time'].size

	if speed == "1.1": kinFile = "./generateForSimInputs/data/human/HuMoD-database/generatedFiles/Subject_B_speed_1.1_13-Apr-2017_KIN.csv"
	elif speed == "1.3": kinFile = "./generateForSimInputs/data/human/HuMoD-database/generatedFiles/Subject_B_speed_1.3_10-Jul-2017_KIN.csv"
	footHeight = ldt.readCsvGeneral(kinFile,1,['time','height'],['time','leftToe'])
	footHeight['dt'] = (footHeight['time'][-1]-footHeight['time'].min())/footHeight['time'].size

elif subject == "A":
	if speed == "1.3": emgFile = "./generateForSimInputs/data/human/HuMoD-database/generatedFiles/Subject_A_speed_1.3_31-Oct-2017_EMG.csv"
	musclesActivation = ldt.readCsvGeneral(emgFile,1,['time','ext','flex'],['time',extMuscleHumod+"_"+SIDE,flexMuscleHumod+"_"+SIDE])
	musclesActivation['dt'] = (musclesActivation['time'][-1]-musclesActivation['time'].min())/musclesActivation['time'].size

	if speed == "1.3": kinFile = "./generateForSimInputs/data/human/HuMoD-database/generatedFiles/Subject_A_speed_1.3_31-Oct-2017_KIN.csv"
	footHeight = ldt.readCsvGeneral(kinFile,1,['time','height'],['time','rightToe'])
	footHeight['dt'] = (footHeight['time'][-1]-footHeight['time'].min())/footHeight['time'].size


""" Generate figures """
redAi = "#e9342f"
bluAi = "#00aaeb"

fig,ax = plt.subplots(1,figsize=(18,4))
ax.plot(musclesActivation["time"],musclesActivation["ext"],redAi)
ax.plot(musclesActivation["time"],musclesActivation["flex"],bluAi)
plt.show()
