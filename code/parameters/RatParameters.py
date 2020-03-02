import numpy as np
class RatParameters():

    @classmethod
    def get_tot_sim_time(cls):
        return 12385

    @classmethod
    def get_gait_cycles_file(cls):
        return "./generateForSimInputs/output/ratGaitCycles.p"

    @classmethod
    def get_muscles(cls):
        return ["TA","GM"]

    @classmethod
    def get_muscles_dict(cls):
        return {"ext":"GM","flex":"TA"}

    @classmethod
    def get_nn_template_file(cls):
        return "templateFrwSim.txt"

    @classmethod
    def get_network_weights(cls):
        w1 = 0.011
        w2 = -0.0076
        return w1,w2

    @classmethod
    def get_interneurons_baseline_fr(cls):
        fr = {
            "IaInt":list(np.random.poisson(50, size=100000)),
            "IIExInt":list(np.random.poisson(50, size=100000)),
            "RORa":list(np.random.poisson(50, size=100000)),
            "RORaInt":list(np.random.poisson(50, size=100000)),
            "Iaf":list(np.random.poisson(0, size=100000)),
            "IIf":list(np.random.poisson(0, size=100000)),
            "II_RAf_foot":list(np.random.poisson(0, size=100000)),
            "II_SAIf_foot":list(np.random.poisson(0, size=100000)),
            "II_RAf":list(np.random.poisson(0, size=100000)),
            "II_SAIf":list(np.random.poisson(0, size=100000))
        }
        return fr
