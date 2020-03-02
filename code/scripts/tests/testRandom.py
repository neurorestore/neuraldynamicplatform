from mpi4py import MPI
import random as rnd
from tools import seed_handler as sh
sh.save_seed(1)
sh.set_seed()

comm = MPI.COMM_WORLD
sizeComm = comm.Get_size()
rank = comm.Get_rank()



class testRandom():
    def __init__(self,n):
        self.ranks = range(sizeComm)
        self.n = n

    def printRandom(self):
        print self.n,rank,rnd.random()


def main ():
    tr = testRandom(1)
    tr.printRandom()
    comm.Barrier()
    print "\n"
    comm.Barrier()
    tr2 = testRandom(2)
    tr2.printRandom()

if __name__ == '__main__':
    main()
