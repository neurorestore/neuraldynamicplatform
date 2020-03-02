from mpi4py import MPI
import os

comm = MPI.COMM_WORLD
sizeComm = comm.Get_size()
rank = comm.Get_rank()

def modify_network_structure(templateFile,outFileName,delay,weights):
	""" Modify a templete network structure to create a second structure file.

	Keyword arguments:
	templateFile -- neural netwrok structure file that is used as template.
	outFileName -- name of the output structure file.
	delay -- delay of the afferent fibers
	weights -- list containign the delays to set.
	"""
	if rank==0:
		outFile = open("../nnStructures/"+outFileName,"w")
		section = None
		for line in open("../nnStructures/templates/"+templateFile,"r"):
			if line[0] == "@":section = float(line[1])
			elif section == 1 or section==2 or section==3: line, flag = _replace_val(line,"__delay",delay)
			elif section == 4 or section==5 or section==6:
				flag = False
				count = 0
				while not flag:
					if len(weights)<=count: break
					line, flag = _replace_val(line,"__weight_"+str(count+1),weights[count])
					count+=1

			outFile.write(line)
		outFile.close()

def _replace_val(line,find,replace):
	""" Find and replace a value in a string.

	Keyword arguments:
	line -- string.
	find -- value to find.
	replace -- new value.
	"""
	strList = line.strip("\n").split()
	flag = False
	for i,val in enumerate(strList):
		if val==find:
			flag = True
			strList[i] = str(replace)
	line = " ".join(strList)+"\n"
	return line, flag
