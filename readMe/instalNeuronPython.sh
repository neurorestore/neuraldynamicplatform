#!/bin/sh
#Install Neuron with InterViews and nrnpython interphase
export IDIR=/Applications/NEURON-7.4
mkdir $IDIR
mkdir $IDIR/nrn
mkdir $IDIR/iv

#create a directory in home directory
cd $HOME
mkdir ~/neuron_new
cd ~/neuron_new
# It might worth trying with the standard distribution from https://www.neuron.yale.edu/neuron/download/getstd if errors occurs
hg clone http://www.neuron.yale.edu/hg/neuron/nrn
hg clone http://www.neuron.yale.edu/hg/neuron/iv

cd iv
sh ./build.sh
./configure --prefix=$IDIR/iv
make
make install

cd ../nrn
sh ./build.sh
./configure --prefix=$IDIR/nrn --with-iv=$IDIR/iv --with-nrnpython=dynamic --with-paranrn=dynamic
make
# Here you may need to add this part in case you are on mac and you insatlled python through brew and pip
# For further infor check: http://stackoverflow.com/questions/24257803/distutilsoptionerror-must-supply-either-home-or-prefix-exec-prefix-not-both
# touch ~/.pydistutils.cfg
# echo "[install]" >> ~/.pydistutils.cfg
# echo "prefix=" >> ~/.pydistutils.cfg
make install
make after_install

cd src/nrnpython
python setup.py install
# if you added the previou section, you need to remove the created file as it might interfere with pip
# rm ~/.pydistutils.cfg
