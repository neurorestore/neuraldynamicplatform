from mpi4py import MPI
comm = MPI.COMM_WORLD
sizeComm = comm.Get_size()
rank = comm.Get_rank()

class HumanParameters():

    __dataset = "humod" # "float" vs "humod"
    __muscles = {"ext":"SOL","flex":"TA"} # SOL or GL


    @classmethod
    def get_dataset(cls):
        return HumanParameters.__dataset

    @classmethod
    def get_tot_sim_time(cls):
        if HumanParameters.__dataset == "float":
            return 10000
        elif HumanParameters.__dataset == "humod":
            return 9995
        else:
            raise(Exception("No dataset selected"))

    @classmethod
    def get_gait_cycles_file(cls):
        if HumanParameters.__dataset == "float":
            return "./generateForSimInputs/output/humanGaitCyclesFloat.p"
        elif HumanParameters.__dataset == "humod":
            return "./generateForSimInputs/output/humanGaitCyclesB13.p"
        else:
            raise(Exception("No dataset selected"))

    @classmethod
    def get_muscles(cls):
        return HumanParameters.__muscles.values()

    @classmethod
    def get_muscles_dict(cls):
        return HumanParameters.__muscles

    @classmethod
    def get_nn_template_file(cls):
        if "SOL" in HumanParameters.__muscles.values():
            return "templateFrwSimHumanSOL.txt"
        elif "GL" in HumanParameters.__muscles.values():
            return "templateFrwSimHuman.txt"

    @classmethod
    def get_network_weights(cls):
        w1 = 0.0210
        w2 = 0.0364
        w3 = 0.0165
        w4 = 0.0219
        return w1,w2,w3,w4

    @classmethod
    def get_ext_Ia_afferents_locomotion_files(cls):
        if HumanParameters.__dataset == "humod":
            if rank==0: print "using HuMoD afferent firings"
            if "GL" in HumanParameters.__muscles.values():
                return "../afferentsFirings/meanFr_Ia_GL_humanBl.txt"
            elif "SOL" in HumanParameters.__muscles.values():
                return "../afferentsFirings/meanFr_Ia_SOL_humanBl.txt"
            else:
                raise(Exception("Wrong selected muscle"))

        elif HumanParameters.__dataset == "float":
            print "using float afferent firings"
            if "SOL" in HumanParameters.__muscles.values():
                return "../afferentsFirings/meanFr_Ia_SOL_humanfloatPaperJBl.txt"
            else:
                raise(Exception("Wrong selected muscle"))
        else:
            raise(Exception("No dataset selected"))

    @classmethod
    def get_flex_Ia_afferents_locomotion_files(cls):
        if HumanParameters.__dataset == "humod":
            if "TA" in HumanParameters.__muscles.values():
                return "../afferentsFirings/meanFr_Ia_TA_humanBl.txt"
            else:
                raise(Exception("Wrong selected muscle"))
        elif HumanParameters.__dataset == "float":
            if "TA" in HumanParameters.__muscles.values():
                return "../afferentsFirings/meanFr_Ia_TA_humanfloatPaperJBl.txt"
            else:
                raise(Exception("Wrong selected muscle"))
        else:
            raise(Exception("No dataset selected"))

    @classmethod
    def get_ext_II_afferents_locomotion_files(cls):
        if HumanParameters.__dataset == "humod":
            if "GL" in HumanParameters.__muscles.values():
                return "../afferentsFirings/meanFr_II_GL_humanBl.txt"
            elif "SOL" in HumanParameters.__muscles.values():
                return "../afferentsFirings/meanFr_II_SOL_humanBl.txt"
            else:
                raise(Exception("Wrong selected muscle"))

        elif HumanParameters.__dataset == "float":
            if "SOL" in HumanParameters.__muscles.values():
                return "../afferentsFirings/meanFr_II_SOL_humanfloatPaperJBl.txt"
            else:
                raise(Exception("Wrong selected muscle"))
        else:
            raise(Exception("No dataset selected"))

    @classmethod
    def get_flex_II_afferents_locomotion_files(cls):
        if HumanParameters.__dataset == "humod":
            if "TA" in HumanParameters.__muscles.values():
                return "../afferentsFirings/meanFr_II_TA_humanBl.txt"
            else:
                raise(Exception("Wrong selected muscle"))
        elif HumanParameters.__dataset == "float":
            if "TA" in HumanParameters.__muscles.values():
                return "../afferentsFirings/meanFr_II_TA_humanfloatPaperJBl.txt"
            else:
                raise(Exception("Wrong selected muscle"))
        else:
            raise(Exception("No dataset selected"))
