import matplotlib.pyplot as plt
import time


class RealTimePlotter():
	""" Plot in real time. """

	def __init__(self, yLabels):

		self._fig, self._ax = plt.subplots(len(yLabels),1,figsize=(16,12))
		self._resultsFolder = "../../results/"

		for ax, yLabel in zip(self._ax,yLabels):
			ax.set_xlim([0, 3000])
			ax.set_ylim([0, 1])
			ax.set_ylabel(yLabel,fontsize=8)

		plt.ion()
		plt.show()

	def add_values(self,xVal,yVals):
		for ax, yVal in zip(self._ax, yVals):
			ax.scatter(xVal,yVal)
		plt.draw()

	def save_fig(self,nameSuffi=""):
		fileName = time.strftime("%Y_%m_%d_RealTimePlot"+nameSuffi+".pdf")
		plt.savefig(self._resultsFolder+fileName, format="pdf",transparent=True)
