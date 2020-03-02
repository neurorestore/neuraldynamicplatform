import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import scipy.optimize as so
import pickle

def main():
	"""
	Fit an exponential function 'A*exp(k*x)+c' to the curve representing the rat
	foot SAI firing rates over time during contiuous pression (10 s of 200 mN
	applied on 1.17 mm2). Data are coming from Leem 1993a - figure 8.
	In Leem 1993b, data shows that SAI response saturate over at 200 mN. Therefore,
	during locomotion, where a higher force is reached, these data should still be
	valid.
	"""
	rawData=np.loadtxt('./generateForSimInputs/data/rat/rat_SAI_leem_1993_fig8.csv',delimiter=',')
	time = rawData[:,0]-rawData[0,0]
	time *= 0.2
	firingRate = np.round(rawData[:,1])

	fig = plt.figure()
	ax1 = fig.add_subplot(1,1,1)

	# Initial guess
	A = 3
	K = -40
	# Non-linear Fit
	expPar = np.array([A, K])
	expPar = so.fmin(fit_exp_error,expPar,args=(time,firingRate),xtol=0.00001, ftol=0.00001)
	A, K = expPar
	print "y = 10*[{:.2f}*exp({:.2f}*x)]".format(A,K)
	with open("./generateForSimInputs/output/RA_modelParameters.p", 'w') as pickle_file:
		pickle.dump(A,pickle_file)
		pickle.dump(K,pickle_file)

	fit_firingRate = model_func(time, A, K)
	plt.plot(time, firingRate*10,'x')
	plt.plot(time, fit_firingRate*10)
	plt.show()

def model_func(x, A, K):
	return A * np.exp(K * x)

def fit_exp_error(expPar,x,y):
	A,K = expPar
	fit = model_func(x, A, K)
	errorTemp = np.abs(y-fit)
	error = np.sum(errorTemp)+errorTemp[0]*100

	return error


if __name__	== '__main__':
	main()
