The following steps explain how to use and run the code developed during the semester project.

1) The code developed during the semester project of this course uses the Neuron module.
Therefore, to use the developed software it is first necessary to install Neuron with python (http://www.neuron.yale.edu/neuron/download). See also the installNeruonPython.sh in the current folder for a possible solution.

2) The program I developed is ment to be used with MPI. For this purpose it is also suggested to install openmpi and mpi4py.

3) The folder python_files/mod_files contains different mechanisms that describe the membrane dynamics or particular cell properties necessary for certain Neuron cell models. To test the developed code these files have to be compiled. To do so use go in the ../python_files folder and issue the following command: nrnivmodl ./mod_files.

4) Different types of simulations can be executed by running the files in the ../python_files/scripts folder.
To see how to run a specific file inside this folder refer to the docstrings comments inside the relative file. 


------------------------------------------------------------------------------------------------------------------

The results of the simulations are saved in the ../results folder where there are already some results of the simulations I performed. 

The folders afferentsFirings, nnStructures and recruitmentData contains files containg data necessary for the code.