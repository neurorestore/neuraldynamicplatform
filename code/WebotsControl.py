import subprocess
import socket
from tools import structures_tools as tls

class WebotsControl():
	""" Run a webots simulation.

	Run the musculoskeletal model with defined muscle control values.
	"""

	def __init__(self,experiment):
		# Define experiment type (bed vs treadmill vs bodyweight)
		self._experiment = experiment
		self._init_muscle_controls()

	def _init_muscle_controls(self,activation=0):
		""" Initialize webots muscles names. """
		self._nnData = ""
		self._nnData +=" ".join(["RIGHT_SOL",str(activation)]) + "\n"
		self._nnData +=" ".join(["RIGHT_TA",str(activation)]) + "\n"
		self._nnData +=" ".join(["RIGHT_VAS",str(activation)]) + "\n"
		self._nnData +=" ".join(["RIGHT_HAM",str(activation)]) + "\n"
		self._nnData +=" ".join(["RIGHT_GLU",str(activation)]) + "\n"
		self._nnData +=" ".join(["RIGHT_HF",str(activation)]) + "\n"
		self._nnData +=" ".join(["LEFT_SOL",str(activation)]) + "\n"
		self._nnData +=" ".join(["LEFT_TA",str(activation)]) + "\n"
		self._nnData +=" ".join(["LEFT_VAS",str(activation)]) + "\n"
		self._nnData +=" ".join(["LEFT_HAM",str(activation)]) + "\n"
		self._nnData +=" ".join(["LEFT_GLU",str(activation)]) + "\n"
		self._nnData +=" ".join(["LEFT_HF",str(activation)]) + "\n"

	def _run_webots(self):
		""" Run webots as a subprocess """
		if self._experiment == "bed":
			program = ["webots","--stdout","../../sml/controller_current/webots/worlds/743_formento_bed.wbt"]
		elif self._experiment == "treadmill":
			program = ["webots","--stdout","../../sml/controller_current/webots/worlds/743_formento_tbws.wbt"]
		elif self._experiment == "bodyweight":
			program = ["webots","--stdout","../../sml/controller_current/webots/worlds/743_formento_bw.wbt"]
		elif self._experiment == "testMuscLength":
			program = ["webots","--stdout","../../sml/controller_current/webots/worlds/743_formento_testMuscRestingLength.wbt"]
		else: raise(Exception("Unknown experiment!"))

		self._webots = subprocess.Popen(program, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

		# Initialize TCP communication (server side)
		TCP_IP = '127.0.0.1'
		TCP_PORT = 5005
		BUFFER_SIZE = 512
		self._s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self._s.bind((TCP_IP, TCP_PORT))
		self._s.listen(1)
		self._conn, addr = self._s.accept()

	def run(self):
		""" Run the closed loop simualtion. """
		self._run_webots()

		# We first wait for webots inputs
		webotsTurn = True
		neuralNetworkTurn = False
		while True:
			if webotsTurn:
				print "reading data from webots:"
				wbtData = self._wbt_read_data()
				webotsTurn = False
				neuralNetworkTurn = True

			elif neuralNetworkTurn:
				print "sending data to webots..."
				self._send_data_to_wbt(self._nnData)
				neuralNetworkTurn = False
				webotsTurn = True

	def _wbt_read_data(self):
		""" Read the data coming from the webots controller. """
		reaData = True
		wbtIncomingData = False
		wbtData = ""
		while reaData:
			wbtIncomingMsg =  self._webots.stdout.readline().rstrip("\n").split()
			if "COMM_OUT" in wbtIncomingMsg: wbtIncomingData = True
			elif "END" in wbtIncomingMsg: reaData = False
			elif wbtIncomingData: wbtData += " ".join(wbtIncomingMsg[1:])+"\n"
			print "\t\t\t\tWebots: :"+" ".join(wbtIncomingMsg[1:])
		return wbtData

	def _send_data_to_wbt(self,nnData):
		""" Send the neural network's data to the webots controller. """
		nnData += "END\n"
		self._conn.send(nnData)
