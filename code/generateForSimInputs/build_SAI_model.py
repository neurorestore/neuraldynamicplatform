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
	firingRate = np.round(rawData[:,1])
	C = np.mean(firingRate[40:])

	fig = plt.figure()
	ax1 = fig.add_subplot(1,1,1)

	# Initial guess
	A = 1
	K = -4
	# Non-linear Fit
	expPar = np.array([A, K])
	expPar = so.fmin(fit_exp_error,expPar,args=(time,firingRate,C),xtol=0.00001, ftol=0.00001)
	A, K = expPar
	print "y = 10*[{:.2f}*exp({:.2f}*x)+{:.2f}]".format(A,K,C)
	with open("./generateForSimInputs/output/SAI_modelParameters.p", 'w') as pickle_file:
		pickle.dump(A,pickle_file)
		pickle.dump(K,pickle_file)
		pickle.dump(C,pickle_file)

	fit_firingRate = model_func(time, A, K, C)
	plt.plot(time, firingRate*10,'x')
	plt.plot(time, fit_firingRate*10)
	plt.show()

def model_func(x, A, K, C):
	return A * np.exp(K * x) + C

def fit_exp_error(expPar,x,y,C):
	A,K = expPar
	fit = model_func(x, A, K, C)
	error = np.sum(np.abs(y-fit))
	return error


if __name__	== '__main__':
	main()
