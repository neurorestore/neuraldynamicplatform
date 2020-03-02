import sys
sys.path.append('../code')
from tools import seed_handler as sh
import time as timeModule
sh.save_seed(timeModule.time())
from ClosedLoopManager import ClosedLoopManager
from tools import structures_tools as tls
#TODO - within the HBP this part has compleatly chanched - there is another repo for the closedloop simulations

def main():
	""" This program executes a neural-biomechanical closed loop simulation.
	The program launches the neural netwrok (python) and the biomechanical
	model (cpp) and manages the communication between these two programs.
	The program doesn't have to be executed by MPI.
	"""
	if len(sys.argv)<4:
		print "Error in arguments. Required arguments:"
		print "\t ees frequency [0-1000] "
		print "\t ees amplitude (0-600] or %Ia_II_Mn "
		print "\t experiment [bed, treadmill, bodyweight] "
		print "Optional arguments:"
		print "Species (mouse, rat or human)"
		print "\t tot time of simulation (default = 3000)"
		print "\t perturbation parameters %muscleName/cellsName/percStimFiber/frequency/pulsesNumber/startTime or False (default = False)"
		sys.exit(-1)

	nnNp = "4"
	eesFreq = sys.argv[1]
	eesAmp = sys.argv[2]
	experiment = sys.argv[3]
	if len(sys.argv)>=5: species = sys.argv[4]
	else: species = "human"
	if len(sys.argv)>=6 : totTime = sys.argv[5]
	else: totTime = "3000"
	if len(sys.argv)>=7: perturbationParams = sys.argv[6]
	else: perturbationParams = "False"


	w1 = 0.0112
	w2 = -0.0076
	templateFile = "templateClosedLoopSimple.txt"
	nnStructFile = "generatedStructures/ClosedLoop_w1_"+str(w1)+"_w2_"+str(w2)+".txt"
	tls.modify_network_structure(templateFile,nnStructFile,None,[w1,w2])

	clm = ClosedLoopManager(nnNp, eesFreq, eesAmp, nnStructFile, experiment, species, totTime, perturbationParams)
	clm.run()

if __name__ == '__main__':
	main()
