import sys
sys.path.append('../code')
from WebotsControl import WebotsControl

def main():
	""" This program executes a neural-biomechanical closed loop simulation.
	The program launches the neural netwrok (python) and the biomechanical
	model (cpp) and manages the communication between these two programs.
	The program doesn't have to be executed by MPI.
	"""
	if len(sys.argv)<2:
		print "Error in arguments. Required arguments:"
		print "\t experiment [bed, treadmill, bodyweight] "
		sys.exit(-1)

	experiment = sys.argv[1]

	clm = WebotsControl(experiment)
	clm.run()

if __name__ == '__main__':
	main()
